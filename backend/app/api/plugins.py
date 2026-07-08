from fastapi import APIRouter

router = APIRouter(tags=["Plugins"])


@router.get("/plugins")
def plugins():
    return []