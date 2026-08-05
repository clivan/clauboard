import docker

from app.utils.logger import logger


CLAUBOARD_NETWORK = "clauboard-net"


class DockerService:

    def __init__(self):

        self.client = docker.from_env()

    def containers(self):

        return self.client.containers.list(all=True)

    def get(self, name):

        try:
            return self.client.containers.get(name)

        except docker.errors.NotFound:
            return None

    def exists(self, name):

        return self.get(name) is not None

    def running(self, name):

        container = self.get(name)

        if container is None:
            return False

        return container.status == "running"

    def _reconnect_network(self, container):
        """
        Reconecta el contenedor a clauboard-net si la referencia de
        red quedó huérfana (pasa cuando se hace docker compose down+up
        y la red se recrea con un ID distinto).
        """

        try:
            network = self.client.networks.get(CLAUBOARD_NETWORK)
            network.disconnect(container, force=True)
        except Exception:
            pass

        try:
            network = self.client.networks.get(CLAUBOARD_NETWORK)
            network.connect(container)
            logger.info(
                f"[docker] {container.name} reconectado a {CLAUBOARD_NETWORK}"
            )
        except Exception as error:
            logger.warning(
                f"[docker] no se pudo reconectar {container.name}: {error}"
            )

    def start(self, name):

        container = self.get(name)

        if container is None:
            return

        try:
            container.start()

        except docker.errors.NotFound as error:

            if "network" in str(error).lower() and "not found" in str(error).lower():

                logger.warning(
                    f"[docker] {name}: red huérfana detectada, reconectando..."
                )

                self._reconnect_network(container)
                container.start()

            else:
                raise

    def stop(self, name):

        container = self.get(name)

        if container:
            container.stop()

    def restart(self, name):

        container = self.get(name)

        if container:
            container.restart()

    def remove(self, name):

        container = self.get(name)

        if container:
            container.remove(force=True)

    def run(self, config):

        try:
            return self.client.containers.run(**config)

        except docker.errors.APIError as error:
            raise RuntimeError(str(error))

    def pull_progress(self, image: str):
        """
        Genera eventos de progreso del pull de una imagen.
        Cada yield es un dict con: status, layer, progress, percent (0-100).
        """

        layers = {}

        try:
            for event in self.client.api.pull(image, stream=True, decode=True):

                status  = event.get("status", "")
                layer   = event.get("id", "")
                detail  = event.get("progressDetail", {})
                current = detail.get("current", 0)
                total   = detail.get("total", 0)

                if layer and total:
                    layers[layer] = (current, total)

                # Calcula porcentaje global sobre todas las capas conocidas
                total_bytes   = sum(t for _, t in layers.values())
                current_bytes = sum(c for c, _ in layers.values())

                percent = int(current_bytes * 100 / total_bytes) if total_bytes else 0

                yield {
                    "status":   status,
                    "layer":    layer,
                    "progress": f"{current_bytes // 1024 // 1024} MB / {total_bytes // 1024 // 1024} MB",
                    "percent":  percent,
                }

        except docker.errors.APIError as error:
            yield {"status": "error", "layer": "", "progress": str(error), "percent": 0}