from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import UserCreate, UserLogin, Token, UserResponse
from app.services.auth_service import auth_service
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Đăng ký tài khoản mới"""
    try:
        new_user = await auth_service.create_user(user)
        return UserResponse(
            id=str(new_user["_id"]),
            email=new_user["email"],
            full_name=new_user["full_name"],
            is_active=new_user["is_active"],
            created_at=new_user["created_at"]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Đăng nhập"""
    user = await auth_service.authenticate_user(
        user_credentials.email,
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tokens = auth_service.create_tokens(user["email"])
    return tokens

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Lấy thông tin user hiện tại"""
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        full_name=current_user["full_name"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"]
    )