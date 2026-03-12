from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import connection, models
from schemas import user_schemas

# ملاحظة: حذفنا الـ prefix من هنا لأننا أضفناه في main.py
router = APIRouter(tags=["Admin Management"])

# 1. جلب كل المستخدمين (لصفحة Manage Users)
# الرابط سيصبح: GET /admin/users
@router.get("/users", response_model=List[user_schemas.UserOut])
def get_all_users(db: Session = Depends(connection.get_db)):
    users = db.query(models.User).all()
    return users

# 2. جلب طلبات المتاجر المعلقة
# الرابط سيصبح: GET /admin/shop-requests
@router.get("/shop-requests", response_model=List[user_schemas.UserOut])
def get_pending_shops(db: Session = Depends(connection.get_db)):
    # جلب المستخدمين الذين لديهم طلب متجر ولم يتم قبولهم بعد
    requests = db.query(models.User).filter(
        models.User.has_shop_request == True,
        models.User.is_approved == False
    ).all()
    return requests

# 3. قبول أو رفض طلب المتجر
# الرابط سيصبح: PUT /admin/approve-shop/{user_id}
@router.put("/approve-shop/{user_id}")
def approve_shop(user_id: int, approve: bool, db: Session = Depends(connection.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if approve:
        user.is_approved = True
        user.has_shop_request = False # نغلق الطلب لأنه تمت الموافقة
    else:
        user.is_approved = False
        user.has_shop_request = False # نرفض الطلب
        user.shop_name = None # اختيارياً: مسح الاسم المرفوض
    
    db.commit()
    return {"message": "Shop status updated successfully", "approved": approve}

# 4. حذف مستخدم
# الرابط سيصبح: DELETE /admin/users/{user_id}
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(connection.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}