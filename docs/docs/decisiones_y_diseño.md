# Decisiones de Diseño e Implementación

## 1. Estructura del Proyecto
El sistema sigue una arquitectura modular basada en FastAPI:
- `/app/` contiene los módulos de negocio (`users`, `products`).
- `/tests/` implementa pruebas unitarias automáticas.
- `/docs/` almacena documentación y decisiones de diseño.
- `.github/workflows/` contiene los archivos YAML para CI/CD.

## 2. Buenas Prácticas Aplicadas
- Nomenclatura clara y consistente.
- Separación de responsabilidades en funciones.
- Manejo de errores con `try/except` y respuestas HTTP adecuadas.
- No duplicación de código (principio DRY).
- Uso de tipado con anotaciones de tipo (`str`, `int`, `List`, etc.).

## 3. Decisiones Técnicas
- Se eligió **FastAPI** por su rendimiento y documentación OpenAPI automática.
- Se aplicó **flake8** para linting y verificación de estilo.
- Se usó **pytest** para automatizar pruebas.
- Se implementó **CI/CD** con GitHub Actions para validación automática.

## 4. Conclusión
La implementación cumple con los criterios de la Parte IV, integrando buenas prácticas de desarrollo, control de versiones y automatización continua.
