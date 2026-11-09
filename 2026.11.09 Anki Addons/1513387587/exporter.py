"""
Note Type Exporter - Exports Anki note types to JSON format.
"""

import json
from datetime import datetime
from typing import Any

from aqt import mw

# Export format version
FORMAT_VERSION = "1.0"


def get_all_note_types() -> list[dict]:
    """Get all note types from the collection."""
    if not mw.col:
        return []
    return mw.col.models.all()


def get_note_type_names_and_ids() -> list[tuple[int, str]]:
    """Get list of (id, name) tuples for all note types."""
    if not mw.col:
        return []
    return [(m.id, m.name) for m in mw.col.models.all_names_and_ids()]


def _clean_field_for_export(field: dict) -> dict:
    """Extract only the fields we want to export from a field dict."""
    return {
        "name": field.get("name", ""),
        "ord": field.get("ord", 0),
        "font": field.get("font", "Arial"),
        "size": field.get("size", 20),
        "sticky": field.get("sticky", False),
        "rtl": field.get("rtl", False),
        "description": field.get("description", ""),
        "plainText": field.get("plainText", False),
        "collapsed": field.get("collapsed", False),
        "excludeFromSearch": field.get("excludeFromSearch", False),
    }


def _clean_template_for_export(template: dict) -> dict:
    """Extract only the fields we want to export from a template dict."""
    return {
        "name": template.get("name", ""),
        "ord": template.get("ord", 0),
        "qfmt": template.get("qfmt", ""),
        "afmt": template.get("afmt", ""),
        "bqfmt": template.get("bqfmt", ""),
        "bafmt": template.get("bafmt", ""),
    }


def _clean_note_type_for_export(model: dict) -> dict:
    """
    Clean a note type dict for export.
    Removes runtime-only fields like id, mod, usn that shouldn't be exported.
    """
    return {
        "name": model.get("name", ""),
        "type": model.get("type", 0),  # 0 = standard, 1 = cloze
        "css": model.get("css", ""),
        "latex_pre": model.get("latexPre", ""),
        "latex_post": model.get("latexPost", ""),
        "latex_svg": model.get("latexsvg", False),
        "sort_field_index": model.get("sortf", 0),
        "fields": [_clean_field_for_export(f) for f in model.get("flds", [])],
        "templates": [_clean_template_for_export(t) for t in model.get("tmpls", [])],
    }


def export_note_types(
    model_ids: list[int],
    include_metadata: bool = True
) -> dict[str, Any]:
    """
    Export selected note types to a dictionary ready for JSON serialization.
    
    Args:
        model_ids: List of note type IDs to export
        include_metadata: Whether to include export metadata
    
    Returns:
        Dictionary with export data
    """
    note_types = []
    
    for mid in model_ids:
        model = mw.col.models.get(mid)
        if model:
            note_types.append(_clean_note_type_for_export(model))
    
    export_data = {
        "format_version": FORMAT_VERSION,
        "note_types": note_types,
    }
    
    if include_metadata:
        export_data["metadata"] = {
            "exported_at": datetime.utcnow().isoformat() + "Z",
            "anki_version": _get_anki_version(),
            "addon_version": _get_addon_version(),
            "count": len(note_types),
        }
    
    return export_data


def export_note_types_to_file(
    model_ids: list[int],
    file_path: str,
    include_metadata: bool = True
) -> bool:
    """
    Export selected note types to a JSON file.
    
    Args:
        model_ids: List of note type IDs to export
        file_path: Path to the output file
        include_metadata: Whether to include export metadata
    
    Returns:
        True if export succeeded, False otherwise
    """
    try:
        export_data = export_note_types(model_ids, include_metadata)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"[Note Type Export] Error exporting: {e}")
        return False


def _get_anki_version() -> str:
    """Get the current Anki version."""
    try:
        from anki.buildinfo import version
        return version
    except ImportError:
        return "unknown"


def _get_addon_version() -> str:
    """Get this add-on's version."""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "unknown"
