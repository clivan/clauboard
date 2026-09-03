import hashlib
from pathlib import Path

from app.services.framework_registry import resolve_image

# Dispositivo por default según template
TEMPLATE_DEVICE_DEFAULTS = {
    "msp430": "/dev/ttyACM0",
    "esp32":  "/dev/ttyUSB0",
    "ros2":   "/dev/video0",
    "rpi-pico": "/dev/ttyACM0",
}

# Templates cuya imagen depende de framework/arch elegidos (ver
# framework_registry.py). El resto usa la imagen fija de su
# compose.yml sin variable MICRO_IMAGE.
TEMPLATES_WITH_FRAMEWORK = {"avr", "msp430", "stm32", "esp32", "rpi-pico"}


class EnvService:

    def generate(
        self,
        project_id: str,
        template: str,
        device: str | None = None,
        framework: str | None = None,
        arch: str | None = None,
        microros: bool = False,
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

        if template in TEMPLATES_WITH_FRAMEWORK:

            resolved_image = resolve_image(template, framework, arch, microros)

            if resolved_image:
                lines.append(f"MICRO_IMAGE={resolved_image}")

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
        framework: str | None = None,
        arch: str | None = None,
        microros: bool = False,
    ):

        content = self.generate(
            project_id, template, device, framework, arch, microros
        )

        (Path(project_path) / ".env").write_text(content)