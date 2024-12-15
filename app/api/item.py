import shutil
from typing import Annotated, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import delete, select, update
from app.core.database import DB
from app.core.utils.auth import AUTH_ME
from app.models.item import Item, ItemImage
import secrets
from app.core.config import core_settings
from pathlib import Path


router = APIRouter()

# creates the assets directory if it doesn't exist
UPLOAD_DIR = Path("assets/item_assets")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# max file size (10MB)
MAX_ITEM_IMAGE_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
MAX_IMAGES_PER_ITEM = 10


def save_item_images(item_key: str, file: UploadFile, upload_dir: Path) -> tuple[str, str]:
    """Saves the image and returns file key and extension."""
    # validate_image(file)

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file.file.seek(0, 2)  # moves to end of file, to check file size without loading it to memory
    if file.file.tell() > MAX_ITEM_IMAGE_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    file.file.seek(0)  # resets file pointer to beginning

    file_key = secrets.token_hex(16)
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    #  full directory path for the item
    item_dir = upload_dir / item_key
    try:
        #  directory and any necessary parent directories
        item_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to create directory: {str(e)}") from e

    # full file path
    file_path = item_dir / f"{file_key}{file_extension}"

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}") from e

    return file_key, file_extension


def remove_item_images_directory(item_key: str, upload_dir: Path) -> None:
    """Removes the entire directory for an item_key and all its contents."""
    item_dir = upload_dir / item_key
    if not item_dir.exists():
        raise HTTPException(status_code=404, detail=f"Directory for item '{item_key}' not found")
    try:
        # shutil.rmtree to remove directory and all its contents
        shutil.rmtree(item_dir)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove directory: {str(e)}") from e


@router.post("/add-item", status_code=status.HTTP_201_CREATED, description="Adds new item")
def add_item(
    user: AUTH_ME,
    db: DB,
    # files: Optional[list[UploadFile]] = File(default=[]),
    files: Optional[list[UploadFile]] = File(default=None),
    price: float = Form(..., gt=0),
    price_negotiable: bool = Form(...),
    category_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
):

    # if files is None:
    #     files = []

    files = files or []

    if len(files) > MAX_IMAGES_PER_ITEM:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_IMAGES_PER_ITEM} images allowed")

    item_key = None
    try:
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

        item_key = item.key

        uploaded_files = []
        for file in files:
            file_key = secrets.token_hex(16)
            file_key, file_extension = save_item_images(item.key, file, UPLOAD_DIR)
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

        db.commit()
        return {"success": True, "item_id": item.id}

    # if any upload fails, deletes all previously uploaded files and rolls back db changes
    except Exception as e:
        db.rollback()
        if item_key is not None:
            remove_item_images_directory(item_key, UPLOAD_DIR)
        raise
