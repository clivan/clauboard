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

        env_file = compose_file.parent.parent / ".env"

        command = [
            "docker", "compose",
            *(["--env-file", str(env_file)] if env_file.exists() else []),
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

    def run(self, compose_file: Path, project_name: str, service: str) -> str:
        """
        Equivalente a `docker compose run --rm <service>`.
        No bloquea — retorna el comando completo para que el usuario
        lo corra en su propia terminal (no abre un TTY desde la API).
        """

        return (
            f"docker compose "
            f"--env-file {compose_file.parent.parent / '.env'} "
            f"-f {compose_file} "
            f"-p {project_name} "
            f"run --rm {service}"
        )

    def down(self, compose_file: Path, project_name: str):

        self._run(["down", "--timeout", "3"], compose_file, project_name)

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