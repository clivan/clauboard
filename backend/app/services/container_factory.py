from app.models.application import Application
from app.models.application_type import ApplicationType


class ContainerFactory:

    @staticmethod
    def build(app: Application):

        if app.type == ApplicationType.TOOLCHAIN:
            raise ValueError(
                f"'{app.id}' es type=toolchain: no se maneja como "
                "contenedor persistente vía ApplicationManager. Los "
                "toolchains se copian a un proyecto (compose/) y se "
                "ejecutan con 'docker compose run --rm' — todavía no "
                "implementado (pendiente)."
            )

        ports = {}

        for p in app.ports:
            ports[f"{p.container}/{p.protocol}"] = p.host

        volumes = {}

        for v in app.volumes:

            if v.host.startswith("~"):
                raise ValueError(
                    f"Ruta de volumen inválida '{v.host}': '~' no se "
                    "puede resolver desde dentro del contenedor del "
                    "backend (no conoce el HOME real del host). "
                    "Usa una ruta absoluta, ej. /home/claudio/Sync"
                )

            volumes[v.host] = {
                "bind": v.container,
                "mode": "rw"
            }

        config = {

            "image": app.image,

            "name": app.container_name,

            "detach": True,

            "restart_policy": {
                "Name": app.restart
            },

            "network": "clauboard-net",

            "ports": ports,

            "volumes": volumes,

            "environment": app.environment,

            "labels": app.labels,
        }

        if app.devices:
            config["devices"] = app.devices

        if app.privileged:
            config["privileged"] = True

        return config