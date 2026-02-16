from math import cos, radians

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.models import Building, Business, Organization, OrganizationBusiness
from app.schemas import OrganizationResponse
from app.utils import haversine_distance

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get(
    "/search",
    response_model=list[OrganizationResponse],
    summary="Организация по названию",
)
def search_organization_by_name(
    name: str = Query(..., min_length=2, description="Название организации для поиска"),
    db: Session = Depends(get_db),
):
    """
    Поиск организаций по названию (регистронезависимый, частичное совпадение)

    Args:
        name: Часть названия организации, минимум 2 символа

    Returns:
        Список организаций, включая здание, телефоны, виды деятельности
    """
    orgs = (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            selectinload(Organization.businesses),
        )
        .all()
    )

    # Регистронезависимый поиск
    search_term = name.lower()
    filtered_orgs = [org for org in orgs if search_term in org.name.lower()]
    return filtered_orgs


@router.get(
    "/nearby",
    response_model=list[OrganizationResponse],
    summary="Организации в радиусе",
)
def get_organizations_nearby(
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
    Возвращает список организаций, которые находятся в заданной области

    Args:
        lat: Широта центральной точки
        lon: Долгота центральной точки
        circle: Организации в круге заданного радиуса
        square: Организации в квадрате со стороной = 2 * радиус

    Returns:
        Список организаций, включая здание, телефоны, виды деятельности
    """

    # Рассчитываем bounding box
    lat_delta = radius / 111000
    cos_lat = max(cos(radians(lat)), 1e-10)
    lon_delta = radius / (111000 * cos(radians(cos_lat)))

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
        building_ids = [
            b.id
            for b in buildings_in_box
            if haversine_distance(lat, lon, b.latitude, b.longitude) <= radius
        ]
    else:
        building_ids = [b.id for b in buildings_in_box]

    if not building_ids:
        return []

    orgs = (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            selectinload(Organization.businesses),
        )
        .filter(Organization.building_id.in_(building_ids))
        .all()
    )

    return orgs


@router.get(
    "/building/{building_id}",
    response_model=list[OrganizationResponse],
    summary="Список организаций в здании",
)
def get_organizations_by_building(building_id: int, db: Session = Depends(get_db)):
    """Возвращает список всех организаций, находящихся в конкретном здании

    Args:
        building_id: Идентификатор здания

    Returns:
        Список организаций, включая здание, телефоны, виды деятельности

    Raises:
        404: Здание не найдено
    """
    building = db.get(Building, building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Здание с ID {building_id} не найден",
        )

    orgs = (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            selectinload(Organization.businesses),
        )
        .filter(Organization.building_id == building_id)
        .all()
    )

    return orgs


@router.get(
    "/business/{business_id}",
    response_model=list[OrganizationResponse],
    summary="Список организаций по виду деятельности",
)
def get_organizations_by_business(business_id: int, db: Session = Depends(get_db)):
    """Возвращает список всех организаций, которые относятся к указанному виду деятельности

    Args:
        business_id: Идентификатор вида деятельности

    Returns:
        Список организаций, включая здание, телефоны, виды деятельности

    Raises:
        404: Вид деятельности не найден
    """
    business = db.get(Business, business_id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Вид деятельности с ID {business_id} не найден",
        )

    orgs = (
        db.query(Organization)
        .join(
            OrganizationBusiness,
            Organization.id == OrganizationBusiness.organization_id,
        )
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            selectinload(Organization.businesses),
        )
        .filter(OrganizationBusiness.business_id == business_id)
        .all()
    )

    return orgs


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
    summary="Организация по идентификатору",
)
def get_organization_by_id(organization_id: int, db: Session = Depends(get_db)):
    """
    Возвращает информацию об организации по её идентификатору

    Args:
        organization_id: Идентификатор организации

    Returns:
        Информация об организации, включая здание, телефоны, виды деятельности

    Raises:
        404: Организация не найдена
    """
    org = (
        db.query(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            selectinload(Organization.businesses),
        )
        .filter(Organization.id == organization_id)
        .first()
    )

    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Организация с ID {organization_id} не найдена",
        )

    return org
