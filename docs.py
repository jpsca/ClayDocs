import subprocess
from claydocs import Docs


nav = [
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
]

docs = Docs(nav)


if __name__ == "__main__":
    proc = subprocess.Popen([
        "npx", "tailwindcss",
        "-i", "./static/_source.css",
        "-o", "./static/docs.css",
        "--watch",
    ])
    docs.run()
    proc.terminate()
