# PubFinder System Architecture

This document provides a high-level architectural summary of the entire **PubFinder (Beerdar)** platform, illustrating how the frontend Single Page Application (SPA), backend API service, caching layers, external geospatial providers, container environment, and Brewery CI/CD deployment engine operate together as a unified ecosystem.

---

## 🛰️ High-Level System Architecture Diagram

```mermaid
graph TD
    subgraph Client_Device ["Client Browser / Mobile Device"]
        Browser["SPA Client Interface"]
        Geo["Browser Geolocation API"]
        Browser -->|Acquire GPS| Geo
    end

    subgraph UI_Container ["Frontend Container (pubfinder-ui)"]
        Nginx["Nginx Alpine Web Server"]
        Assets["Static HTML / JS / CSS Assets"]
        Nginx -->|Serves Static Files| Assets
    end

    subgraph API_Container ["Backend Container (pubfinder-api)"]
        FastAPI["Python FastAPI Server"]
        VenueService["Domain Venue Service"]
        Cache["Spatial LRU Cache Repository"]
        ProviderChain["ProviderChain Strategy"]
        
        FastAPI --> VenueService
        VenueService -->|Check ~100m Grid| Cache
        VenueService -->|Cache Miss| ProviderChain
    end

    subgraph External_OSM ["External OpenStreetMap Providers"]
        Nominatim["Nominatim Spatial Engine"]
        Overpass["Overpass API Interpreter"]
        
        ProviderChain -->|Primary Bounding Box Query| Nominatim
        ProviderChain -->|Secondary Fallback Query| Overpass
    end

    subgraph Brewery_Engine ["CI/CD & Deployment Engine (Brewery)"]
        Brewery["Brewery Engine"]
        BuildSpec["build.yaml"]
        DeploySpec["deployment.yaml"]
        
        BuildSpec -->|Build Config| Brewery
        DeploySpec -->|Deployment Config| Brewery
        Brewery -->|Health Check GET /health| FastAPI
    end

    Browser -->|1. HTTP GET /| Nginx
    Browser -->|2. GET /api/v1/nearest| Nginx
    Nginx -->|3. Proxy /api/ -> pubfinder-api:8080| FastAPI
```

---

## 🧩 Architectural Layers & System Components

### 1. User Interface & Edge Layer (`pubfinder-ui`)
- **Technology Stack**: Svelte 4, TypeScript, TailwindCSS v4, and Lucide Icons.
- **Visual Design**: 8-bit retro light-mode arcade aesthetic utilizing Google Fonts (*Silkscreen* and *Press Start 2P*), hard 3D pixel drop shadows, and 4px solid black border framing.
- **PWA Service Worker**: Registered via `vite-plugin-pwa` with `skipWaiting` and `clientsClaim` for instant deployment updates.
- **Web Server & Reverse Proxy**: Hosted inside an Nginx Alpine container (Port `4002` host / `80` container). Serves static HTML/JS/CSS assets with `no-cache` headers for HTML/Service Worker files and proxies `/api/` traffic internally to `pubfinder-api:8080`.

---

### 2. Backend Application & Processing Layer (`pubfinder-api`)
- **Technology Stack**: Python 3.11, FastAPI, Pydantic v2, and `httpx`.
- **Modular Software Design**:
  - **Strategy Pattern (`ProviderChain`)**: Encapsulates external data provider logic, prioritizing OpenStreetMap Nominatim bounding-box queries (~0.25s response time) and falling back to Overpass API interpreter queries.
  - **Repository Pattern (`SpatialLRUCacheRepository`)**: Implements grid-based spatial caching by rounding user coordinates to 3 decimal places (~100m grid cell) with 15-minute TTL invalidation.
  - **Domain Service Layer (`VenueService` & `GeoService`)**: Normalizes address structures, filters non-drinking establishments or disused venues, calculates Haversine distances and walking times, and sorts venues by proximity.
- **Async Lifespan Connection Pooling**: Manages a shared `httpx.AsyncClient` socket connection pool across the application lifecycle to minimize TCP handshake overhead.

---

### 3. External Geospatial Integrations
- **OpenStreetMap Nominatim**: Primary provider querying spatial amenity nodes and building polygon ways.
- **OpenStreetMap Overpass API**: Secondary fallback provider querying raw node/way elements when primary queries time out or yield no results.
- **Google Maps**: Generates direct destination navigation URLs (`https://www.google.com/maps/dir/?api=1&destination={lat},{lon}`) for user routing.

---

### 4. CI/CD Pipeline & Homelab Orchestration (Brewery)
- **Container Build Specifications (`build.yaml`)**:
  - Configures artifact compilation patterns for `pubfinder-api` (`backend/Dockerfile`) and `pubfinder-ui` (`frontend/Dockerfile`).
- **Deployment Specifications (`deployment.yaml`)**:
  - Defines service mapping, host port bindings (`4001:8080` for API, `4002:80` for UI), rolling deployment strategies, automatic failure rollbacks, and explicit HTTP health check monitoring (`GET /health`).

---

## 🔄 End-to-End Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User Device
    participant UI as pubfinder-ui (Nginx)
    participant API as pubfinder-api (FastAPI)
    participant OSM as OpenStreetMap Providers

    User->>UI: Access Web App (GET /)
    UI-->>User: Serve 8-Bit Retro SPA & Favicon
    User->>User: Acquire GPS Coordinates (Device Location API)
    User->>UI: GET /api/v1/nearest?lat=51.5117&lon=-0.1240
    UI->>API: Proxy Request to pubfinder-api:8080/api/v1/nearest
    
    alt Spatial Cache Hit
        API-->>UI: Return Cached Venues JSON
    else Spatial Cache Miss
        API->>OSM: Query Nominatim / Overpass Providers
        OSM-->>API: Return Raw Spatial Nodes/Ways
        API->>API: Filter Disused, Calculate Distance & Walking Time, Sort
        API-->>UI: Return NearestResponse JSON
    end

    UI-->>User: Render Retro Radar Compass & Expandable Target Cards
```

---

## 🛠️ Verification & Health Monitoring

- **API Health Check Endpoint**: `GET /health` returns JSON `{"status": "healthy", "service": "pubfinder-api", "timestamp": "..."}`.
- **UI Health Check Endpoint**: `GET /` returns `200 OK` HTML index page.
- **Stateless Operation**: The platform requires no persistent database, relying entirely on real-time spatial ingress and in-memory spatial grid caching.
