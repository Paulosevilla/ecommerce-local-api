
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4, UUID

# --- Domain Models ---

class Address(BaseModel):
    street: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=64)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=60)
    addresses: Optional[List[Address]] = None

class User(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    addresses: List[Address] = []
    is_active: bool = True

# --- Repository (in-memory demo) ---

class IUserRepository:
    def add(self, user: User) -> User: ...
    def get(self, user_id: UUID) -> Optional[User]: ...
    def get_by_email(self, email: str) -> Optional[User]: ...
    def list(self) -> List[User]: ...
    def update(self, user_id: UUID, user: User) -> User: ...
    def deactivate(self, user_id: UUID) -> None: ...

class InMemoryUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._db: Dict[UUID, User] = {}

    def add(self, user: User) -> User:
        self._db[user.id] = user
        return user

    def get(self, user_id: UUID) -> Optional[User]:
        return self._db.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        for u in self._db.values():
            if u.email == email:
                return u
        return None

    def list(self) -> List[User]:
        return list(self._db.values())

    def update(self, user_id: UUID, user: User) -> User:
        if user_id not in self._db:
            raise KeyError("User not found")
        self._db[user_id] = user
        return user

    def deactivate(self, user_id: UUID) -> None:
        if user_id not in self._db:
            raise KeyError("User not found")
        u = self._db[user_id]
        u.is_active = False
        self._db[user_id] = u

# --- Service Layer ---

class UserService:
    def __init__(self, repo: IUserRepository) -> None:
        self.repo = repo

    def _ensure_unique_email(self, email: str) -> None:
        if self.repo.get_by_email(email):
            raise ValueError("email_already_exists")

    def create_user(self, payload: UserCreate) -> User:
        self._ensure_unique_email(payload.email)
        # NOTE: hash omitted for demo; in production use passlib/bcrypt
        user = User(id=uuid4(), name=payload.name, email=payload.email, addresses=[])
        return self.repo.add(user)

    def list_users(self) -> List[User]:
        return self.repo.list()

    def get_user(self, user_id: UUID) -> User:
        user = self.repo.get(user_id)
        if not user:
            raise LookupError("user_not_found")
        return user

    def update_user(self, user_id: UUID, changes: UserUpdate) -> User:
        user = self.get_user(user_id)
        updated = user.copy(update={
            "name": changes.name if changes.name is not None else user.name,
            "addresses": changes.addresses if changes.addresses is not None else user.addresses,
        })
        return self.repo.update(user_id, updated)

    def add_address(self, user_id: UUID, address: Address) -> User:
        user = self.get_user(user_id)
        updated = user.copy(update={"addresses": user.addresses + [address]})
        return self.repo.update(user_id, updated)

    def deactivate(self, user_id: UUID) -> None:
        self.repo.deactivate(user_id)

# --- Dependency wiring ---

_repo_singleton = InMemoryUserRepository()
_service_singleton = UserService(_repo_singleton)

def get_service() -> UserService:
    return _service_singleton

# --- API Router ---

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(payload: UserCreate, svc: UserService = Depends(get_service)):
    try:
        return svc.create_user(payload)
    except ValueError as ve:
        if str(ve) == "email_already_exists":
            raise HTTPException(status_code=409, detail="Email ya registrado")
        raise

@router.get("/", response_model=List[User])
def list_users_endpoint(svc: UserService = Depends(get_service)):
    return svc.list_users()

@router.get("/{user_id}", response_model=User)
def get_user_endpoint(user_id: UUID, svc: UserService = Depends(get_service)):
    try:
        return svc.get_user(user_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.put("/{user_id}", response_model=User)
def update_user_endpoint(user_id: UUID, changes: UserUpdate, svc: UserService = Depends(get_service)):
    try:
        return svc.update_user(user_id, changes)
    except LookupError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.post("/{user_id}/addresses", response_model=User)
def add_address_endpoint(user_id: UUID, address: Address, svc: UserService = Depends(get_service)):
    try:
        return svc.add_address(user_id, address)
    except LookupError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.delete("/{user_id}", status_code=204)
def deactivate_user_endpoint(user_id: UUID, svc: UserService = Depends(get_service)):
    try:
        svc.deactivate(user_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return None
