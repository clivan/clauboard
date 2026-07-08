import subprocess

class GitService:

    def init(self, path):

        subprocess.run(
            ["git", "init"],
            cwd=path
        )