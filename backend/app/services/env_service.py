import hashlib
from pathlib import Path

# Dispositivo por default según template
TEMPLATE_DEVICE_DEFAULTS = {
    "msp430": "/dev/ttyACM0",
    "esp32":  "/dev/ttyUSB0",
    "ros2":   "/dev/video0",
}


class EnvService:

    def generate(
        self,
        project_id: str,
        template: str,
        device: str | None = None,
    ) -> str:

        lines = [
            f"PROJECT_ID={project_id}",
            f"PROJECT_NAME={project_id}",
            "TZ=America/Mexico_City",
        ]

        if template == "ros2":

            domain_id = (
                int(hashlib.sha256(project_id.encode()).hexdigest(), 16)
                % 101
            )

            lines.append(f"ROS_DOMAIN_ID={domain_id}")
            lines.append("DISPLAY=:0")

        # Device: usa el que el usuario especificó, si no el default del template
        resolved_device = device or TEMPLATE_DEVICE_DEFAULTS.get(template)

        if resolved_device:
            lines.append(f"DEVICE={resolved_device}")

        return "\n".join(lines) + "\n"

    def save(
        self,
        project_path: Path,
        project_id: str,
        template: str,
        device: str | None = None,
    ):

        content = self.generate(project_id, template, device)

        (Path(project_path) / ".env").write_text(content)