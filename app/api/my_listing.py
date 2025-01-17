# import os
# from pathlib import Path
# import secrets
# import shutil
# from fastapi import APIRouter, File, HTTPException, UploadFile
# import filetype
# from sqlalchemy import delete, func, select, update
# from app.core.database import db_conn
# from app.core.utils.auth import AUTH_ME
# from app.models.listing import Listing, ListingImage, ListingStatus
# from app.schemas.listing import ListingAddRequest, ListingImageInfo, ListingInfo, ListingStatusChange, ListingUpdateRequest


# router = APIRouter()

# # creates the assets directory if it doesn't exist
# STORAGE_SOURCE = "http://127.0.0.1:8000"
# STORAGE_BUCKET = "assets/listing_images"


# # max file size (10MB)
# MAX_listing_IMAGE_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
# MAX_IMAGES_PER_listing = 10


# def save_listing_images(file: UploadFile) -> list[str, str]:
#     # Read first 8192 bytes for filetype detection
#     first_chunk = file.file.read(8192)
#     file.file.seek(0)  # Reset file pointer

#     # Detect file type using filetype
#     kind = filetype.guess(first_chunk)

#     if not kind:
#         raise HTTPException(status_code=400, detail="Could not determine file type")

#     # Validate if it's an image and check allowed types
#     allowed_mimes = {"image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"], "image/webp": [".webp"]}

#     if kind.mime not in allowed_mimes:
#         raise HTTPException(status_code=400, detail=f"Unsupported image type: {kind.mime}. Allowed types: JPEG, PNG, WEBP")

#     # Check file size
#     file.file.seek(0, 2)
#     if file.file.tell() > MAX_listing_IMAGE_FILE_SIZE:
#         raise HTTPException(status_code=400, detail="File too large")
#     file.file.seek(0)

#     # Generate file key and validate extension
#     file_key = secrets.token_hex(16)
#     file_extension = Path(file.filename).suffix.lower()

#     if file_extension not in [ext for exts in allowed_mimes.values() for ext in exts]:
#         raise HTTPException(status_code=400, detail="Invalid file extension")

#     # save file
#     file_path = Path(f"{STORAGE_BUCKET}/{file_key}{file_extension}")

#     # make the dir if not available
#     file_path.parent.mkdir(parents=True, exist_ok=True)

#     with file.file as source_file:
#         with file_path.open("wb") as destination_file:
#             shutil.copyfileobj(source_file, destination_file)

#     return file_key, file_extension


# def remove_listing_image(file_key: str, file_extension) -> None:
#     """removes the entire directory for an listing_key and all its contents."""
#     file_path = f"{STORAGE_BUCKET}/{file_key}{file_extension}"
#     try:
#         os.remove(Path(file_path))
#     except OSError as e:
#         raise HTTPException(status_code=500, detail=f"Failed to remove image: {str(e)}") from e


# @router.post("/add-image", response_model=ListingImageInfo, description="Adds new listing image")
# def add_image(user: AUTH_ME, db: db_conn, image: UploadFile = File(...)):
#     """
#     - images are saved and registered in db
#     - temporary files will be removed if listing_id is empty after 24 hours
#     """
#     file_key = None
#     file_extension = None

#     try:
#         file_key, file_extension = save_listing_images(image)
#         listing_image = ListingImage(
#             listing_id=None,
#             key=file_key,
#             extension=file_extension,
#             storage_source=STORAGE_SOURCE,
#             storage_bucket=STORAGE_BUCKET,
#         )

#         db.add(listing_image)
#         db.commit()

#         return ListingImageInfo.from_db_model(listing_image)

#     except Exception as e:
#         print(e)
#         db.rollback()
#         if file_key is not None and file_extension is not None:
#             remove_listing_image(file_key, file_extension)
#         raise HTTPException(status_code=500, detail=f"Failed to add image") from e


# @router.post("/remove-image/{image_key}", response_model=dict, description="Removes an listing image")
# def remove_image(user: AUTH_ME, db: db_conn, image_key: str):

#     try:
#         listing_image = db.scalar(select(ListingImage).where(ListingImage.key == image_key))

#         if not listing_image:
#             raise HTTPException(status_code=404, detail="Listing image not found")

#         if listing_image.listing_id is not None:
#             listing = db.scalar(select(Listing).where(Listing.id == listing_image.listing_id, Listing.user_id == user.id))
#             if not listing:
#                 raise HTTPException(status_code=404, detail="Listing image doesn't belong to the user")

#         db.execute(delete(ListingImage).where(ListingImage.key == listing_image.key))
#         remove_listing_image(listing_image.key, listing_image.extension)

#         db.commit()

#         return {"message": "Image deleted successfully"}

#     except Exception as e:
#         db.rollback()
#         print(e)
#         raise HTTPException(status_code=500, detail=f"Failed to remove image") from e


# @router.post("/add", description="Adds new listing")
# def add_listing(user: AUTH_ME, db: db_conn, data: ListingAddRequest):
#     listing_key = secrets.token_hex(16)
#     try:
#         listing = Listing(
#             user_id=user.id,
#             key=listing_key,
#             price=data.price,
#             price_negotiable=data.price_negotiable,
#             category_id=data.category_id,
#             title=data.title,
#             description=data.description,
#             latitude=data.latitude,
#             longitude=data.longitude,
#         )

#         db.add(listing)
#         db.flush()  # gets ID without committing

#         if data.image_keys:  # Protect against None
#             stmt = update(ListingImage).where(ListingImage.key.in_(data.image_keys)).values(listing_id=listing.id)
#             db.execute(stmt)

#         db.commit()
#         return {"success": True, "message": "Listing added successfully", "listing_id": listing.id}

#     except Exception as e:
#         db.rollback()
#         print(e)
#         raise HTTPException(status_code=500, detail="Failed to add listing") from e


# @router.post("/update", description="Update listing info")
# def update_listing(user: AUTH_ME, db: db_conn, data: ListingUpdateRequest):
#     try:
#         # check if listing is available and belongs to this user
#         listing = db.scalar(select(Listing).where(Listing.key == data.listing_key, Listing.user_id == user.id))
#         if not listing:
#             raise HTTPException(status_code=404, detail="Listing not found")

#         db.execute(
#             update(Listing)
#             .where(Listing.id == listing.id)
#             .values(
#                 price=data.price,
#                 price_negotiable=data.price_negotiable,
#                 category_id=data.category_id,
#                 title=data.title,
#                 description=data.description,
#                 updated_at=func.now(),
#             )
#         )

#         # clean up listing_ids from ListingImages
#         db.execute(update(ListingImage).where(ListingImage.listing_id == listing.id).values(listing_id=None))

#         if data.image_keys:  # protects against None
#             stmt = update(ListingImage).where(ListingImage.key.in_(data.image_keys)).values(listing_id=listing.id)
#             db.execute(stmt)

#         db.commit()

#         return {"success": True, "message": "Listing updated successfully"}

#     except Exception as e:
#         db.rollback()
#         print(e)
#         raise HTTPException(status_code=500, detail="Failed to update listing") from e


# @router.post("/change-status", description="Changes listing status and does corresponding action")
# def change_status(user: AUTH_ME, db: db_conn, data: ListingStatusChange):

#     try:

#         listing = db.scalar(select(Listing).where(Listing.key == data.listing_key, Listing.user_id == user.id))
#         if not listing:
#             raise HTTPException(status_code=404, detail="Listing not found")

#         db.execute(update(Listing).where(Listing.id == listing.id).values(status=data.status, updated_at=func.now()))
#         db.commit()

#         return {"success": True, "message": "Listing status changed successfully"}

#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Failed to update listing status") from e


# @router.post("/delete/{listing_key}", description="Delete listing with its key")
# def change_status(user: AUTH_ME, db: db_conn, listing_key: str):
#     try:
#         listing = db.scalar(select(Listing).where(Listing.key == listing_key, Listing.user_id == user.id))
#         if not listing:
#             raise HTTPException(status_code=404, detail="Listing not found")

#         # listing is not deleted, but just status changes to deletd
#         db.execute(update(Listing).where(Listing.id == listing.id).values(status=ListingStatus.deleted, updated_at=func.now()))
#         db.commit()

#         return {"success": True, "message": "Listing deleted successfully"}

#     except Exception as e:
#         print(e)
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Failed to delete the listing") from e


# @router.post("/info/{listing_key}", response_model=ListingInfo, description="Fetches listing info")
# def fetch_listings(user: AUTH_ME, db: db_conn, listing_key: str):
#     try:
#         listing = db.scalar(select(Listing).where(Listing.key == listing_key, Listing.user_id == user.id))
#         if not listing:
#             raise HTTPException(status_code=404, detail="Listing not found")

#         listing_images = db.scalars(select(ListingImage).where(ListingImage.listing_id == listing.id))

#         return ListingInfo.from_db_models(listing, listing_images)

#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Failed to fetch listing info") from e
