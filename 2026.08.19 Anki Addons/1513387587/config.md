# Configuration Options

## default_conflict_action
- **Type**: string
- **Default**: `"ask"`
- **Options**: `"ask"`, `"rename"`, `"skip"`
- **Description**: What to do when importing a note type with a name that already exists in the collection

### Values:
- `"ask"` - Show a dialog asking the user what to do for each conflict
- `"rename"` - Automatically rename with "(imported)" suffix
- `"skip"` - Don't import note types that already exist

---

## export_include_metadata
- **Type**: boolean
- **Default**: `true`
- **Description**: Whether to include metadata (export date, Anki version, addon version) in exported files

---

## last_export_dir
- **Type**: string
- **Default**: `""`
- **Description**: Last used directory for export file dialog (automatically updated)

---

## last_import_dir
- **Type**: string
- **Default**: `""`
- **Description**: Last used directory for import file dialog (automatically updated)
