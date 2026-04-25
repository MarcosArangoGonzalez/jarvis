---
context: stack
name: Android · Kotlin
description: Android 14+ · Kotlin 2.x · Compose UI · Coroutines
---

## Stack Android/Kotlin

### Arquitectura
- MVVM con ViewModel + StateFlow
- Repository pattern para datos
- Hilt para dependency injection
- Coroutines + Flow para async

### UI (Jetpack Compose)
- State hoisting — UI sin lógica de negocio
- `remember`/`rememberSaveable` para estado de UI
- Material 3 components

### Prohibido
- `AsyncTask` (deprecated)
- `LiveData` en código nuevo (usar StateFlow)
- Acceso a red en el hilo principal
- Permisos sin justificación en manifest

### Build
- Gradle Kotlin DSL (`.kts`)
- `minSdk 26` por defecto a menos que se especifique
