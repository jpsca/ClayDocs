import subprocess

from claydocs import Docs
from markupsafe import Markup


pages = {
    "en": [
        "index.md",
        [
            "Guide",
            [
                "guide/index.md",
                "guide/arguments.md",
                "guide/extra.md",
                "guide/css_and_js.md",
            ],
        ],
    ],
    "es": [
        "index.md",
        "ole.md",
    ],
}

# `code: name` dict of available languages
languages = {
    "en": "English",
    "es": "Español",
}

docs = Docs(pages, languages=languages, default="en")


if __name__ == "__main__":
    proc = subprocess.Popen([
        "npx", "tailwindcss",
        "-i", "./static/_source.css",
        "-o", "./static/docs.css",
        "--watch",
    ])
    try:
        docs.run()
    finally:
        proc.terminate()
