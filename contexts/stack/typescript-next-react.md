---
context: stack
name: TypeScript · Next.js · React
description: Next.js 15+ · React 19 · TypeScript strict · App Router
---

## Stack TypeScript/Next.js

### Reglas de tipado
- `strict: true` siempre — nunca `any` sin justificación
- Tipos explícitos en props de componentes
- `zod` para validación en runtime (APIs, formularios)

### App Router (Next.js 15+)
- Server Components por defecto — Client Components solo si necesario
- `use server` / `use client` explícito
- Route handlers en `app/api/`
- Metadata en cada page.tsx

### React 19
- `use()` hook para Promises en Server Components
- Server Actions para mutaciones de formulario
- No usar `useEffect` para fetch — usar Server Components

### Prohibido
- `any` sin comentario justificativo
- `pages/` router en proyectos nuevos
- CSS inline (usar Tailwind o CSS Modules)
