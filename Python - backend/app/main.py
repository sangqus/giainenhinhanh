from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI(title = "photo Editor API")
# frontend nay goi API khong bi chan
app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials= True,
    allow_methods= ["*"],
    allow_headers= ["*"],
)

# ket noi voi mongodb
MONGODB_URL = os.getenv("MONGODB_URl"," co so du lieu dang lam")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.photo_editor_db # database photo_editor_db 
#db.users va db.photos

# app khoi dong 
@app.on_event("Bắt đầu")
async def startup_db():
    print("Đã kết nối với Mongodb")

# app tắt
@app.on_event("Thoát ra")
async def shutdown_db():
    client.close() # tránh leak tai nguyen

# API test gốc /
@app.get("/")
async def root():
    return{"Thông báo","API trình chỉnh sửa ảnh đang chạy"}
# dung de test http

# import routes 
from routes import auth, photos 
app.include_routes(auth.router , prefix="/api/auth", tags=["Authentication"])
app.include_routes(photos.routes, prefix="/api/photos", tags=["Photos"])