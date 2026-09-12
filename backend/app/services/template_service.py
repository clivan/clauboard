from pathlib import Path
import shutil
import yaml

from app.config import TEMPLATES_DIR

# Servicios del compose.yml de ROS2 que el usuario puede elegir incluir.
# "ros2" (el nodo base) siempre se incluye, no es opcional.
ROS2_OPTIONAL_SERVICES = {"realsense-driver", "vision-processing", "gazebo"}


class TemplateService:

    def __init__(self, templates_path: Path = TEMPLATES_DIR):
        self.templates_path = Path(templates_path)

    def list(self):
        if not self.templates_path.exists():
            return []

        return [
            d.name
            for d in self.templates_path.iterdir()
            if d.is_dir()
        ]

    def exists(self, template: str) -> bool:
        return (self.templates_path / template).exists()

    def apply(self, template: str, destination: str, ros2_services: "list[str] | None" = None):

        source = self.templates_path / template

        if not source.exists():
            raise FileNotFoundError(
                f"Template '{template}' not found."
            )

        destination = Path(destination)

        for item in source.iterdir():

            target = destination / item.name

            # Caso especial: el compose.yml de ROS2 se filtra según los
            # servicios opcionales elegidos, en vez de copiarse tal cual.
            if template == "ros2" and item.is_dir() and item.name == "compose":
                self._apply_ros2_compose(item, target, ros2_services)
                continue

            if item.is_dir():
                shutil.copytree(
                    item,
                    target,
                    dirs_exist_ok=True
                )

            else:
                shutil.copy2(item, target)

    def _apply_ros2_compose(self, source_dir: Path, target_dir: Path, services: "list[str] | None"):

        target_dir.mkdir(parents=True, exist_ok=True)

        for item in source_dir.iterdir():

            if item.name != "compose.yml":
                # Cualquier otro archivo en la carpeta compose/ se copia
                # normal (por si en el futuro hay algo más ahí).
                if item.is_dir():
                    shutil.copytree(item, target_dir / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target_dir / item.name)
                continue

            data = yaml.safe_load(item.read_text())

            # Sin selección explícita: se copia completo, comportamiento
            # igual al de antes de esta feature.
            if services is None:
                shutil.copy2(item, target_dir / item.name)
                continue

            selected = set(services) & ROS2_OPTIONAL_SERVICES

            filtered_services = {
                name: config
                for name, config in data.get("services", {}).items()
                if name == "ros2" or name in selected
            }

            data["services"] = filtered_services

            (target_dir / "compose.yml").write_text(
                yaml.dump(data, sort_keys=False, default_flow_style=False)
            )