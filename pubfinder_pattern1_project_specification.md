# Project Specification: PubFinder (Stateless, Global & Pattern 1 SPA)

**A self-hosted, location-aware microservice and high-performance Progressive Web Application (PWA) built as a pure client-side SPA (Pattern 1) and served via Nginx Alpine. It determines the user's geolocation upon page load and instantly displays the nearest pub, microbrewery, or taproom using live global OpenStreetMap data, complete with real-time opening status, walking distance, and interactive navigation.**

---

## 1. System Architecture & Container Strategy

```
                          [ Client Browser / PWA Mobile ]
                                         │
                                         │ HTTPS (HTML5 Geolocation: Lat, Lon)
                                         ▼
                        [ Existing Homelab Reverse Proxy ]
                            (Caddy / Traefik / Nginx)
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   │ Container Network (pubfinder-network)     │
                   │                                           │
                   ▼                                           ▼
         [ Frontend Container ]                      [ Backend Container ]
      Nginx Alpine (Pattern 1 SPA)               FastAPI / Node / Rust API
      Built from Multi-stage Dockerfile          Built from Multi-stage Dockerfile
                                                              │
                                                              │ Async Overpass QL Query
                                                              ▼
                                                  [ Public Overpass API ]
                                                   (Global OpenStreetMap)
```

### 1.1 Deployment & Containerization Requirements
* **Single Repository Architecture:** The application repository contains frontend SPA code, backend API proxy code, container manifests, and Brewery CI/CD pipeline configurations.
* **Pattern 1 Container Architecture:** The frontend uses a two-stage Docker build: Stage 1 uses Node.js to compile static assets (`/dist`), and Stage 2 copies those assets into an ultra-lightweight `nginx:alpine` image with custom SPA fallback routing (`try_files $uri $uri/ /index.html;`).
* **Stateless & Database-Free:** No local database (e.g. PostgreSQL/PostGIS) required. Operates with zero local storage requirements, making it completely lightweight and globally functional.
* **Brewery CI/CD Pipeline Integration:** Fully compatible with the [Brewery CI/CD Engine](https://github.com/HughStanway/brewery). Requires a repository-root `build.yaml` (defining `docker-image` artifacts for both API and UI) and `deployment.yaml` (specifying multi-container stack orchestration, health checks, and rollback policies).
* **Orchestration (`docker-compose.yml` & `deployment.yaml`):** Runs the API proxy and frontend Nginx container connected on an internal Docker bridge network, compatible with Brewery automated deployments and existing reverse proxies.

---

## 2. Technical Stack Specifications

### 2.1 Frontend Stack (Pattern 1 SPA)
* **Framework Options:** React + Vite, Svelte + Vite, or Vue 3 + Vite.
* **Styling & UI:** Tailwind CSS, Shadcn UI / Radix primitives, Lucide Icons.
* **UI/UX Paradigm:** Mobile-first, fluid responsive layout, dark mode by default, glassmorphism card components, high-contrast typography, animated directional compass indicator, and dynamic loading skeletons.
* **Location Handling:** HTML5 Geolocation API (`navigator.geolocation.getCurrentPosition` / `watchPosition`) with high accuracy enabled.
* **PWA Engine:** Service Worker registration via `vite-plugin-pwa` enabling offline app shell caching and native splash screen execution.

### 2.2 Backend API Stack
* **Framework:** Python (FastAPI with Pydantic v2 & HTTPX) or TypeScript (Node.js with Fastify / Axios).
* **External Provider:** Public Overpass API endpoints (e.g., `https://overpass-api.de/api/interpreter`).
* **Caching Layer:** In-memory LRU Cache (e.g., `cachetools` in Python or `lru-cache` in Node). Hashes user coordinates rounded to 3 decimal places (~100m spatial grid) with a 15-minute TTL to prevent external API rate-limiting.
* **Geospatial Processing:** Performs Haversine distance and walking time estimates in-memory before returning ordered venue arrays to the client.

---

## 3. External API Integration (Overpass QL)

The backend service executes an optimized Overpass QL query targeting surrounding nodes and ways tagged as drinking establishments:

```overpassql
[out:json][timeout:10];
(
  node["amenity"="pub"](around:5000, {lat}, {lon});
  node["amenity"="bar"](around:5000, {lat}, {lon});
  node["craft"="brewery"](around:5000, {lat}, {lon});
  node["microbrewery"="yes"](around:5000, {lat}, {lon});
  way["amenity"="pub"](around:5000, {lat}, {lon});
);
out center body;
```

---

## 4. REST API Endpoint Specifications

### `GET /health`
System health check endpoint used by Brewery CI/CD Deployment Engine and container orchestrators to monitor service availability.

* **Response Payload (`200 OK`):**
```json
{
  "status": "healthy",
  "timestamp": "2026-08-07T15:00:00Z",
  "service": "pubfinder-api"
}
```

---

### `GET /api/v1/nearest`
Accepts client coordinates, checks the in-memory spatial cache, proxies to the Overpass API if necessary, and returns the sorted venues.

* **Query Parameters:**
  * `lat` (float, required): User's current latitude.
  * `lon` (float, required): User's current longitude.
  * `limit` (int, optional, default = 1): Number of venues to return.
  * `radius_m` (int, optional, default = 5000): Search radius in meters.

* **Response Payload (`200 OK`):**

```json
{
  "status": "success",
  "query_location": {
    "latitude": 51.8115,
    "longitude": -0.0298
  },
  "primary_venue": {
    "id": "osm-node-1049281",
    "name": "The Saracens Head",
    "type": "pub",
    "distance_meters": 142,
    "walking_time_minutes": 2,
    "address": {
      "street": "High Street",
      "city": "Ware",
      "postcode": "SG12 9BP"
    },
    "opening_status": {
      "is_open_now": true,
      "raw": "Mo-Th 11:00-23:00; Fr-Sa 11:00-00:00; Su 12:00-22:30"
    },
    "coordinates": {
      "latitude": 51.8119,
      "longitude": -0.0291
    },
    "maps_url": "https://www.google.com/maps/dir/?api=1&destination=51.8119,-0.0291"
  },
  "alternatives": [
    {
      "id": "osm-node-1049282",
      "name": "Waterside Inn",
      "type": "pub",
      "distance_meters": 280,
      "walking_time_minutes": 4,
      "coordinates": {
        "latitude": 51.8105,
        "longitude": -0.0310
      }
    }
  ]
}
```

---

## 5. Dockerization & Deployment Setup

### 5.1 Frontend Dockerfile (`frontend/Dockerfile`)

```dockerfile
# Stage 1: Build Frontend Static Distribution
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve with High-Performance Nginx Alpine (Pattern 1)
FROM nginx:alpine AS runner
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 5.2 Frontend Nginx Configuration (`frontend/nginx.conf`)

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend container
    location /api/ {
        proxy_pass http://pubfinder-api:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

### 5.3 Backend API Dockerfile (`backend/Dockerfile`)

```dockerfile
# Stage 1: Build Dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime Image
FROM python:3.11-slim AS runner
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 5.4 Complete Stateless `docker-compose.yml`

```yaml
version: '3.8'

services:
  pubfinder-api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: pubfinder-api
    environment:
      - CACHE_TTL_SECONDS=900
      - OVERPASS_URL=https://overpass-api.de/api/interpreter
    restart: unless-stopped
    networks:
      - pubfinder-net

  pubfinder-ui:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: pubfinder-ui
    ports:
      - "3000:80"
    depends_on:
      - pubfinder-api
    restart: unless-stopped
    networks:
      - pubfinder-net

networks:
  pubfinder-net:
    driver: bridge
```

### 5.5 Brewery CI/CD Build Configuration (`build.yaml`)

Required by Brewery Build Engine at repository root to compile and register container images:

```yaml
metadata:
  name: beerdar
  versionScheme: semver

build:
  image: node:20-alpine
  timeoutSeconds: 300
  memory: 512m
  cpus: 1

steps:
  setup: |
    echo "Initializing build workspace..."
  build: |
    echo "Verifying Dockerfile specifications for frontend and backend..."
  test: |
    echo "Running component tests..."

artifacts:
  - name: pubfinder-api
    pattern: backend
    type: docker-image

  - name: pubfinder-ui
    pattern: frontend
    type: docker-image
```

### 5.6 Brewery CI/CD Deployment Specification (`deployment.yaml`)

Required by Brewery Deployment Engine at repository root to automate container orchestration, health tracking, and rollbacks:

```yaml
version: 1

deployment:
  name: pubfinder-stack
  description: "PubFinder 8-Bit Retro Arcade SPA and Location-Aware Ingress API"

services:
  pubfinder-api:
    artifact: "pubfinder-api@latest"
    type: "docker-image"
    ports:
      - "8080:8080"
    environment:
      CACHE_TTL_SECONDS: "900"
      OVERPASS_URL: "https://overpass-api.de/api/interpreter"
    healthCheck:
      endpoint: "GET http://pubfinder-api:8080/health"
      interval: "10s"
      timeout: "5s"
      retries: 3
      unhealthyThreshold: 2
    resources:
      cpus: "0.5"
      memory: "256m"

  pubfinder-ui:
    artifact: "pubfinder-ui@latest"
    type: "docker-image"
    ports:
      - "3000:80"
    depends_on:
      - pubfinder-api
    healthCheck:
      endpoint: "GET http://pubfinder-ui:80/"
      interval: "10s"
      timeout: "5s"
      retries: 3
      unhealthyThreshold: 2
    resources:
      cpus: "0.25"
      memory: "128m"

networks:
  default:
    driver: bridge

policies:
  strategy: "rolling"
  waitForHealthy: true
  healthCheckTimeout: 60s

rollback:
  automatic: true
  onFailure: true
  keepPreviousVersions: 3
```

---

## 6. Implementation Roadmap

```
Phase 1: Backend Proxy & Cache Engine
├── Implement FastAPI/Node API service with GET /health & GET /api/v1/nearest
├── Build Overpass QL query builder & HTTP client
└── Add in-memory spatial caching with 3-decimal coordinate rounding (~100m grid)

Phase 2: Modern Frontend SPA Development (Pattern 1)
├── Scaffold Vite project (React/Svelte/Vue) with Tailwind CSS
├── Implement custom HTML5 Geolocation hook with permission error handling
├── Build full hero card UI, compass directional arrow, and maps routing trigger
└── Write custom frontend nginx.conf with try_files SPA fallback

Phase 3: Brewery CI/CD Integration & Homelab Deployment
├── Create root build.yaml (docker-image artifacts) for Brewery Build Engine
├── Create root deployment.yaml (health checks, policies) for Brewery Deployment Engine
├── Verify multi-stage Docker builds for frontend (Nginx Alpine) and backend
├── Validate automated build & deployment via Brewery CI/CD pipeline
└── Register PWA manifest for native mobile add-to-homescreen installation
```
