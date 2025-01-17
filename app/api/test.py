# from fastapi import APIRouter
# from sqlalchemy import select

# from app.core.database import db_conn
# from app.models.listing import ListingImage


# router = APIRouter()


# @router.get("/tt", response_model=dict)
# def test_listing(db: db_conn):
#     print("test endpoint called")

#     #   stmt = select(User).where(User.age >= min_age).order_by(User.name)
#     #     result = session.execute(stmt)

#     listings: list[ListingImage] = db.scalars(select(ListingImage).where(ListingImage.listing_id == 1)).all()

#     # query = select(ListingImage).where(ListingImage.listing_id == 12)
#     # result = db.execute(query).scalars().all()
#     # print(result)

#     print(listings)
#     for i in listings:
#         print(i)

#     return {}
