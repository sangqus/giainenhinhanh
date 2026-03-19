from jose import JWTError, jwt # thu vien hao token
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "khóa bí mật của bạn" # doi tuong production
ALGORITHM = "HS256" # kiem tra token
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # thoi gian token

# ham duoc goi khi nguoi dung ddang nhap thanh cong server tao the bai token cho nguoi ddung
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()# tao ban sao du lieu
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None