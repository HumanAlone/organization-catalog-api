from math import atan2, cos, radians, sin, sqrt

from sqlalchemy.orm import Session

from app.models import Business


def get_business_subtree_ids(db: Session, root_id: int) -> set[int]:
    """Возвращает ID корня и потомков"""
    all_ids = {root_id}

    children = db.query(Business.id).filter(Business.parent_id == root_id).all()
    child_ids = {c[0] for c in children}
    all_ids.update(child_ids)

    if child_ids:
        grandchildren = (
            db.query(Business.id).filter(Business.parent_id.in_(child_ids)).all()
        )
        grandchild_ids = {g[0] for g in grandchildren}
        all_ids.update(grandchild_ids)

    return all_ids


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    R = 6371000  # радиус Земли в метрах
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
