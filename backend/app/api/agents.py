from fastapi import APIRouter

router = APIRouter(tags=["Agents"])


@router.get("/agents")
def agents():
    # Pendiente de decidir el alcance lo los agentes.
    return []