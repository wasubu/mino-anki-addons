"""
Note Type Export - Anki Add-on
Export and import note types (models) as JSON files.

Author: Anki Plugins
Version: 1.0.0
"""

__version__ = "1.0.0"

try:
    from .binding import run
    run()
except ImportError as ie:
    print(f"""
    [WARNING] Note Type Export: Import error - {ie}
    Running in test mode.
    """)
