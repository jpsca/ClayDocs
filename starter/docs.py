import subprocess

from claydocs import Docs


pages = [
    "index.md",
]

docs = Docs(
    pages,

    # `code: name` dict of available languages
    # languages=languages,

    # Language mounted at "/" instead of "/lang/"
    # default="en",
)


def tailwind():
    return subprocess.Popen([
        "npx", "tailwindcss",
        "-i", "./static/_source.css",
        "-o", "./static/docs.css",
        "--watch",
    ])

if __name__ == "__main__":
    proc_tailwind = tailwind()
    try:
        docs.run()
    finally:
        proc_tailwind.terminate()
