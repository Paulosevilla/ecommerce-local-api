
# E-commerce Local API

Aplicación de referencia para el proyecto: **App móvil de comercio electrónico para productos locales**.

## Ejecutar localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Endpoints clave:
- `GET /health`
- `POST /users/` `GET /users/` `PUT /users/{id}` `POST /users/{id}/addresses`
- `POST /products/` `GET /products/` `GET /products/{id}` `PUT /products/{id}`

## Pruebas
```bash
pytest -q
```

## Tecnologías
- FastAPI, Pydantic, Uvicorn, Pytest
- GitHub Actions: Lint + Tests + Build

## Licencia
MIT
