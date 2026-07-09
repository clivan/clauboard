from pathlib import Path


class WorkspaceService:

    DIRECTORIES = (
        "compose",
        "apps",
        "data",
        "logs",
        "backups",
        "templates",
        ".clauboard",
    )

    def initialize(self, project_path: Path):

        project_path.mkdir(
            parents=True,
            exist_ok=True
        )

        for directory in self.DIRECTORIES:

            (
                project_path /
                directory
            ).mkdir(exist_ok=True)

        readme = project_path / "README.md"

        if not readme.exists():

            readme.write_text(
                "# Clauboard Project\n"
            )