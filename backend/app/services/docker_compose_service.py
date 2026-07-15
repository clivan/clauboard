import subprocess
from pathlib import Path

from app.utils.logger import logger


class DockerComposeService:
    """
    Única clase responsable de invocar `docker compose`.
    Ninguna otra clase debe ejecutar subprocess contra Docker Compose
    (convención definida en el contexto del proyecto).
    """

    def _run(
        self,
        args: list[str],
        compose_file: Path,
        project_name: str,
        capture: bool = False,
    ) -> str | None:

        command = [
            "docker", "compose",
            "-f", str(compose_file),
            "-p", project_name,
            *args,
        ]

        logger.info(f"[{project_name}] docker compose {' '.join(args)}")

        result = subprocess.run(
            command,
            capture_output=capture,
            text=True,
        )

        if result.returncode != 0:

            error = result.stderr if capture else (
                f"docker compose {' '.join(args)} "
                f"terminó con código {result.returncode}"
            )

            logger.error(f"[{project_name}] fallo: {error}")

            raise RuntimeError(error)

        return result.stdout if capture else None

    def up(self, compose_file: Path, project_name: str):

        self._run(["up", "-d"], compose_file, project_name)

    def down(self, compose_file: Path, project_name: str):

        self._run(["down"], compose_file, project_name)

    def restart(self, compose_file: Path, project_name: str):

        self._run(["restart"], compose_file, project_name)

    def logs(   
        self,
        compose_file: Path,
        project_name: str,
        tail: int = 200,
    ) -> str:

        return self._run(
            ["logs", "--no-color", "--tail", str(tail)],
            compose_file,
            project_name,
            capture=True,
        )

    def status(self, compose_file: Path, project_name: str) -> str:

        return self._run(
            ["ps", "--format", "json"],
            compose_file,
            project_name,
            capture=True,
        )