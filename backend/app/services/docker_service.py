import docker

class DockerService:

    def __init__(self):
        self.client = docker.from_env()
    
    def list_containers(self):
        containers = self.client.containers.list(all=True)
        result = []
        for c in containers:
            result.append({
                "id": c.short_id,
                "name": c.name,
                "image": c.image.tags[0] if c.image.tags else "unknown",
                "status": c.status
            })
        return result

    def get(self, name):
        return self.client.containers.get(name)

    def start(self, name):
        self.get(name).start()

    def stop(self, name):
        self.get(name).stop()   

    def restart(self, name):
        self.get(name).restart()

    def status(self, name):
        return self.get(name).status
    
    def logs(self, name):
        return self.get(name).logs().decode()
    
    
