from fastapi import FastAPI

from docker_service import DockerService

docker = DockerService()

print(docker.list_containers())

app = FastAPI(
    title="Nexus",
    version="0.1"
)


@app.get("/")
def root():
    return {
        "name": "Nexus",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }