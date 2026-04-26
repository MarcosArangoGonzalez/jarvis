---
context: stack
name: Vercel · Edge Functions
description: Next.js deploy en Vercel, Edge Runtime, Preview deployments, env vars
---

## Stack Vercel / Edge

### Deployment
- Preview automático en cada PR — nunca desplegar a prod desde local
- Production en merge a `main` vía GitHub integration
- Variables de entorno: Vercel Dashboard → Environment Variables (no en código)
- Secrets sensibles: sincronizar desde Bitwarden → Vercel CLI

### Edge Runtime
- `export const runtime = 'edge'` para funciones ultraligeras (<1ms cold start)
- Limitaciones: sin `fs`, sin `child_process`, sin Node.js APIs nativas
- Usar solo para: middleware, auth checks, geolocalización, A/B testing
- Node.js Runtime para: DB queries, file processing, heavy compute

### Vercel CLI útil
```bash
vercel env pull .env.local     # pull variables de desarrollo
vercel deploy --prebuilt       # deploy desde build local
vercel logs <deployment-url>   # logs en tiempo real
```

### Optimizaciones
- `next/image` para todas las imágenes — optimización automática
- ISR (Incremental Static Regeneration) para páginas semi-estáticas
- Edge caching en headers de respuesta: `Cache-Control: s-maxage=60`

### Prohibido
- Secrets en `next.config.js` o variables de entorno del lado del cliente sin prefijo `NEXT_PUBLIC_`
- Deploy directo a producción sin pasar por preview
