import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.staticfiles import StaticFiles
from app.core.database import DB
from app.core.utils.auth import AUTH_ME
from app.models.item import Item, ItemImage, ItemStatus
from app.models.user import User
import secrets
from app.core.config import core_settings

router = APIRouter()

# creates the assets directory if it doesn't exist
UPLOAD_DIR = Path("assets/item_assets")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# max file size (10MB)
MAX_ITEM_IMAGE_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


# @router.post("/upload-image", response_model=dict, status_code=status.HTTP_200_OK)
# # async def upload_image(user: AUTH_ME, file: UploadFile = File(...)):


def upload_image_to_db(db: DB, item_id: int, file: UploadFile = File(...)) -> ItemImage:
    # validates file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

    # check file size
    file.file.seek(0, 2)  # seeks to end of file
    file_size = file.file.tell()  # gets current position (file size)
    file.file.seek(0)  # resets file position

    if file_size > MAX_ITEM_IMAGE_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum size is 10MB",
        )

    try:
        # generates secure unique filename
        file_key = secrets.token_hex(16)
        file_extension = Path(file.filename).suffix.lower()  # normalizes extension

        # validates extension
        if file_extension not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Supported types: JPG, PNG, GIF, WebP",
            )

        # PATH creates path
        file_path = Path(f"{UPLOAD_DIR}/{file_key}{file_extension}")

        # save the file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # add new item image in db
        item_image = ItemImage(
            item_id=item_id,
            key=file_key,
            source=core_settings.item_image_upload_source,
            extension=file_extension,
            bucket_path="assets/item_images",
        )

        db.add(item_image)
        db.commit()
        db.refresh(item_image)

        # item_image_url = f"{core_settings.server_host}/{item_image.bucket_path}{item_image.extension}"
        return item_image

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}",
        )
    finally:
        file.file.close()  #  ensure file is closed


@router.post("/remove-image", response_model=dict, status_code=status.HTTP_200_OK)
async def remove_image(db: DB, image_key: str):
    """removes image from filesystem and database"""

    try:
        # finds the image record
        image = db.query(ItemImage).filter(ItemImage.key == image_key).first()

        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

        # get the file path
        file_path = Path(UPLOAD_DIR) / f"{image_key}{image.extension}"

        # deletes the physical file if it exists
        if file_path.exists():
            file_path.unlink()

        # deletes the database record
        db.delete(image)
        db.commit()

        return {"success": True, "message": "Image successfully removed", "key": image_key}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing image: {str(e)}",
        )


@router.post("/add-or-update", response_model=dict, status_code=status.HTTP_200_OK)
async def add_new_item(
    user: AUTH_ME,
    db: DB,
    files: list[UploadFile] = File(..., description="Item images"),
    item_id: int = Form(None, description="Optional item ID"),
    price: float = Form(..., description="Price of the item"),
    price_negotiable: bool = Form(..., description="Is it negotiable?"),
    category_id: bool = Form(..., description="Selected category id"),
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
):

    item_key = secrets.token_hex(16)

    # if id is unavailable, create new item
    if not item_id:
        item = Item(
            user_id=user.id,
            key=item_key,
            price=price,
            price_negotiable=price_negotiable,
            # status=ItemStatus.active, # used to update status
            category_id=category_id,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
        )

        db.add(item)
        db.commit()
        db.refresh()
        item_id = item.id

        if not item_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't add a new item")

        for file in files:
            upload_image_to_db(db=db, file=file, item_id=item_id)

    # Your processing logic here
    return {}
