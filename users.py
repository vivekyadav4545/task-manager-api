from fastapi import APIRouter , Depends , status , HTTPException ,Request
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm
from sqlalchemy.orm import session
from slowapi import Limiter
from slowapi.util import get_remote_address
from limiter import limiter


from database import get_db 
import models 
import schemas
import auth

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/signup" , response_model=schemas.UserResponse , status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def signup(request: Request, user :schemas.UserCreate , db : session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user :
        raise HTTPException(status_code=400 , detail="Email is already registerd")
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email= user.email , hashed_password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model= schemas.Token)
@limiter.limit("5/minute")
def login(request: Request, form_data : OAuth2PasswordRequestForm = Depends() , db : session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password , user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate":"Bearer"}
        )

    access_token = auth.create_access_token(data = {"sub": user.email})
    return {"access_token": access_token , "token_type":"bearer"}

def get_current_user(token:str = Depends(oauth2_scheme) , db :session = Depends(get_db))->models.User :
    credentail_exceptions = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )

    payload = auth.decode_access_token(token)
    if payload is None:
        raise credentail_exceptions
    
    email:str = payload.get("sub")

    if email is None:
        raise credentail_exceptions

    user = db.query(models.User).filter(models.User.email == email).first()

    if user.email is None:
        raise credentail_exceptions

    return user
    
