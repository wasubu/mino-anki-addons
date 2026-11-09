"""
Dialog windows for Note Type Export add-on.
"""

import os
from typing import Optional

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QGroupBox,
    QDialogButtonBox, QMessageBox, Qt, QAbstractItemView
)
from aqt.utils import getSaveFile, tooltip

from .config import ConfigKey, ConfigService, ConflictAction
from .exporter import get_note_type_names_and_ids, export_note_types_to_file


class ExportDialog(QDialog):
    """Dialog for selecting note types to export."""
    
    def __init__(self, parent=None):
        super().__init__(parent or mw)
        self.setWindowTitle("Export Note Types")
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)
        self._setup_ui()
        self._load_note_types()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Select the note types you want to export.\n"
            "The exported file can be imported into any Anki installation."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Note type list
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        layout.addWidget(self.list_widget)
        
        # Select all / deselect all buttons
        select_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all)
        select_layout.addWidget(select_all_btn)
        select_layout.addWidget(deselect_all_btn)
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.include_metadata_cb = QCheckBox("Include export metadata (date, version)")
        self.include_metadata_cb.setChecked(
            ConfigService.read(ConfigKey.EXPORT_INCLUDE_METADATA, bool)
        )
        options_layout.addWidget(self.include_metadata_cb)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_export)
        button_box.rejected.connect(self.reject)
        
        # Rename OK button
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Export...")
        
        layout.addWidget(button_box)
    
    def _load_note_types(self):
        """Load note types into the list."""
        self.note_types = get_note_type_names_and_ids()
        
        for model_id, name in self.note_types:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, model_id)
            self.list_widget.addItem(item)
    
    def _select_all(self):
        """Select all items."""
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSelected(True)
    
    def _deselect_all(self):
        """Deselect all items."""
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSelected(False)
    
    def _on_export(self):
        """Handle export button click."""
        selected_items = self.list_widget.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select at least one note type to export."
            )
            return
        
        # Get file path
        last_dir = ConfigService.read(ConfigKey.LAST_EXPORT_DIR, str) or ""
        
        file_path = getSaveFile(
            parent=self,
            title="Export Note Types",
            dir_description="note_type_export",
            key="note_type_export",
            ext=".json",
            fname="note-types.json"
        )
        
        if not file_path:
            return
        
        # Ensure .json extension
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
        
        # Save directory for next time
        ConfigService.write(ConfigKey.LAST_EXPORT_DIR, os.path.dirname(file_path))
        
        # Get selected model IDs
        model_ids = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in selected_items
        ]
        
        # Perform export
        include_metadata = self.include_metadata_cb.isChecked()
        ConfigService.write(ConfigKey.EXPORT_INCLUDE_METADATA, include_metadata)
        
        success = export_note_types_to_file(model_ids, file_path, include_metadata)
        
        if success:
            tooltip(f"Exported {len(model_ids)} note type(s) to {os.path.basename(file_path)}")
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Export Failed",
                "An error occurred while exporting. Check the console for details."
            )


class ImportPreviewDialog(QDialog):
    """Dialog for previewing and selecting note types to import."""
    
    def __init__(self, import_data: dict, parent=None):
        super().__init__(parent or mw)
        self.import_data = import_data
        self.setWindowTitle("Import Note Types")
        self.setMinimumWidth(450)
        self.setMinimumHeight(500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Metadata info (if present)
        metadata = self.import_data.get("metadata", {})
        if metadata:
            info_text = []
            if "exported_at" in metadata:
                info_text.append(f"Exported: {metadata['exported_at'][:10]}")
            if "anki_version" in metadata:
                info_text.append(f"Anki version: {metadata['anki_version']}")
            if "count" in metadata:
                info_text.append(f"Note types: {metadata['count']}")
            
            if info_text:
                info_label = QLabel(" | ".join(info_text))
                info_label.setStyleSheet("color: gray; font-size: 10px;")
                layout.addWidget(info_label)
        
        # Instructions
        instructions = QLabel(
            "Select the note types you want to import.\n"
            "Note types with ⚠️ already exist in your collection."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Note type list with checkboxes
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self._populate_list()
        layout.addWidget(self.list_widget)
        
        # Select buttons
        select_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all)
        select_layout.addWidget(select_all_btn)
        select_layout.addWidget(deselect_all_btn)
        select_layout.addStretch()
        layout.addLayout(select_layout)
        
        # Conflict action setting
        conflict_group = QGroupBox("Default action for name conflicts")
        conflict_layout = QVBoxLayout(conflict_group)
        
        current_action = ConfigService.read(ConfigKey.DEFAULT_CONFLICT_ACTION, str)
        
        from aqt.qt import QRadioButton
        
        self.action_ask = QRadioButton("Ask me each time")
        self.action_rename = QRadioButton("Auto-rename with '(imported)' suffix")
        self.action_skip = QRadioButton("Skip conflicting note types")
        
        self.action_ask.setChecked(current_action == ConflictAction.ASK)
        self.action_rename.setChecked(current_action == ConflictAction.RENAME)
        self.action_skip.setChecked(current_action == ConflictAction.SKIP)
        
        conflict_layout.addWidget(self.action_ask)
        conflict_layout.addWidget(self.action_rename)
        conflict_layout.addWidget(self.action_skip)
        
        layout.addWidget(conflict_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_import)
        button_box.rejected.connect(self.reject)
        
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Import")
        
        layout.addWidget(button_box)
    
    def _populate_list(self):
        """Populate the list with note types from import data."""
        note_types = self.import_data.get("note_types", [])
        
        for i, nt in enumerate(note_types):
            name = nt.get("name", f"Note Type {i+1}")
            field_count = len(nt.get("fields", []))
            template_count = len(nt.get("templates", []))
            
            # Check if exists
            existing = mw.col.models.by_name(name) if mw.col else None
            conflict_marker = "⚠️ " if existing else ""
            
            display_text = f"{conflict_marker}{name} ({field_count} fields, {template_count} cards)"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setSelected(True)  # Select by default
            self.list_widget.addItem(item)
    
    def _select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSelected(True)
    
    def _deselect_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setSelected(False)
    
    def _on_import(self):
        """Handle import button click."""
        # Save conflict action preference
        if self.action_ask.isChecked():
            action = ConflictAction.ASK
        elif self.action_rename.isChecked():
            action = ConflictAction.RENAME
        else:
            action = ConflictAction.SKIP
        
        ConfigService.write(ConfigKey.DEFAULT_CONFLICT_ACTION, action)
        self.accept()
    
    def get_selected_indices(self) -> list[int]:
        """Get indices of selected note types."""
        return [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.list_widget.selectedItems()
        ]


class ConflictResolutionDialog(QDialog):
    """Dialog for resolving individual name conflicts during import."""
    
    SKIP = 0
    RENAME = 1
    OVERWRITE = 2
    CANCELLED = -1
    
    def __init__(self, note_type_name: str, parent=None, show_apply_to_all: bool = False):
        super().__init__(parent or mw)
        self.note_type_name = note_type_name
        self.show_apply_to_all = show_apply_to_all
        self.result_action = self.CANCELLED
        self.apply_to_all = False
        
        self.setWindowTitle("Name Conflict")
        self.setMinimumWidth(400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Message
        message = QLabel(
            f"A note type named '<b>{self.note_type_name}</b>' already exists.\n\n"
            "What would you like to do?"
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Option buttons
        skip_btn = QPushButton("Skip (don't import)")
        skip_btn.clicked.connect(lambda: self._set_result(self.SKIP))
        layout.addWidget(skip_btn)
        
        rename_btn = QPushButton("Import with new name (add '(imported)' suffix)")
        rename_btn.clicked.connect(lambda: self._set_result(self.RENAME))
        layout.addWidget(rename_btn)
        
        # Check if notes are using this note type
        existing = mw.col.models.by_name(self.note_type_name) if mw.col else None
        use_count = mw.col.models.use_count(existing) if existing else 0
        
        overwrite_btn = QPushButton("Overwrite existing note type")
        if use_count > 0:
            overwrite_btn.setEnabled(False)
            overwrite_btn.setToolTip(f"Cannot overwrite: {use_count} note(s) are using this note type")
        overwrite_btn.clicked.connect(lambda: self._set_result(self.OVERWRITE))
        layout.addWidget(overwrite_btn)
        
        # Apply to all checkbox
        if self.show_apply_to_all:
            layout.addSpacing(10)
            self.apply_to_all_cb = QCheckBox("Apply this choice to all remaining conflicts")
            layout.addWidget(self.apply_to_all_cb)
        
        # Cancel button
        layout.addSpacing(10)
        cancel_btn = QPushButton("Cancel Import")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
    
    def _set_result(self, action: int):
        """Set the result and close dialog."""
        self.result_action = action
        if self.show_apply_to_all:
            self.apply_to_all = self.apply_to_all_cb.isChecked()
        self.accept()
    
    def exec(self) -> int:
        """Execute dialog and return the chosen action."""
        super().exec()
        return self.result_action
    
    def exec_with_apply_to_all(self) -> tuple[int, bool]:
        """Execute dialog and return (action, apply_to_all)."""
        super().exec()
        return (self.result_action, self.apply_to_all)
