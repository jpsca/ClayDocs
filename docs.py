import subprocess

from claydocs import Docs


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

languages = {
    "en": "English",
    "es": "Español",
}

docs = Docs(
    pages,
    # `code: name` dict of available languages
    languages=languages,
    # Language mounted at "/" instead of "/lang/"
    default="en",
)


def tailwind():
    return subprocess.Popen([
        "npx", "tailwindcss",
        "-i", "./static/_source.css",
        "-o", "./static/docs.css",
        "--watch",
    ])

if __name__ == "__main__":
    docs.run()
    # proc_tailwind = tailwind()
    # try:
    #     docs.run()
    # finally:
    #     proc_tailwind.terminate()
