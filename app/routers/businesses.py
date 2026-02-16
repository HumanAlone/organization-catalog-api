from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.models import Business, Organization, OrganizationBusiness
from app.schemas import OrganizationResponse
from app.utils import get_business_subtree_ids

router = APIRouter(prefix="/businesses", tags=["Businesses"])


@router.get(
    "/{business_id}/organizations",
    response_model=list[OrganizationResponse],
    summary="Список организаций по виду деятельности рекурсивно",
)
def get_organizations_by_business_recursive(
    business_id: int, db: Session = Depends(get_db)
):
    """Возвращает список организаций по виду деятельности и всем его подвидам

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

    business_ids = get_business_subtree_ids(db, business_id)

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
        .filter(OrganizationBusiness.business_id.in_(business_ids))
        .all()
    )

    return orgs
