# Live Device Compass Tracking & Real-Time Position Updates

This document describes the design, mathematical algorithm, component architecture, and unit testing strategy for the **Live Device Compass Tracking** and **Real-Time GPS Position Watching** features in PubFinder.

---

## 🎯 Feature Overview

1. **Live Magnetometer / Gyroscope Orientation**:
   - Uses browser `DeviceOrientationEvent` APIs (`webkitCompassHeading` on iOS, `deviceorientationabsolute` / `alpha` on Android/Chrome) to track phone orientation in real time.
   - Rotates the retro 8-bit cardinal ring ($N, E, S, W$) to align with True North ($\theta_{\text{dial}} = -H_{\text{device}}$) and points the red needle directly at the physical pub location ($\theta_{\text{needle}} = B_{\text{target}} - H_{\text{device}}$).
   - Includes iOS permission handling (`DeviceOrientationEvent.requestPermission()`).

2. **Continuous Real-Time GPS Tracking**:
   - Uses `navigator.geolocation.watchPosition` to track the user's location as they physically walk down the street.
   - Dynamically recalculates distance ($M/\text{KM}$), walking time ($\sim\text{MIN}$), and target bearing in real time across `Compass`, `HeroCard`, and `AlternativesList`.

---

## 🧮 Mathematical Algorithm & Smooth Angle Tracking

```
[ Target Venue ] (Absolute Bearing: B_target)
       ^
       |
       |  Relative Needle Angle = B_target - H_filtered
       |
[ Phone Top Edge ] (Device Heading: H_filtered)
```

### 1. Static Target Bearing ($B_{\text{target}}$)
Calculated between user coordinates $(lat_1, lon_1)$ and target venue coordinates $(lat_2, lon_2)$:

$$\theta = \operatorname{atan2}\left(\sin(\Delta\lambda)\cos(\phi_2), \cos(\phi_1)\sin(\phi_2) - \sin(\phi_1)\cos(\phi_2)\cos(\Delta\lambda)\right)$$
$$B_{\text{target}} = (\theta \cdot \frac{180}{\pi} + 360) \pmod{360}$$

---

### 2. Continuous Shortest-Path Angle Tracking
To prevent $360^\circ \leftrightarrow 0^\circ$ wrap-around jump glitches when performing full 360-degree spins, incoming target headings ($H_{\text{raw}}$) are tracked using continuous shortest-path angular differences:

$$\Delta H = ((H_{\text{raw}} - H_{\text{current}} + 540) \pmod{360}) - 180$$
$$H_{\text{current}} \leftarrow H_{\text{current}} + 0.15 \cdot \Delta H$$

Because $H_{\text{current}}$ is updated continuously in scalar space without artificial $0..360$ resets during animation frames, CSS rotational transforms execute fluidly without reverse 360-degree spins.

---

### 3. Sibling DOM Rotations

- **Cardinal Dial Rotation**: $\theta_{\text{dial}} = -H_{\text{current}}$ (North always points to physical True North).
- **Pub Pointer Needle (Red Arrow)**: $\theta_{\text{needle}} = B_{\text{target}} - H_{\text{current}}$ (Red tip points directly at target pub in real 3D space).

---

## 🛠️ Unit Test Suite

Frontend unit tests are implemented in `frontend/src/lib/geo.test.ts` using Vitest:

- `calculateBearing`: Verifies angular calculations between known coordinates.
- `calculateHaversineDistance`: Verifies spherical distance computation.
- `calculateWalkingTimeMinutes`: Verifies walking time calculations based on an $80\text{m/min}$ pace.
- `normalizeAngle`: Ensures degree wrapping in $0..360$.
- `calculateShortestAngleDiff`: Verifies shortest-path angular difference computation across $0^\circ / 360^\circ$ boundaries.
- `computeRelativeBearing`: Verifies relative needle angles relative to phone orientation.

Execute unit tests locally:
```bash
cd frontend
npm test
```
