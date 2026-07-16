import hashlib
from pathlib import Path

# Variables extra por template, además de PROJECT_ID/PROJECT_NAME/TZ
# que siempre se generan. AVR y STM32 no llevan DEVICE porque usan
# privileged: true en su compose (programador USB genérico, sin un
# path de dispositivo fijo y confiable).
TEMPLATE_ENV_DEFAULTS = {
    "msp430": {"DEVICE": "/dev/ttyACM0"},
    "esp32": {"DEVICE": "/dev/ttyUSB0"},
    "ros2": {"DEVICE": "/dev/video0"},
}


class EnvService:

    def generate(self, project_id: str, template: str) -> str:

        lines = [
            f"PROJECT_ID={project_id}",
            f"PROJECT_NAME={project_id}",
            "TZ=America/Mexico_City",
        ]

        if template == "ros2":

            # Deriva un ROS_DOMAIN_ID estable a partir del id del
            # proyecto, para que dos proyectos ROS2 no choquen en la
            # misma red por default (0-100, rango recomendado por ROS2).
            domain_id = (
                int(hashlib.sha256(project_id.encode()).hexdigest(), 16)
                % 101
            )

            lines.append(f"ROS_DOMAIN_ID={domain_id}")

            # No se puede leer el DISPLAY real de tu sesión desde
            # dentro del contenedor del backend (no comparte tu X).
            # ':0' es el valor típico en Linux de escritorio único;
            # ajústalo a mano si el tuyo es distinto (`echo $DISPLAY`
            # en tu terminal real te lo confirma).
            lines.append("DISPLAY=:0")

        extra = TEMPLATE_ENV_DEFAULTS.get(template, {})

        for key, value in extra.items():
            lines.append(f"{key}={value}")

        return "\n".join(lines) + "\n"

    def save(self, project_path: Path, project_id: str, template: str):

        content = self.generate(project_id, template)

        (Path(project_path) / ".env").write_text(content)