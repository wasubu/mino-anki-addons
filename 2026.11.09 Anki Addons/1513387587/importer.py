"""
Note Type Importer - Imports note types from JSON files into Anki.
"""

import json
from typing import Optional

from aqt import mw
from aqt.utils import getFile, showInfo, showWarning, tooltip

from .config import ConfigKey, ConfigService, ConflictAction


def load_note_types_from_file(file_path: str) -> Optional[dict]:
    """
    Load note types data from a JSON file.
    
    Args:
        file_path: Path to the JSON file
    
    Returns:
        Parsed JSON data or None if loading failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate basic structure
        if "note_types" not in data:
            showWarning("Invalid file format: missing 'note_types' field.")
            return None
        
        if not isinstance(data["note_types"], list):
            showWarning("Invalid file format: 'note_types' must be a list.")
            return None
        
        return data
    
    except json.JSONDecodeError as e:
        showWarning(f"Invalid JSON file: {e}")
        return None
    except Exception as e:
        showWarning(f"Error reading file: {e}")
        return None


def check_name_conflicts(note_types_data: list[dict]) -> list[tuple[str, int]]:
    """
    Check which note type names already exist in the collection.
    
    Args:
        note_types_data: List of note type dicts from import file
    
    Returns:
        List of (name, existing_model_id) tuples for conflicting names
    """
    conflicts = []
    
    for nt_data in note_types_data:
        name = nt_data.get("name", "")
        if name:
            existing = mw.col.models.by_name(name)
            if existing:
                conflicts.append((name, existing["id"]))
    
    return conflicts


def _create_note_type_from_data(nt_data: dict, name_override: Optional[str] = None) -> dict:
    """
    Create a new note type dict from imported data.
    
    Args:
        nt_data: Note type data from import file
        name_override: Optional name to use instead of the one in data
    
    Returns:
        New note type dict ready to be added to the collection
    """
    name = name_override or nt_data.get("name", "Imported Note Type")
    
    # Create base note type
    new_model = mw.col.models.new(name)
    
    # Set type (0 = standard, 1 = cloze)
    new_model["type"] = nt_data.get("type", 0)
    
    # Set CSS
    new_model["css"] = nt_data.get("css", "")
    
    # Set LaTeX settings
    if "latex_pre" in nt_data:
        new_model["latexPre"] = nt_data["latex_pre"]
    if "latex_post" in nt_data:
        new_model["latexPost"] = nt_data["latex_post"]
    if "latex_svg" in nt_data:
        new_model["latexsvg"] = nt_data["latex_svg"]
    
    # Clear default fields and add imported ones
    new_model["flds"] = []
    for fld_data in nt_data.get("fields", []):
        field = mw.col.models.new_field(fld_data.get("name", "Field"))
        field["ord"] = fld_data.get("ord", len(new_model["flds"]))
        field["font"] = fld_data.get("font", "Arial")
        field["size"] = fld_data.get("size", 20)
        field["sticky"] = fld_data.get("sticky", False)
        field["rtl"] = fld_data.get("rtl", False)
        field["description"] = fld_data.get("description", "")
        field["plainText"] = fld_data.get("plainText", False)
        field["collapsed"] = fld_data.get("collapsed", False)
        field["excludeFromSearch"] = fld_data.get("excludeFromSearch", False)
        mw.col.models.add_field(new_model, field)
    
    # Clear default templates and add imported ones
    new_model["tmpls"] = []
    for tmpl_data in nt_data.get("templates", []):
        template = mw.col.models.new_template(tmpl_data.get("name", "Card"))
        template["ord"] = tmpl_data.get("ord", len(new_model["tmpls"]))
        template["qfmt"] = tmpl_data.get("qfmt", "")
        template["afmt"] = tmpl_data.get("afmt", "")
        template["bqfmt"] = tmpl_data.get("bqfmt", "")
        template["bafmt"] = tmpl_data.get("bafmt", "")
        mw.col.models.add_template(new_model, template)
    
    # Set sort field index
    sort_idx = nt_data.get("sort_field_index", 0)
    if sort_idx < len(new_model["flds"]):
        new_model["sortf"] = sort_idx
    
    return new_model


def _generate_unique_name(base_name: str, suffix: str = "(imported)") -> str:
    """Generate a unique name by adding a suffix, incrementing if needed."""
    new_name = f"{base_name} {suffix}"
    counter = 1
    
    while mw.col.models.by_name(new_name):
        counter += 1
        new_name = f"{base_name} {suffix} {counter}"
    
    return new_name


def import_single_note_type(
    nt_data: dict,
    conflict_action: str = ConflictAction.ASK,
    parent=None
) -> tuple[bool, str]:
    """
    Import a single note type.
    
    Args:
        nt_data: Note type data from import file
        conflict_action: How to handle name conflicts
        parent: Parent widget for dialogs
    
    Returns:
        Tuple of (success, message)
    """
    name = nt_data.get("name", "Imported Note Type")
    existing = mw.col.models.by_name(name)
    
    final_name = name
    
    if existing:
        if conflict_action == ConflictAction.SKIP:
            return (False, f"Skipped '{name}' (already exists)")
        
        elif conflict_action == ConflictAction.RENAME:
            final_name = _generate_unique_name(name)
        
        elif conflict_action == ConflictAction.OVERWRITE:
            # Remove existing note type (only if no notes use it)
            if mw.col.models.use_count(existing):
                return (False, f"Cannot overwrite '{name}' - notes are using it")
            mw.col.models.remove(existing["id"])
        
        elif conflict_action == ConflictAction.ASK:
            # This should be handled by the caller using dialogs
            from .dialogs import ConflictResolutionDialog
            dialog = ConflictResolutionDialog(name, parent or mw)
            result = dialog.exec()
            
            if result == ConflictResolutionDialog.SKIP:
                return (False, f"Skipped '{name}'")
            elif result == ConflictResolutionDialog.RENAME:
                final_name = _generate_unique_name(name)
            elif result == ConflictResolutionDialog.OVERWRITE:
                if mw.col.models.use_count(existing):
                    return (False, f"Cannot overwrite '{name}' - notes are using it")
                mw.col.models.remove(existing["id"])
            else:
                return (False, f"Cancelled import of '{name}'")
    
    try:
        new_model = _create_note_type_from_data(nt_data, final_name)
        mw.col.models.add(new_model)
        return (True, f"Imported '{final_name}'")
    except Exception as e:
        return (False, f"Error importing '{name}': {e}")


def import_note_types(
    note_types_data: list[dict],
    default_conflict_action: str = ConflictAction.ASK,
    parent=None
) -> tuple[int, int, list[str]]:
    """
    Import multiple note types.
    
    Args:
        note_types_data: List of note type dicts from import file
        default_conflict_action: Default action for conflicts
        parent: Parent widget for dialogs
    
    Returns:
        Tuple of (success_count, failure_count, messages)
    """
    success_count = 0
    failure_count = 0
    messages = []
    
    # Track if user chose "apply to all" in conflict dialog
    apply_to_all_action = None
    
    for nt_data in note_types_data:
        name = nt_data.get("name", "Imported Note Type")
        existing = mw.col.models.by_name(name)
        
        # Determine action for this note type
        if existing and default_conflict_action == ConflictAction.ASK:
            if apply_to_all_action:
                action = apply_to_all_action
            else:
                from .dialogs import ConflictResolutionDialog
                dialog = ConflictResolutionDialog(name, parent or mw, show_apply_to_all=True)
                result, apply_to_all = dialog.exec_with_apply_to_all()
                
                if result == ConflictResolutionDialog.CANCELLED:
                    messages.append(f"Import cancelled at '{name}'")
                    break
                
                action = {
                    ConflictResolutionDialog.SKIP: ConflictAction.SKIP,
                    ConflictResolutionDialog.RENAME: ConflictAction.RENAME,
                    ConflictResolutionDialog.OVERWRITE: ConflictAction.OVERWRITE,
                }.get(result, ConflictAction.SKIP)
                
                if apply_to_all:
                    apply_to_all_action = action
        else:
            action = default_conflict_action
        
        success, msg = import_single_note_type(nt_data, action, parent)
        messages.append(msg)
        
        if success:
            success_count += 1
        else:
            failure_count += 1
    
    return (success_count, failure_count, messages)


def import_note_types_from_file(parent=None) -> None:
    """
    Open file dialog and import note types from selected JSON file.
    
    Args:
        parent: Parent widget for dialogs
    """
    # Get last used directory
    last_dir = ConfigService.read(ConfigKey.LAST_IMPORT_DIR, str) or ""
    
    # Open file dialog
    file_path = getFile(
        parent=parent or mw,
        title="Import Note Types",
        cb=None,
        filter="JSON files (*.json);;All files (*.*)",
        key="note_type_import"
    )
    
    if not file_path:
        return
    
    # Save directory for next time
    import os
    ConfigService.write(ConfigKey.LAST_IMPORT_DIR, os.path.dirname(file_path))
    
    # Load file
    data = load_note_types_from_file(file_path)
    if not data:
        return
    
    note_types = data.get("note_types", [])
    if not note_types:
        showInfo("No note types found in file.")
        return
    
    # Show import preview dialog
    from .dialogs import ImportPreviewDialog
    dialog = ImportPreviewDialog(data, parent or mw)
    if not dialog.exec():
        return
    
    selected_indices = dialog.get_selected_indices()
    if not selected_indices:
        showInfo("No note types selected for import.")
        return
    
    selected_note_types = [note_types[i] for i in selected_indices]
    default_action = ConfigService.read(ConfigKey.DEFAULT_CONFLICT_ACTION, str)
    
    # Perform import
    success, failure, messages = import_note_types(
        selected_note_types,
        default_action,
        parent or mw
    )
    
    # Show result
    if failure == 0:
        tooltip(f"Successfully imported {success} note type(s)")
    else:
        result_msg = f"Imported: {success}\nFailed: {failure}\n\nDetails:\n"
        result_msg += "\n".join(messages[-10:])  # Show last 10 messages
        if len(messages) > 10:
            result_msg += f"\n... and {len(messages) - 10} more"
        showInfo(result_msg)
