<script lang="ts">
  import type { Venue } from '../types';
  import { MapPin, Footprints, ExternalLink, Clock, Beer, Trophy, Zap } from '@lucide/svelte';

  export let venue: Venue;
  export let bearing: number;
</script>

<div class="w-full pixel-container p-5 sm:p-6 my-4 bg-white relative">
  <!-- Top Arcade Header Bar -->
  <div class="flex items-center justify-between gap-2 mb-4 pb-3 border-b-4 border-black">
    <div class="pixel-badge bg-amber-400 text-black px-2.5 py-1 flex items-center gap-1.5 font-bold">
      <Trophy class="w-3.5 h-3.5" />
      <span>PRIMARY TARGET</span>
    </div>
    <div class="pixel-badge bg-emerald-300 text-black px-2 py-1 font-bold text-[9px]">
      DIR: {bearing}°
    </div>
  </div>

  <!-- Venue Name & Type -->
  <div class="mb-4">
    <h2 class="text-xl sm:text-2xl font-black text-black leading-tight tracking-tight uppercase">
      {venue.name}
    </h2>
    <div class="inline-block mt-2 px-2 py-0.5 bg-black text-amber-300 text-xs font-heading uppercase">
      TYPE: {venue.type}
    </div>
  </div>

  <!-- Address Info -->
  {#if venue.address}
    <div class="mb-4 p-2 bg-amber-50 border-2 border-black text-xs font-mono text-black flex items-start gap-2">
      <MapPin class="w-4 h-4 text-black shrink-0 mt-0.5" />
      <span>
        {[venue.address.street, venue.address.city, venue.address.postcode].filter(Boolean).join(', ')}
      </span>
    </div>
  {/if}

  <!-- Opening Hours Badge -->
  {#if venue.opening_status?.raw}
    <div class="mb-4 p-2 bg-cyan-100 border-2 border-black text-xs font-mono text-black flex items-center gap-2">
      <Clock class="w-4 h-4 text-black shrink-0" />
      <span class="truncate font-semibold">{venue.opening_status.raw}</span>
    </div>
  {/if}

  <!-- Metrics Grid -->
  <div class="grid grid-cols-2 gap-3 mb-5">
    <div class="pixel-card p-3 flex items-center gap-3">
      <div class="w-8 h-8 bg-black text-amber-400 border-2 border-black flex items-center justify-center font-bold">
        <MapPin class="w-4 h-4" />
      </div>
      <div>
        <div class="text-[9px] font-heading uppercase text-black font-bold">DISTANCE</div>
        <div class="text-sm font-bold font-mono text-black">
          {venue.distance_meters < 1000 ? `${venue.distance_meters} M` : `${(venue.distance_meters/1000).toFixed(2)} KM`}
        </div>
      </div>
    </div>

    <div class="pixel-card-green p-3 flex items-center gap-3">
      <div class="w-8 h-8 bg-black text-emerald-400 border-2 border-black flex items-center justify-center font-bold">
        <Footprints class="w-4 h-4" />
      </div>
      <div>
        <div class="text-[9px] font-heading uppercase text-black font-bold">WALK TIME</div>
        <div class="text-sm font-bold font-mono text-black">
          ~{venue.walking_time_minutes} MIN
        </div>
      </div>
    </div>
  </div>

  <!-- Navigation Button -->
  <a
    href={venue.maps_url}
    target="_blank"
    rel="noopener noreferrer"
    class="w-full py-3 px-4 pixel-button flex items-center justify-center gap-2 text-center text-black uppercase"
  >
    <span>NAVIGATE GOOGLE MAPS</span>
    <ExternalLink class="w-4 h-4" />
  </a>
</div>
