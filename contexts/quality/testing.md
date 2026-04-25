---
context: quality
name: Testing
description: TDD, cobertura >80%, fixtures reutilizables, no mocks de BD
---

## Contexto de Testing

### Filosofía
- Tests que fallan primero (TDD) cuando sea práctico
- Tests de integración sobre mocks siempre que sea posible
- No mockear la base de datos: usar BD de test real o SQLite en memoria
- Un test por comportamiento, no por función

### Estructura
```
tests/
├── conftest.py          ← fixtures compartidas
├── test_<dominio>.py    ← tests por dominio
└── integration/         ← tests E2E (si aplica)
```

### Fixtures
- Usar `pytest.fixture` con scope apropiado
- `scope="session"` para recursos costosos (BD, servidor)
- Datos de test en `tests/fixtures/` — no inline en tests

### Cobertura
- Mínimo 80% de líneas
- 100% en lógica de negocio crítica (auth, pagos, permisos)
- Reportar con `pytest --cov=src --cov-report=html`

### Prohibido
- Tests que dependen del orden de ejecución
- `time.sleep()` en tests (usar mocks de tiempo)
- Tests que tocan filesystem de producción
