<script lang="ts">
  import { Navigation, Compass as CompassIcon } from '@lucide/svelte';

  export let bearing: number = 0;
  export let distanceMeters: number = 0;
  export let walkingTimeMinutes: number = 0;
</script>

<div class="relative flex flex-col items-center justify-center p-4 my-2">
  <!-- Retro Blocky Compass Circle Container -->
  <div class="relative w-48 h-48 bg-white border-4 border-black shadow-[6px_6px_0px_#000] flex items-center justify-center p-2">
    <!-- Grid Crosshair Lines -->
    <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
      <div class="w-full h-[2px] bg-slate-300"></div>
      <div class="h-full w-[2px] bg-slate-300 absolute"></div>
    </div>

    <!-- Inner Circle Border -->
    <div class="w-36 h-36 border-2 border-dashed border-black rounded-full flex items-center justify-center relative">
      <!-- Cardinal Directions (Retro Font) -->
      <span class="absolute -top-4 font-heading text-[10px] font-bold text-red-600 bg-white px-1 border border-black">N</span>
      <span class="absolute -right-4 font-heading text-[10px] font-bold text-black bg-white px-1 border border-black">E</span>
      <span class="absolute -bottom-4 font-heading text-[10px] font-bold text-black bg-white px-1 border border-black">S</span>
      <span class="absolute -left-4 font-heading text-[10px] font-bold text-black bg-white px-1 border border-black">W</span>

      <!-- Rotating Pixel Arrow Needle -->
      <div
        class="transition-transform duration-500 ease-out flex items-center justify-center"
        style="transform: rotate({bearing}deg);"
      >
        <div class="relative flex flex-col items-center">
          <div class="w-0 h-0 border-l-[12px] border-l-transparent border-r-[12px] border-r-transparent border-b-[24px] border-b-red-600 filter drop-shadow-[2px_2px_0px_#000]"></div>
          <div class="w-0 h-0 border-l-[12px] border-l-transparent border-r-[12px] border-r-transparent border-t-[24px] border-t-black"></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Distance & Bearing Badges -->
  <div class="mt-4 flex flex-wrap justify-center items-center gap-2">
    <div class="pixel-badge px-2.5 py-1 bg-amber-300 text-black font-bold">
      BEARING: {bearing}°
    </div>
    <div class="pixel-badge px-2.5 py-1 bg-cyan-200 text-black font-bold">
      DIST: {distanceMeters < 1000 ? `${distanceMeters}M` : `${(distanceMeters/1000).toFixed(1)}KM`}
    </div>
    <div class="pixel-badge px-2.5 py-1 bg-emerald-200 text-black font-bold">
      WALK: ~{walkingTimeMinutes} MIN
    </div>
  </div>
</div>
