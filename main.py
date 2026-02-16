import uvicorn
from fastapi import Depends, FastAPI

from app.dependencies import verify_api_key
from app.routers import buildings, businesses, organizations

app = FastAPI(
    title="Organization Catalog API",
    description="Тестовое задание на должность разработчика",
    version="1.0.0",
    dependencies=[Depends(verify_api_key)],
)

app.include_router(organizations.router)
app.include_router(buildings.router)
app.include_router(businesses.router)


@app.get(
    "/",
    summary="Проверка работоспособности сервиса",
)
def health_check():
    return {
        "service": "Organization Catalog Api",
        "health": "OK",
        "author": "Sergey Naryshkin",
        "description": "Тестовое задание на должность разработчика",
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
