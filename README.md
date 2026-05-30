---
title: Droidify
emoji: 🤖
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
short_description: Live Android ROM, device and recovery indexer
tags:
  - android
  - rom
  - lineageos
  - fastapi
pinned: false
---

# Droidify — Hugging Face Spaces

> **This is the HF Spaces build.** The main repository for self-hosting is [github.com/eliekh05/Droidify](https://github.com/eliekh05/Droidify).

---

## A note on this deployment

HF Spaces Docker requires a single root Dockerfile on port 7860. The main Droidify repo runs two containers — nginx serving static files on port 80, and FastAPI handling the API internally on port 8000. That architecture cannot run on HF Spaces without changes.

This repo is a dedicated HF build where FastAPI serves both the static frontend and the API in a single process on port 7860. The scrapers, frontend, and API are identical to the main repo. Only the serving layer is different.

**Updates here will lag behind the main repo.** This is a manual sync — when the main repo gets new scrapers, bug fixes, or frontend changes, this deployment gets updated separately. There will always be some delay between the two. If you need the latest version, self-host from the main repo.

**A note on ownership.** The original developer of Droidify remains the same regardless of what happens to this Space. If HF Spaces ever forces a situation where the account hosting this Space needs to change — whether due to platform policy, account issues, or anything else HF decides to do — any new owner of this Space will be someone directly controlled and trusted by the original developer. The code, the project, and the direction stay the same. The original developer is still building this with the help of AI tools and has no intention of walking away. But HF Spaces is a third-party platform and third-party platforms do unpredictable things — so this is just an honest note that the Space owner and the project owner are not necessarily the same person, and the project owner is always [eliekh05](https://github.com/eliekh05/Droidify).

---

## What it does

Live Android ecosystem indexer — search devices, custom ROMs, recoveries, tools, and guides fetched in real time from 20+ free public sources. No login. No ads. No hardcoded data.

**Devices:** 1,100+ indexed from LineageOS, OrangeFox, TWRP and more
**ROMs:** 2,300+ builds — crDroid, Evolution X, GrapheneOS, DivestOS, /e/OS, CalyxOS, iodéOS, LineageOS, and more
**Recoveries:** 1,200+ — TWRP, OrangeFox, PBRP, SHRP
**GSI ROMs:** AxionAOSP, LunarisOS, AOSP, Evolution X GSI, and more for all Treble devices

---

## API

| Endpoint | Description |
|---|---|
| `GET /api/devices?q=` | Search devices by name, codename, or manufacturer |
| `GET /api/devices/{codename}` | Device detail — ROMs, recoveries, stock firmware |
| `GET /api/roms?q=` | ROM index |
| `GET /api/recoveries?q=` | Recovery index |
| `GET /api/tools` | Root tools — Magisk, KernelSU, APatch |
| `GET /api/android-versions` | Android version history |
| `GET /api/guides/{codename}` | Flashing guides |
| `GET /api/health` | Health check — returns `{"status": "ok", "build": "huggingface"}` |
| `GET /docs` | Interactive Swagger UI |

---

## Why two repos instead of one with multiple Dockerfiles?

Because keeping the main repo clean matters more than convenience. The main repo is a proper two-container production setup with nginx. Putting HF-specific logic (port overrides, StaticFiles mounts, single-process constraints) into the main Dockerfile or docker-compose would make it worse for everyone self-hosting. A dedicated repo keeps both builds clean and honest about what they are.

---

## Self-hosting (better option)

```bash
git clone https://github.com/eliekh05/Droidify
cd Droidify
./install.sh
```

Runs nginx + FastAPI, full production setup, no port restrictions. Works on any machine with Docker.

---

## License

MIT — [github.com/eliekh05/Droidify](https://github.com/eliekh05/Droidify)
