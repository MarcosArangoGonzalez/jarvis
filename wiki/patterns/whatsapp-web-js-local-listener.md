---
title: "WhatsApp local listener (whatsapp-web.js)"
type: pattern
status: active
tags:
  - whatsapp
  - nodejs
  - automation
  - local
pattern_category: api
language: typescript
complexity: medium
reusable: true
created: 2026-04-18
updated: 2026-04-18
tokens_consumed: 220
sources:
  - "tools/skills/whatsapp_listener/listener.js"
Summary: "Listener de WhatsApp local via whatsapp-web.js usando LocalAuth. El QR se muestra en terminal y la sesión persiste. Alternativa local a Green API (que bloquea QR cloud)."
---

# WhatsApp local listener (whatsapp-web.js)

> Green API y servicios cloud similares fallan el QR porque WhatsApp detecta que la sesión no es local. whatsapp-web.js corre en la misma máquina que el navegador → WhatsApp lo trata como WhatsApp Web normal.

## Pattern

```js
import { Client, LocalAuth } from "whatsapp-web.js";
import qrcode from "qrcode-terminal";

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "./.wwebjs_auth" }),
  puppeteer: { headless: true, args: ["--no-sandbox"] },
});

client.on("qr", (qr) => qrcode.generate(qr, { small: true }));
client.on("ready", () => console.log("Ready"));
client.on("message", async (msg) => {
  // process msg.body
  await msg.reply("✓ received");
});

client.initialize();
```

## Key Points

- `LocalAuth` persiste la sesión en `.wwebjs_auth/` — no re-scan tras primer auth
- Filtrar por `msg.from` para escuchar solo el chat de Jarvis (`JARVIS_WHATSAPP_CHAT_ID`)
- `msg.isGroupMsg` — skip group messages
- Puppeteer necesita Chromium instalado: `apt install chromium-browser` o deja que npm lo descargue
- `--disable-dev-shm-usage` es necesario en entornos con /dev/shm pequeño (Docker, WSL)

## Setup

```bash
cd tools/skills/whatsapp_listener
npm install
node listener.js   # scan QR → session saved
# Next runs: node listener.js (no QR needed)
```

## Caveats

- La sesión caduca si WhatsApp Web se cierra en otro dispositivo — borrar `.wwebjs_auth/` y re-scan
- whatsapp-web.js puede romper con updates de WhatsApp Web — mantener `npm update` periódico
- Gitignore `.wwebjs_auth/` — contiene cookies de sesión

## Related

[[wiki/patterns]] | [[wiki/sources]]
