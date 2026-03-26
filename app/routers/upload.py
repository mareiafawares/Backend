import os
import time
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from app.core.oauth2 import get_current_user

router = APIRouter(tags=["Upload"])

UPLOAD_DIR = "static/uploads/images"
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def _allowed_file(content_type: Optional[str]) -> bool:
    return content_type in ALLOWED_CONTENT_TYPES if content_type else False


def _safe_ext(content_type: str) -> str:
    m = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif", "image/webp": ".webp"}
    return m.get(content_type, ".jpg")


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    """
    Upload an image file. Returns a URL path to the stored image.
    Use with: Authorization: Bearer <token>
    """
    if not _allowed_file(file.content_type):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Allowed: JPEG, PNG, GIF, WebP",
        )
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = _safe_ext(file.content_type or "image/jpeg")
    name = f"{uuid.uuid4().hex}_{int(time.time() * 1000)}{ext}"
    path = os.path.join(UPLOAD_DIR, name).replace("\\", "/")
    try:
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  
            raise HTTPException(status_code=400, detail="File too large (max 10 MB)")
        with open(path, "wb") as f:
            f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to save file")
    url = f"/static/uploads/images/{name}"
    return {"url": url}
