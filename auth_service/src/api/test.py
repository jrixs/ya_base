from fastapi import APIRouter, status

router = APIRouter()


@router.get("/",
            summary="test",
            description="test",
            status_code=status.HTTP_200_OK
            )
def test():
    return {"test": "ok"}
