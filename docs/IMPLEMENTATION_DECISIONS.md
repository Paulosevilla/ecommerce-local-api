
# Decisiones de diseño e implementación

- **Arquitectura**: API REST con FastAPI; módulos desacoplados (usuarios, productos) con capas: modelo → repositorio → servicio → router.
- **Clean Code**: responsabilidades únicas, nombres significativos, funciones cortas, validaciones en capa de servicio, manejo explícito de errores.
- **Repositorios in-memory**: simplifican la ejecución y pruebas; se podría sustituir por ORM (SQLAlchemy) sin cambiar la capa de servicio.
- **Validaciones**: Pydantic (tipos, rangos, formatos).
- **Errores**: se propagan como `HTTPException` con códigos consistentes (404, 409, 400).
- **Pruebas**: `pytest` con `TestClient` de FastAPI para endpoints críticos.
- **CI/CD**: GitHub Actions ejecuta lint, pruebas y compilación bytecode.
