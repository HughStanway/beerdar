# 🍺 PubFinder (Beerdar)

A self-hosted, location-aware microservice and high-performance Progressive Web Application (PWA) built as a pure client-side SPA (Pattern 1) with an 8-bit retro arcade interface. It determines the user's geolocation upon page load and instantly displays the nearest pub, microbrewery, or taproom using live OpenStreetMap data, complete with walking distance, compass bearing, and interactive navigation.

Fully integrated for automated multi-container compilation and deployment via the **[Brewery CI/CD Pipeline](https://github.com/HughStanway/brewery)**.

---

## 🚀 Features

- **Stateless & Database-Free:** Operates with zero persistent local database requirements. Live OpenStreetMap geospatial data is indexed on the fly.
- **Pattern 1 Container Architecture:** Frontend is served via high-performance `nginx:alpine` with `try_files` SPA fallback and API reverse proxying.
- **Sub-Second Spatial Performance:** High-speed OpenStreetMap Nominatim and Overpass proxy engine with an in-memory spatial LRU cache (~100m spatial grid resolution, 15-minute TTL).
- **8-Bit Retro Arcade UI:** Built with Svelte + Vite + Tailwind CSS, featuring pixelated typography (`Press Start 2P`, `Silkscreen`), hard drop-shadows, animated directional compass dial, and light mode aesthetics.
- **Brewery CI/CD Pipeline Ready:** Out-of-the-box compatibility with `build.yaml` (docker-image compilation) and `deployment.yaml` (rolling deployments, container health polling, automatic rollbacks).

---

## 🛠️ Architecture

```
                          [ Client Browser / PWA Mobile ]
                                         │
                                         │ HTTP (HTML5 Geolocation: Lat, Lon)
                                         ▼
                               [ pubfinder-ui Container ]
                                Nginx Alpine (Pattern 1 SPA)
                                         │
                        ┌────────────────┴────────────────┐
                        │ Internal Docker Bridge Network  │
                        ▼                                 ▼
             [ / (Static Assets) ]           [ /api/ (Proxy) ]
                                                      │
                                                      ▼
                                           [ pubfinder-api Container ]
                                            FastAPI / Python Microservice
                                                      │
                                                      │ Spatial Cache & OSM Ingress
                                                      ▼
                                         [ OpenStreetMap Services ]
                                          (Nominatim / Overpass)
```

---

## ⚡ Quick Start (Local Docker Compose)

### Prerequisites
- Docker & Docker Compose installed.

### Run Stack
```bash
# Clone and enter directory
cd /Users/hughstanway/Projects/beerdar

# Build and start services
docker-compose up --build -d
```

Access the application in your browser:
- **Frontend SPA UI:** `http://localhost:3000`
- **Backend API:** `http://localhost:8080/health` or `http://localhost:8080/api/v1/nearest?lat=51.8115&lon=-0.0298`

---

## 🍺 Brewery CI/CD Integration

This project includes pre-configured repository-root manifests for Brewery:

1. **`build.yaml`**: Configures Brewery's Build Engine to compile multi-stage Dockerfiles into versioned registry artifacts:
   - `pubfinder-api` (`backend/Dockerfile`)
   - `pubfinder-ui` (`frontend/Dockerfile`)

2. **`deployment.yaml`**: Configures Brewery's Deployment Engine to orchestrate services:
   - Automated health check polling on `http://pubfinder-api:8080/health` and `http://pubfinder-ui:80/`
   - Memory & CPU resource limits
   - Rolling update policy with automatic failure rollback

---

## 🧪 Running Tests

### Backend Unit & Integration Tests
```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest
```

### Frontend Build
```bash
cd frontend
npm install
npm run build
```

---

## 📡 REST API Endpoint Specifications

### `GET /health`
System health check endpoint used by Brewery CI/CD Deployment Engine and container orchestrators.
```json
{
  "status": "healthy",
  "timestamp": "2026-08-07T15:00:00Z",
  "service": "pubfinder-api"
}
```

### `GET /api/v1/nearest`
Queries OpenStreetMap for nearby pubs, bars, microbreweries, and taprooms.

**Parameters:**
- `lat` (float, required): User latitude (-90.0 to 90.0)
- `lon` (float, required): User longitude (-180.0 to 180.0)
- `limit` (int, optional, default = 1): Number of alternative venues to return
- `radius_m` (int, optional, default = 5000): Search radius in meters

---

## 📄 License
Proprietary - Homelab use only