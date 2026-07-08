from app.models.application import Application


class ContainerFactory:

    @staticmethod
    def build(app: Application):

        ports = {}

        for p in app.ports:
            ports[f"{p.container}/{p.protocol}"] = p.host

        volumes = {}

        for v in app.volumes:
            volumes[v.host] = {
                "bind": v.container,
                "mode": "rw"
            }

        return {

            "image": app.image,

            "name": app.container_name,

            "detach": True,

            "restart_policy": {
                "Name": app.restart
            },

            "ports": ports,

            "volumes": volumes,

            "environment": app.environment,

            "labels": app.labels
        }