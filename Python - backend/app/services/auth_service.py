from passlib.context import CryptContext
from models.user import User, UserCreate
from motor.motor_asyncio import AsyncIOMotorDatabase
# ma hoa mat khau an toan
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# cac ham chinh 
# nhan mat khau tho -> tra ve chuoi da duoc hash ma hoa
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
# so sanh mat khau cua nguoi dung voi hash trong Db -> true / false
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_user(db: AsyncIOMotorDatabase, user: UserCreate):
    # kiem tra email co ton tai
    existing = await db.users.find_one({"email": user.email})
    if existing:
        return None
    #chuyen obj user thanh dict
    user_dict = user.dict()
    user_dict["hashed_password"] = hash_password(user_dict.pop("password"))
    result = await db.users.insert_one(user_dict)
    return str(result.inserted_id)

async def authenticate_user(db: AsyncIOMotorDatabase, email: str, password: str):
    user = await db.users.find_one({"email": email})
    if not user:
        return None # khong tim thay email
    
    if not verify_password(password, user["hashed_password"]):
        return None # sai mat khau
    return user # dang thanh cong 
    