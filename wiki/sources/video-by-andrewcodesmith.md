---
title: "Video by andrewcodesmith"
type: source
status: NEW
tags:
  - "instagram"
created: 2026-04-18
updated: 2026-04-18
tokens_consumed: 220
sources:
  - "https://www.instagram.com/reel/DXAhfExDolr/?igsh=YnVtZnNiazJpczg1"
Summary: "7 rules of app security (from a senior software engineer) 

Security isn’t about doing everything perfectly, it’s about nailing the 20% that stops 80% of the damage.

👾 Authentication on the server 
o"
requires_verification: true
validated: ~
---

# Video by andrewcodesmith

> 7 rules of app security (from a senior software engineer) 

Security isn’t about doing everything perfectly, it’s about nailing the 20% that stops 80% of the damage.

👾 Authentication on the server 
o

## Source

- URL: https://www.instagram.com/reel/DXAhfExDolr/?igsh=YnVtZnNiazJpczg1
- Type: instagram

## Raw Extract (excerpt)

7 rules of app security (from a senior software engineer) 

Security isn’t about doing everything perfectly, it’s about nailing the 20% that stops 80% of the damage.

👾 Authentication on the server 
only

“You’re logged in” must be decided by the backend, not the frontend. Use a solid system (Supabase, Auth0, JWT, etc.) and never let the client fake its identity.

👾 Authorisation on every action 

Being logged in doesn’t mean you can do anything. On every sensitive API call, the server must check “can this user touch this specific record?” and never trust only UI‑side guards.

👾 Treat all input as untrusted 

Form fields, URL params, API payloads, even AI‑generated inputs - treat them all as untrusted. Always validate, sanitise, and use parameterized queries or safe ORM patterns to block injection.

👾 Secrets never in client/git

Never put API keys, JWT secrets, DB passwords, or admin tokens in the frontend, mobile app, or config files in the repo. Keep them in environment variables or
