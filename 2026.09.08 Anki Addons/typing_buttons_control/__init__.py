from . import menu, only_again, typebox

# Initialize Tools menu options
menu.setup()

# Read config once on startup
config = menu.get_config()

if config.get("enable_typebox", True):
    typebox.setup()

if config.get("enable_only_again", True):
    only_again.setup()