---
title: Droidify
emoji: 🤖
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
license: mit
short_description: Live Android ROM and device indexer
---

# Droidify

Live Android ecosystem indexer. Devices, ROMs, recoveries, tools, and guides for 945+ devices — fetched in real time from 20+ public sources.

Source and self-host: [github.com/eliekh05/Droidify](https://github.com/eliekh05/Droidify)

## API

Base URL: `https://eliekh05-droidify-hf.hf.space`

| Endpoint | |
|---|---|
| `GET /api/devices` | Search 945+ devices |
| `GET /api/devices/{codename}` | Device + ROMs + recoveries + firmware |
| `GET /api/roms` | ROM index |
| `GET /api/recoveries` | TWRP, OrangeFox, PBRP, SHRP |
| `GET /api/tools` | Root and flashing tools |
| `GET /api/android-versions` | Android version history |
| `GET /api/guides` | Guides — root, flash, unlock, buy, sell |
| `GET /api/guides/{codename}` | Device-specific guides |
| `GET /api/health` | Health check |
| `GET /docs` | Swagger UI |
