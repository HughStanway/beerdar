<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { Radio, Zap } from '@lucide/svelte';
  import { calculateShortestAngleDiff, normalizeAngle, formatDistance } from '../geo';

  export let bearing: number = 0; // Target bearing from user location to target pub (0..360)
  export let distanceMeters: number = 0;
  export let walkingTimeMinutes: number = 0;

  let targetHeading: number | null = null;
  let currentDisplayHeading: number = 0;
  let isSensorActive: boolean = false;
  let permissionNeeded: boolean = false;
  let animationFrameId: number | null = null;

  function handleOrientation(event: any) {
    let heading: number | null = null;

    if (event.webkitCompassHeading !== undefined && event.webkitCompassHeading !== null) {
      // iOS Safari (webkitCompassHeading: 0..360 magnetic north)
      heading = event.webkitCompassHeading;
    } else if (event.alpha !== undefined && event.alpha !== null) {
      // Android / Chrome (360 - alpha for absolute compass heading)
      heading = (360 - event.alpha) % 360;
    }

    if (heading !== null && !isNaN(heading)) {
      targetHeading = normalizeAngle(heading);
      isSensorActive = true;
    }
  }

  async function requestPermission() {
    if (
      typeof (DeviceOrientationEvent as any) !== 'undefined' &&
      typeof (DeviceOrientationEvent as any).requestPermission === 'function'
    ) {
      try {
        const permissionState = await (DeviceOrientationEvent as any).requestPermission();
        if (permissionState === 'granted') {
          permissionNeeded = false;
          window.addEventListener('deviceorientation', handleOrientation, true);
        }
      } catch (err) {
        console.warn('Compass sensor permission error:', err);
      }
    } else {
      window.addEventListener('deviceorientation', handleOrientation, true);
    }
  }

  function updateSmoothAnimation() {
    if (targetHeading !== null) {
      const diff = calculateShortestAngleDiff(currentDisplayHeading, targetHeading);
      currentDisplayHeading = normalizeAngle(currentDisplayHeading + diff * 0.15);
    }
    animationFrameId = requestAnimationFrame(updateSmoothAnimation);
  }

  onMount(() => {
    if (
      typeof (DeviceOrientationEvent as any) !== 'undefined' &&
      typeof (DeviceOrientationEvent as any).requestPermission === 'function'
    ) {
      permissionNeeded = true;
    } else if ('ondeviceorientation' in window || 'ondeviceorientationabsolute' in window) {
      window.addEventListener('deviceorientationabsolute', handleOrientation, true);
      window.addEventListener('deviceorientation', handleOrientation, true);
    }

    animationFrameId = requestAnimationFrame(updateSmoothAnimation);
  });

  onDestroy(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('deviceorientationabsolute', handleOrientation, true);
      window.removeEventListener('deviceorientation', handleOrientation, true);
    }
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId);
    }
  });

  // Dial rotation: North always points to physical True North (-heading)
  $: dialRotation = isSensorActive && targetHeading !== null
    ? normalizeAngle(-currentDisplayHeading)
    : 0;

  // Needle rotation: Red tip points directly to target pub relative to phone top edge
  $: needleRotation = isSensorActive && targetHeading !== null
    ? normalizeAngle(bearing - currentDisplayHeading)
    : bearing;
</script>

<div class="relative flex flex-col items-center justify-center p-4 my-2">
  <!-- Top Live Sensor Status Badge / Interactive Trigger -->
  <div class="mb-3 flex items-center gap-2">
    {#if isSensorActive}
      <div class="pixel-badge px-2 py-0.5 bg-emerald-300 text-black font-bold flex items-center gap-1.5 text-[9px]">
        <span class="w-2 h-2 bg-emerald-700 animate-ping inline-block"></span>
        <span>COMPASS: SENSOR LIVE</span>
      </div>
    {:else if permissionNeeded}
      <button
        type="button"
        on:click={requestPermission}
        class="pixel-button px-2.5 py-1 text-black font-bold flex items-center gap-1 text-[9px] animate-pulse"
      >
        <Zap class="w-3 h-3" />
        <span>ENABLE LIVE COMPASS</span>
      </button>
    {:else}
      <div class="pixel-badge px-2 py-0.5 bg-amber-200 text-black font-bold flex items-center gap-1 text-[9px]">
        <Radio class="w-3 h-3" />
        <span>COMPASS: STATIC MODE</span>
      </div>
    {/if}
  </div>

  <!-- Retro Blocky Compass Circle Container -->
  <div class="relative w-48 h-48 bg-white border-4 border-black shadow-[6px_6px_0px_#000] flex items-center justify-center p-2 overflow-hidden">
    <!-- Grid Crosshair Lines -->
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
      <div class="w-full h-[2px] bg-slate-300"></div>
      <div class="h-full w-[2px] bg-slate-300 absolute"></div>
    </div>

    <!-- SIBLING 1: Outer Rotating Dial Circle for Cardinal Directions (North points to True North) -->
    <div 
      class="w-36 h-36 border-2 border-dashed border-black rounded-full flex items-center justify-center absolute pointer-events-none"
      style="transform: rotate({dialRotation}deg);"
    >
      <!-- Cardinal Directions (Retro Font) -->
      <span class="absolute -top-4 font-heading text-[10px] font-bold text-red-600 bg-white px-1 border border-black">N</span>
      <span class="absolute -right-4 font-heading text-[10px] font-bold text-black bg-white px-1 border border-black">E</span>
      <span class="absolute -bottom-4 font-heading text-[10px] font-bold text-black bg-white px-1 border border-black">S</span>
      <span class="absolute -left-4 font-heading text-[10px] font-bold text-black bg-white px-1 border border-black">W</span>
    </div>

    <!-- SIBLING 2: Inner Rotating Pixel Arrow Needle (Red tip points directly at target Pub) -->
    <div
      class="absolute flex items-center justify-center pointer-events-none"
      style="transform: rotate({needleRotation}deg);"
    >
      <div class="relative flex flex-col items-center">
        <!-- Red Arrow Tip (Points towards Pub) -->
        <div class="w-0 h-0 border-l-[12px] border-l-transparent border-r-[12px] border-r-transparent border-b-[24px] border-b-red-600 filter drop-shadow-[2px_2px_0px_#000]"></div>
        <!-- Black Tail -->
        <div class="w-0 h-0 border-l-[12px] border-l-transparent border-r-[12px] border-r-transparent border-t-[24px] border-t-black"></div>
      </div>
    </div>
  </div>

  <!-- Distance & Bearing Badges -->
  <div class="mt-4 flex flex-wrap justify-center items-center gap-2">
    <div class="pixel-badge px-2.5 py-1 bg-amber-300 text-black font-bold">
      BEARING: {Math.round(bearing)}°
    </div>
    <div class="pixel-badge px-2.5 py-1 bg-cyan-200 text-black font-bold">
      DIST: {formatDistance(distanceMeters)}
    </div>
    <div class="pixel-badge px-2.5 py-1 bg-emerald-200 text-black font-bold">
      WALK: ~{walkingTimeMinutes} MIN
    </div>
  </div>
</div>
