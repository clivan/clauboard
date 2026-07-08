from pathlib import Path

class WorkspaceService:

    def create(self, path: str):

        Path(path).mkdir(
            parents=True,
            exist_ok=True
        )

    def mkdir(self, path):

        Path(path).mkdir(exist_ok=True)

    def exists(self, path):

        return Path(path).exists()