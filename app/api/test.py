from fastapi import APIRouter
from sqlalchemy import select

from app.core.database import DB
from app.models.item import ItemImage


router = APIRouter()


@router.get("/tt", response_model=dict)
def test_item(db: DB):
    print("test endpoint called")

    #   stmt = select(User).where(User.age >= min_age).order_by(User.name)
    #     result = session.execute(stmt)

    items: list[ItemImage] = db.scalars(select(ItemImage).where(ItemImage.item_id == 1)).all()

    # query = select(ItemImage).where(ItemImage.item_id == 12)
    # result = db.execute(query).scalars().all()
    # print(result)

    print(items)
    for i in items:
        print(i)

    return {}
