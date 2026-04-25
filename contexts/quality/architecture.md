---
context: quality
name: Arquitectura
description: SOLID, Clean Architecture, ADRs, bajo acoplamiento
---

## Contexto de Arquitectura

### Principios activos
- **SRP**: cada clase/módulo tiene una responsabilidad
- **OCP**: extensible sin modificar código existente cuando sea práctico
- **DIP**: dependencias hacia abstracciones, no implementaciones
- **Low coupling**: cambios en un módulo no deben romper otros

### Capas (Clean Architecture)
```
Entities → Use Cases → Interface Adapters → Frameworks/Drivers
```
Las dependencias apuntan siempre hacia el centro.

### Cuándo crear un ADR
- Nueva dependencia externa (librería, servicio)
- Cambio en el modelo de datos
- Decisión de autenticación o autorización
- Cambio de estrategia de despliegue

### Red flags a detectar
- Clases >300 líneas → candidatas a split
- Funciones >50 líneas → extraer subfunciones
- Importaciones circulares → reestructurar capas
- Más de 5 parámetros en un método → objeto de configuración

### Diagramas
- C4 model para sistemas complejos
- Secuencia para flujos OAuth/Auth
- ER para esquemas de BD
