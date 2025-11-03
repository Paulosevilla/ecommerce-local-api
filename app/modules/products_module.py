
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, Field, PositiveInt, condecimal
from uuid import uuid4, UUID
from decimal import Decimal

# --- Domain Models ---

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    description: Optional[str] = Field(None, max_length=500)
    price: condecimal(max_digits=12, decimal_places=2) = Field(..., gt=0)
    stock: PositiveInt = Field(..., description="Unidades disponibles")
    category: str = Field(..., min_length=2, max_length=50)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=80)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[condecimal(max_digits=12, decimal_places=2)] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    active: Optional[bool] = None

class Product(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    price: Decimal
    stock: int
    category: str
    active: bool = True
    images: List[str] = []

# --- Repository ---

class IProductRepository:
    def add(self, p: Product) -> Product: ...
    def get(self, pid: UUID) -> Optional[Product]: ...
    def list(self) -> List[Product]: ...
    def search(self, q: Optional[str], category: Optional[str]) -> List[Product]: ...
    def update(self, pid: UUID, p: Product) -> Product: ...
    def remove(self, pid: UUID) -> None: ...

class InMemoryProductRepository(IProductRepository):
    def __init__(self) -> None:
        self._db: Dict[UUID, Product] = {}

    def add(self, p: Product) -> Product:
        self._db[p.id] = p
        return p

    def get(self, pid: UUID) -> Optional[Product]:
        return self._db.get(pid)

    def list(self) -> List[Product]:
        return list(self._db.values())

    def search(self, q: Optional[str], category: Optional[str]) -> List[Product]:
        results = self.list()
        if q:
            results = [p for p in results if q.lower() in p.name.lower() or (p.description or "").lower().find(q.lower()) != -1]
        if category:
            results = [p for p in results if p.category.lower() == category.lower()]
        return results

    def update(self, pid: UUID, p: Product) -> Product:
        if pid not in self._db:
            raise KeyError("Product not found")
        self._db[pid] = p
        return p

    def remove(self, pid: UUID) -> None:
        if pid not in self._db:
            raise KeyError("Product not found")
        del self._db[pid]

# --- Service Layer ---

class ProductService:
    def __init__(self, repo: IProductRepository) -> None:
        self.repo = repo

    def create(self, payload: ProductCreate) -> Product:
        p = Product(id=uuid4(),
                    name=payload.name,
                    description=payload.description,
                    price=Decimal(payload.price),
                    stock=payload.stock,
                    category=payload.category,
                    active=True,
                    images=[])
        return self.repo.add(p)

    def list(self) -> List[Product]:
        return self.repo.list()

    def search(self, q: Optional[str], category: Optional[str]) -> List[Product]:
        return self.repo.search(q, category)

    def get(self, pid: UUID) -> Product:
        p = self.repo.get(pid)
        if not p:
            raise LookupError("product_not_found")
        return p

    def update(self, pid: UUID, changes: ProductUpdate) -> Product:
        p = self.get(pid)
        updated = p.copy(update={
            "name": changes.name if changes.name is not None else p.name,
            "description": changes.description if changes.description is not None else p.description,
            "price": Decimal(changes.price) if changes.price is not None else p.price,
            "stock": changes.stock if changes.stock is not None else p.stock,
            "category": changes.category if changes.category is not None else p.category,
            "active": changes.active if changes.active is not None else p.active,
        })
        return self.repo.update(pid, updated)

    def add_stock(self, pid: UUID, amount: int) -> Product:
        if amount <= 0:
            raise ValueError("amount_must_be_positive")
        p = self.get(pid)
        updated = p.copy(update={"stock": p.stock + amount})
        return self.repo.update(pid, updated)

    def remove(self, pid: UUID) -> None:
        self.repo.remove(pid)

# --- Dependency wiring ---

_repo_singleton = InMemoryProductRepository()
_service_singleton = ProductService(_repo_singleton)

def get_service() -> ProductService:
    return _service_singleton

# --- API Router ---

router = APIRouter()

@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, svc: ProductService = Depends(get_service)):
    return svc.create(payload)

@router.get("/", response_model=List[Product])
def list_or_search_products(q: Optional[str] = Query(None), category: Optional[str] = Query(None), svc: ProductService = Depends(get_service)):
    if q or category:
        return svc.search(q, category)
    return svc.list()

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: UUID, svc: ProductService = Depends(get_service)):
    try:
        return svc.get(product_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: UUID, changes: ProductUpdate, svc: ProductService = Depends(get_service)):
    try:
        return svc.update(product_id, changes)
    except LookupError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.post("/{product_id}/stock/{amount}", response_model=Product)
def add_stock(product_id: UUID, amount: int, svc: ProductService = Depends(get_service)):
    try:
        return svc.add_stock(product_id, amount)
    except LookupError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: UUID, svc: ProductService = Depends(get_service)):
    try:
        svc.remove(product_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None
