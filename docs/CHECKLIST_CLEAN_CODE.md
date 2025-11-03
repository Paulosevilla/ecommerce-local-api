
# Checklist de Buenas Prácticas (aplicadas)

- [x] Nomenclatura clara y consistente (snake_case para variables, PascalCase para clases).
- [x] Funciones cortas y con responsabilidad única.
- [x] Validación de entrada mediante modelos Pydantic.
- [x] Manejo de errores con excepciones de dominio y HTTP apropiadas.
- [x] DRY: lógica centralizada en servicios y repositorios (sin duplicación en routers).
- [x] Separación de capas (modelo, repositorio, servicio, API) por módulo.
- [x] Tests automáticos para flujos clave (crear/consultar usuarios; CRUD de productos).
- [x] .gitignore para artefactos temporales.
- [x] CI: lint + tests + build en GitHub Actions.
