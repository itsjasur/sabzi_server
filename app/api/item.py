import shutil
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
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


router = APIRouter()


async def save_image(file: UploadFile, upload_dir: Path) -> tuple[str, str]:
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

    # Try-except needed here as this is file system operation, not DB
    try:
        file_path = upload_dir / f"{file_key}{file_extension}"
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    return file_key, file_extension


@router.post("/add-item", status_code=status.HTTP_201_CREATED)
async def add_item(
    user: AUTH_ME,
    db: DB,
    files: list[UploadFile] = File(...),
    price: float = Form(...),
    price_negotiable: bool = Form(...),
    category_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one image required")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")

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

    for file in files:
        try:
            file_key, file_extension = await save_image(file, UPLOAD_DIR)

            item_image = ItemImage(
                item_id=item.id,
                key=file_key,
                extension=file_extension,
                source=core_settings.item_image_upload_source,
                bucket_path="assets/item_images",
            )
            db.add(item_image)
        finally:
            file.file.close()

    db.commit()
    return {"success": True, "item_id": item.id}


class ItemUpdateInfo(BaseModel):
    item_id: int
    price: float = Field(..., gt=0)
    price_negotiable: bool
    status: ItemStatus
    category_id: int
    title: str = Field(..., min_length=1, max_length=256)
    description: str = Field(None, min_length=1, max_length=1024)


@router.post("/update-item")
async def update_item(user: AUTH_ME, db: DB, data: ItemUpdateInfo):
    item = db.query(Item).filter(Item.id == data.item_id, Item.user_id == user.id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in data.model_dump(exclude={"item_id"}).items():
        setattr(item, key, value)

    db.commit()
    return {"success": True, "message": "Item updated successfully"}


class ImageDelete(BaseModel):
    item_id: int
    image_key: str


@router.post("/delete-image")
async def delete_image(user: AUTH_ME, db: DB, data: ImageDelete):
    item = db.query(Item).filter(Item.id == data.item_id, Item.user_id == user.id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    image_count = db.query(ItemImage).filter(ItemImage.item_id == data.item_id).count()
    if image_count <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete last image")

    image = db.query(ItemImage).filter(ItemImage.key == data.image_key, ItemImage.item_id == data.item_id).first()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Try-except needed here as this is file system operation, not DB
    try:
        file_path = UPLOAD_DIR / f"{data.image_key}{image.extension}"
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

    db.delete(image)
    db.commit()
    return {"success": True, "message": "Image deleted successfully"}


@router.post("/add-image")
async def add_image(user: AUTH_ME, db: DB, file: UploadFile = File(...), item_id: int = Form(...)):
    item = db.query(Item).filter(Item.id == item_id, Item.user_id == user.id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    image_count = db.query(ItemImage).filter(ItemImage.item_id == item_id).count()
    if image_count >= 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images reached")

    file_key, file_extension = await save_image(file, UPLOAD_DIR)

    item_image = ItemImage(
        item_id=item_id, key=file_key, extension=file_extension, source=core_settings.item_image_upload_source, bucket_path="assets/item_images"
    )

    db.add(item_image)
    db.commit()

    return {"success": True, "message": "Image added successfully", "image_key": file_key}
