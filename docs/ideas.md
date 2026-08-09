# PubFinder Feature Roadmap & Improvement Ideas

This document outlines proposed feature ideas, UX enhancements, and technical improvements for **PubFinder (Beerdar)**.

---

## 🍻 1. Radar Controls & Venue Filtering

- **Venue Category Filters**: Interactive toggle badges to filter search results by venue type:
  - `ALL`
  - `TRADITIONAL PUBS`
  - `CRAFT BREWERIES & TAPROOMS`
  - `BEER GARDENS`
  - `COCKTAIL BARS`
- **Adjustable Search Radius**: 8-bit retro slider or quick selector buttons (`500M`, `1KM`, `3KM`, `5KM`) to dynamically control search distance.
- **"Open Now Only" Toggle**: Filter out closed venues based on OpenStreetMap `opening_hours` data.

---

## 🧭 2. Real-Time Compass & Map Integration

- **Live Device Compass Tracking**: Utilize mobile `DeviceOrientation` API so the retro radar compass needle dynamically rotates as the user physically turns in the street.
- **Interactive 8-Bit Canvas Map**: Retro-styled map overlay displaying user location and target pub blips.
- **Location Search Bar**: Allow users to search by place name or postcode (e.g., *"Covent Garden"*, *"Manchester Northern Quarter"*, *"SG12"*) in addition to automated GPS acquisition.

---

## 🏆 3. "Mission Mode" & Pub Crawl Route Generator

- **Pub Crawl Route Generator**: Algorithm calculating an optimal 3-pub or 5-pub walking route starting from the user's current coordinates, complete with total walking distance and route order.
- **Retro Arcade Achievements & Check-Ins**: Allow users to "Check In" at pubs (saved in local storage/PWA storage), unlocking 8-bit arcade badges (*"First Pint"*, *"Brewery Explorer"*, *"5-Pub Veteran"*).

---

## 🌳 4. Rich Venue Amenities & Details

- **Amenity Badges**: Extract and display OpenStreetMap tags as retro badges:
  - 🌳 **Beer Garden** (`outdoor_seating=yes`)
  - 🐶 **Dog Friendly** (`dog=yes`)
  - 🍕 **Food Served** (`food=yes`)
  - 📶 **Free Wi-Fi** (`internet_access=wlan`)
  - ♿ **Wheelchair Accessible** (`wheelchair=yes`)
  - ⚽ **Live Sports / TV** (`sports_pub=yes`)
- **Share Target Link & QR Code**: Generate shareable URLs or QR codes so users can text target pub coordinates to friends.

---

## 📱 5. PWA & Offline Enhancements

- **Offline / Low-Data Storage**: Save recent venue searches to IndexedDB so users can view target details and addresses even with weak mobile signal inside cellar pubs.
