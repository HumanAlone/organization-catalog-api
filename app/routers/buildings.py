from math import cos, radians

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Building
from app.schemas import BuildingResponse
from app.utils import haversine_distance

router = APIRouter(prefix="/buildings", tags=["Buildings"])


@router.get(
    "/nearby",
    response_model=list[BuildingResponse],
    summary="Список зданий в области",
)
def get_buildings_nearby(
    lat: float = Query(..., ge=-90, le=90, description="Широта центра"),
    lon: float = Query(..., ge=-180, le=180, description="Долгота центра"),
    radius: float = Query(
        ..., gt=0, le=100_000, description="Радиус в метрах (макс. 100 км)"
    ),
    shape: str = Query(
        "circle", regex="^(circle|square)$", description="Форма области"
    ),
    db: Session = Depends(get_db),
):
    """
    Возвращает список зданий, которые находятся в заданной области

    Args:
        lat: Широта центральной точки
        lon: Долгота центральной точки
        circle: Здания в круге заданного радиуса
        square: Здания в квадрате со стороной = 2 * радиус

    Returns:
        Список зданий
    """
    # Рассчитываем bounding box
    lat_delta = radius / 111000
    lon_delta = radius / (111000 * cos(radians(lat)))

    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta

    # Получаем здания в bounding box
    buildings_in_box = (
        db.query(Building)
        .filter(
            Building.latitude.between(min_lat, max_lat),
            Building.longitude.between(min_lon, max_lon),
        )
        .all()
    )

    # Фильтруем по форме
    if shape == "circle":
        buildings = [
            b
            for b in buildings_in_box
            if haversine_distance(lat, lon, b.latitude, b.longitude) <= radius
        ]
    else:
        buildings = buildings_in_box

    return buildings
