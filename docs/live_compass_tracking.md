# Live Device Compass Tracking & Real-Time Position Updates

This document describes the design, mathematical algorithm, component architecture, and unit testing strategy for the **Live Device Compass Tracking** and **Real-Time GPS Position Watching** features in PubFinder.

---

## 🎯 Feature Overview

1. **Live Magnetometer / Gyroscope Orientation**:
   - Uses browser `DeviceOrientationEvent` APIs (`webkitCompassHeading` on iOS, `deviceorientationabsolute` / `alpha` on Android/Chrome) to track phone orientation in real time.
   - Rotates the retro 8-bit cardinal ring ($N, E, S, W$) to align with True North and points the needle at the physical venue location relative to the top edge of the user's phone.
   - Includes iOS permission handling (`DeviceOrientationEvent.requestPermission()`).

2. **Continuous Real-Time GPS Tracking**:
   - Uses `navigator.geolocation.watchPosition` to track the user's location as they physically walk down the street.
   - Dynamically recalculates distance ($M/\text{KM}$), walking time ($\sim\text{MIN}$), and target bearing in real time across `Compass`, `HeroCard`, and `AlternativesList`.

---

## 🧮 Mathematical Algorithm

```
[ Target Venue ] (Absolute Bearing: B_target)
       ^
       |
       |  Relative Needle Angle = (B_target - H_filtered + 360) % 360
       |
[ Phone Top Edge ] (Device Heading: H_filtered)
```

### 1. Static Target Bearing ($B_{\text{target}}$)
Calculated between user coordinates $(lat_1, lon_1)$ and target venue coordinates $(lat_2, lon_2)$:

$$\theta = \operatorname{atan2}\left(\sin(\Delta\lambda)\cos(\phi_2), \cos(\phi_1)\sin(\phi_2) - \sin(\phi_1)\cos(\phi_2)\cos(\Delta\lambda)\right)$$
$$B_{\text{target}} = (\theta \cdot \frac{180}{\pi} + 360) \pmod{360}$$

---

### 2. Device Heading Low-Pass Filtering
To prevent needle jitter from minor hand tremors, incoming headings ($H_{\text{raw}}$) pass through a shortest-path angular low-pass filter:

$$\Delta H = ((H_{\text{raw}} - H_{\text{current}} + 540) \pmod{360}) - 180$$
$$H_{\text{filtered}} = (H_{\text{current}} + \alpha \cdot \Delta H + 360) \pmod{360} \quad (\alpha = 0.2)$$

---

### 3. Display Rotations

- **Compass Dial Rotation**: $\theta_{\text{dial}} = -H_{\text{filtered}} \pmod{360}$
- **Needle Rotation (Relative Mode)**: $\theta_{\text{needle}} = (B_{\text{target}} - H_{\text{filtered}} + 360) \pmod{360}$
- **Needle Rotation (Static Fallback)**: $\theta_{\text{needle}} = B_{\text{target}}$

---

## 🛠️ Unit Test Suite

Frontend unit tests are implemented in `frontend/src/lib/geo.test.ts` using Vitest:

- `calculateBearing`: Verifies angular calculations between known coordinates.
- `calculateHaversineDistance`: Verifies spherical distance computation.
- `calculateWalkingTimeMinutes`: Verifies walking time calculations based on an $80\text{m/min}$ pace.
- `normalizeAngle`: Ensures degree wrapping in $0..360$.
- `computeRelativeBearing`: Verifies relative needle angles relative to phone orientation.
- `interpolateAngle`: Verifies smooth angular interpolation across the $0^\circ / 360^\circ$ boundary.

Execute unit tests locally:
```bash
cd frontend
npm test
```
