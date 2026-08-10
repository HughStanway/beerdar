import { describe, it, expect } from 'vitest';
import {
  calculateBearing,
  calculateHaversineDistance,
  calculateWalkingTimeMinutes,
  formatDistance,
  normalizeAngle,
  computeRelativeBearing,
  interpolateAngle
} from './geo';

describe('Geospatial Math & Compass Tracking Utilities', () => {
  it('should calculate static bearing between two coordinates', () => {
    // Distance between London Eye (51.5033, -0.1195) and Big Ben (51.5007, -0.1246)
    const bearing = calculateBearing(51.5033, -0.1195, 51.5007, -0.1246);
    expect(bearing).toBeGreaterThanOrEqual(230);
    expect(bearing).toBeLessThanOrEqual(250);
  });

  it('should calculate Haversine distance in meters', () => {
    const dist = calculateHaversineDistance(51.5033, -0.1195, 51.5007, -0.1246);
    expect(dist).toBeGreaterThanOrEqual(440);
    expect(dist).toBeLessThanOrEqual(500);
  });

  it('should calculate walking time in minutes based on 80m/min pace', () => {
    expect(calculateWalkingTimeMinutes(480)).toBe(6);
    expect(calculateWalkingTimeMinutes(50)).toBe(1);
    expect(calculateWalkingTimeMinutes(0)).toBe(1);
  });

  it('should format distance into readable string', () => {
    expect(formatDistance(450)).toBe('450M');
    expect(formatDistance(1500)).toBe('1.5KM');
  });

  it('should normalize angles into 0..360 range', () => {
    expect(normalizeAngle(0)).toBe(0);
    expect(normalizeAngle(360)).toBe(0);
    expect(normalizeAngle(-45)).toBe(315);
    expect(normalizeAngle(405)).toBe(45);
  });

  it('should compute relative bearing relative to device heading', () => {
    // Target is at 90° (East), phone pointing at 45° (NE) -> relative needle is 45°
    expect(computeRelativeBearing(90, 45)).toBe(45);
    // Target is at 45°, phone pointing at 90° -> relative needle is 315° (-45°)
    expect(computeRelativeBearing(45, 90)).toBe(315);
  });

  it('should smoothly interpolate angles across the 0/360 boundary', () => {
    // Current 355°, target 5° -> diff +10° -> interpolated step
    const step1 = interpolateAngle(355, 5, 0.5);
    expect(step1).toBe(0);

    // Current 5°, target 355° -> diff -10° -> interpolated step
    const step2 = interpolateAngle(5, 355, 0.5);
    expect(step2).toBe(0);
  });
});
