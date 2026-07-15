from pathlib import Path

BASE_DIR = Path("/workspace")

PROJECTS_DIR = BASE_DIR / "projects"

PLUGINS_DIR = Path("/plugins")

TEMPLATES_DIR = BASE_DIR / "templates"

WORKSPACE_DIRS = [

    "compose",

    "apps",

    "data",

    "logs",

    "backups",

    "templates",

    ".clauboard",

]