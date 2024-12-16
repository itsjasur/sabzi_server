import os
from pathlib import Path
import secrets
import shutil
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
import filetype
from sqlalchemy import delete, func, select, update
from app.core.database import DB
from app.core.utils.auth import AUTH_ME
from app.models.item import Item, ItemImage
from app.schemas.item import ItemAddRequest, ItemUpdateRequest


router = APIRouter()

# creates the assets directory if it doesn't exist
STORAGE_PATH = Path("assets/item_assets")

# max file size (10MB)
MAX_ITEM_IMAGE_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
MAX_IMAGES_PER_ITEM = 10


def save_item_images(file: UploadFile) -> list[str, str]:
    # Read first 8192 bytes for filetype detection
    first_chunk = file.file.read(8192)
    file.file.seek(0)  # Reset file pointer

    # Detect file type using filetype
    kind = filetype.guess(first_chunk)

    if not kind:
        raise HTTPException(status_code=400, detail="Could not determine file type")

    # Validate if it's an image and check allowed types
    allowed_mimes = {"image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"], "image/webp": [".webp"]}

    if kind.mime not in allowed_mimes:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {kind.mime}. Allowed types: JPEG, PNG, WEBP")

    # Check file size
    file.file.seek(0, 2)
    if file.file.tell() > MAX_ITEM_IMAGE_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    file.file.seek(0)

    # Generate file key and validate extension
    file_key = secrets.token_hex(16)
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in [ext for exts in allowed_mimes.values() for ext in exts]:
        raise HTTPException(status_code=400, detail="Invalid file extension")

    # save file
    file_path = Path(f"{STORAGE_PATH}/{file_key}{file_extension}")

    # make the dir if not available
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file.file as source_file:
        with file_path.open("wb") as destination_file:
            shutil.copyfileobj(source_file, destination_file)

    return file_key, file_extension


def remove_item_images(image_key: str, image_extension) -> None:
    """removes the entire directory for an item_key and all its contents."""
    file_path = f"{STORAGE_PATH}/{image_key}{image_extension}"
    try:
        os.remove(file_path)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove image: {str(e)}") from e


@router.post("/add-image", description="Adds new item image")
def add_image(user: AUTH_ME, db: DB, image: UploadFile = File(default=None)):
    """
    - images are saved and registered in db
    - temporary files will be removed if item_id is empty after 24 hours
    """
    file_key = None
    file_extension = None

    try:
        file_key, file_extension = save_item_images(image)
        item_image = ItemImage(
            item_id=None,
            key=file_key,
            extension=file_extension,
            storage_path=STORAGE_PATH,
        )

        db.add(item_image)
        db.commit()

    except Exception as e:
        db.rollback()
        if file_key is not None and file_extension is not None:
            remove_item_images(file_key, file_extension)
        raise HTTPException(status_code=500, detail=f"Failed to add image") from e


@router.post("/remove-image", description="Removes an item image")
def remove_image(
    user: AUTH_ME,
    db: DB,
    image_key: str = Form(...),
    image: UploadFile = File(default=None),
):

    try:
        item = db.scalar(select(ItemImage).where(ItemImage.key == image_key, Item.user_id == user.id))
        if not item:
            raise HTTPException(status_code=404, detail="Item image not found")

        db.execute(delete(ItemImage).where(ItemImage.key == image_key))
        remove_item_images(image + item.extension)

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to remove image") from e


@router.post("/add-item", description="Adds new item")
def add_item(user: AUTH_ME, db: DB, data: ItemAddRequest):
    item_key = secrets.token_hex(16)
    try:
        item = Item(
            user_id=user.id,
            key=item_key,
            price=data.price,
            price_negotiable=data.price_negotiable,
            category_id=data.category_id,
            title=data.title,
            description=data.description,
            latitude=data.latitude,
            longitude=data.longitude,
        )

        db.add(item)
        db.flush()  # gets ID without committing

        if data.image_keys:  # Protect against None
            stmt = update(ItemImage).where(ItemImage.key.in_(data.image_keys)).values(item_id=item.id)
            db.execute(stmt)

        db.commit()
        return {"success": True, "message": "Item added successfully", "item_id": item.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add item") from e


@router.post("/update-item", description="Update item info")
def update_item(user: AUTH_ME, db: DB, data: ItemUpdateRequest):
    try:
        # check if item is available and belongs to this user
        item = db.scalar(select(Item).where(Item.key == data.item_key, Item.user_id == user.id))
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        db.execute(
            update(Item)
            .where(Item.id == item.id)
            .values(
                price=data.price,
                price_negotiable=data.price_negotiable,
                category_id=data.category_id,
                title=data.title,
                description=data.description,
                updated_at=func.now(),
            )
        )

        # clean up item_ids from ItemImages
        db.execute(update(ItemImage).where(ItemImage.item_id == item.id).values(item_id=None))

        if data.image_keys:  # protects against None
            stmt = update(ItemImage).where(ItemImage.key.in_(data.image_keys)).values(item_id=item.id)
            db.execute(stmt)

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update item") from e
