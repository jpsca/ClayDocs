import jinjax_ui
from claydocs import Docs, starter_theme_path


pages = [
    "index.md",
    "internal.md",
]

docs = Docs(pages, search=False, add_ons=[jinjax_ui])

# Hack for not duplicating the starter theme in the same repo
# We had to change the tailwind.config.js too so it doesn't prune
# the classes inside those components.
# In other words: don't do this at home
docs.catalog.add_folder(starter_theme_path)


if __name__ == "__main__":
    docs.run()
