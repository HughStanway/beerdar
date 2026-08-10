export function calculateBearing(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const deltaLambda = ((lon2 - lon1) * Math.PI) / 180;

  const y = Math.sin(deltaLambda) * Math.cos(phi2);
  const x =
    Math.cos(phi1) * Math.sin(phi2) -
    Math.sin(phi1) * Math.cos(phi2) * Math.cos(deltaLambda);

  const theta = Math.atan2(y, x);
  return Math.round(((theta * 180) / Math.PI + 360) % 360);
}

export function calculateHaversineDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371000; // Earth radius in meters
  const phi1 = (lat1 * Math.PI) / 180;
  const phi2 = (lat2 * Math.PI) / 180;
  const dphi = ((lat2 - lat1) * Math.PI) / 180;
  const dlambda = ((lon2 - lon1) * Math.PI) / 180;

  const a =
    Math.sin(dphi / 2) ** 2 +
    Math.cos(phi1) * Math.cos(phi2) * Math.sin(dlambda / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c);
}

export function calculateWalkingTimeMinutes(meters: number): number {
  if (meters <= 0) return 1;
  return Math.max(1, Math.ceil(meters / 80)); // 80 m/min = approx 4.8 km/h
}

export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${meters}M`;
  }
  return `${(meters / 1000).toFixed(1)}KM`;
}

export function normalizeAngle(degrees: number): number {
  return ((degrees % 360) + 360) % 360;
}

export function calculateShortestAngleDiff(current: number, target: number): number {
  return ((target - current + 540) % 360) - 180;
}

export function computeRelativeBearing(targetBearing: number, deviceHeading: number): number {
  return normalizeAngle(targetBearing - deviceHeading);
}
