import shutil
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, select, update
from app.core.database import DB
from app.core.utils.auth import AUTH_ME
from app.models.item import Item, ItemImage, ItemStatus
import secrets
from app.core.config import core_settings

router = APIRouter()

# creates the assets directory if it doesn't exist
UPLOAD_DIR = Path("assets/item_assets")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# max file size (10MB)
MAX_ITEM_IMAGE_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
MAX_IMAGES_PER_ITEM = 10


router = APIRouter()


def save_image(file: UploadFile, upload_dir: Path) -> tuple[str, str]:
    """Helper function to save image file and return key and extension"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file.file.seek(0, 2)
    if file.file.tell() > MAX_ITEM_IMAGE_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    file.file.seek(0)

    file_key = secrets.token_hex(16)
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    try:
        file_path = upload_dir / f"{file_key}{file_extension}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    return file_key, file_extension


def remove_image(key: str, extension: str):
    try:
        file_path = UPLOAD_DIR / f"{key}{extension}"
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


@router.post("/add-item", status_code=status.HTTP_201_CREATED, description="Adds new item")
def add_item(
    user: AUTH_ME,
    db: DB,
    files: Optional[list[UploadFile]] = File(None),
    price: float = Form(...),
    price_negotiable: bool = Form(...),
    category_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
):

    if len(files) > MAX_IMAGES_PER_ITEM:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_IMAGES_PER_ITEM} images allowed")

    # first try to upload all images to remote storage
    uploaded_files = []
    try:
        for file in files:
            file_key = secrets.token_hex(16)
            file_key, file_extension = save_image(file, UPLOAD_DIR)
            uploaded_files.append((file_key, file_extension))

        item = Item(
            user_id=user.id,
            key=secrets.token_hex(16),
            price=price,
            price_negotiable=price_negotiable,
            category_id=category_id,
            title=title,
            description=description,
            latitude=latitude,
            longitude=longitude,
        )

        db.add(item)
        db.flush()  # gets ID without committing

        for file_key, file_extension in uploaded_files:
            item_image = ItemImage(
                item_id=item.id,
                key=file_key,
                extension=file_extension,
                source=core_settings.item_image_upload_source,
                bucket_path="assets/item_images",
            )
            db.add(item_image)

        db.commit()
        return {"success": True, "item_id": item.id}

    # if any upload fails, deletes all previously uploaded files and rolls back db changes
    except Exception as e:
        db.rollback()
        for file_key, file_extension in uploaded_files:
            try:
                remove_image(file_key, file_extension)
            except Exception:
                pass  # if remove failes just move to next iteration
        raise


@router.post("/update-item", response_model=dict, status_code=status.HTTP_201_CREATED, description="Updates avl item")
def update_item(
    db: DB,
    item_key: str = Form(...),
    files: Optional[list[UploadFile]] = File(None),
    price: float = Form(...),
    price_negotiable: bool = Form(...),
    category_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
):

    try:

        item = db.scalar(select(Item).where(Item.key == item_key))

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        # finds all current images and delete them before removing from db
        item_images: list[ItemImage] = db.query(ItemImage).filter(ItemImage.item_id == item.id).all()
        image_ids: list[int] = []
        # deletes images from storage before deleting from db
        for item_image in item_images:
            image_ids.append(item_image.id)
            remove_image(item_image.key, item_image.extension)

        db.execute(delete(ItemImage).where(ItemImage.id.in_(image_ids)))
        db.commit()

        uploaded_files = []
        if files and len(files) > 0:
            for file in files:
                file_key = secrets.token_hex(16)
                file_key, file_extension = save_image(file, UPLOAD_DIR)
                uploaded_files.append((file_key, file_extension))

            for file_key, file_extension in uploaded_files:
                item_image = ItemImage(
                    item_id=item.id,
                    key=file_key,
                    extension=file_extension,
                    source=core_settings.item_image_upload_source,
                    bucket_path="assets/item_images",
                )
                db.add(item_image)

        db.execute(
            update(Item)
            .where(Item.id == item.id)
            .values(
                price=price,
                price_negotiable=price_negotiable,
                category_id=category_id,
                title=title,
                description=description,
            )
        )

        db.commit()
        return {
            "success": True,
            "details": "Item updated successfully",
        }

    except Exception as e:
        db.rollback()
        raise
