---
context: stack
name: Java · Spring Boot · Angular
description: Spring Boot 3.x · Java 21 · Angular 17+ · JWT auth
---

## Stack Java/Spring Boot + Angular

### Backend (Spring Boot 3.x / Java 21)
- Virtual threads (`@EnableVirtualThreads`) para IO-bound
- Spring Security 6 con JWT (RS256, refresh tokens)
- Repository pattern con Spring Data JPA
- Flyway para migraciones de BD
- `@Validated` en todos los DTOs de entrada

### Frontend (Angular 17+)
- Standalone components — sin NgModules cuando sea posible
- Signals para state management reactivo
- `inject()` en lugar de constructor injection
- Lazy loading de rutas por defecto

### Prohibido
- `@Transactional` en controllers
- Lógica de negocio en `@RestController`
- Cualquier secret hardcodeado

### Build
- Maven Wrapper (`./mvnw`)
- Multi-stage Docker: build + runtime JRE mínimo
