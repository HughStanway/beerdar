<script lang="ts">
  import type { Venue } from '../types';
  import { MapPin, Footprints, ExternalLink, ListFilter } from '@lucide/svelte';

  export let alternatives: Venue[] = [];
</script>

{#if alternatives && alternatives.length > 0}
  <div class="w-full mt-6">
    <div class="flex items-center justify-between mb-3 px-1 border-b-2 border-black pb-1">
      <h3 class="text-xs font-heading font-bold text-black uppercase tracking-wider flex items-center gap-1.5">
        <ListFilter class="w-4 h-4" />
        MORE TARGETS IN RANGE
      </h3>
      <span class="pixel-badge px-1.5 py-0.5 bg-black text-amber-300 font-bold">{alternatives.length}</span>
    </div>

    <div class="space-y-3">
      {#each alternatives as venue, idx}
        <div class="pixel-card-cyan p-3 flex items-center justify-between gap-3">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span class="px-1.5 py-0.5 bg-black text-white text-[9px] font-heading font-bold">
                #{idx + 2}
              </span>
              <h4 class="text-sm font-bold text-black truncate uppercase">{venue.name}</h4>
            </div>

            <div class="flex items-center gap-3 text-xs font-mono text-slate-800 mt-1">
              <span class="font-bold">
                {venue.distance_meters < 1000 ? `${venue.distance_meters}M` : `${(venue.distance_meters/1000).toFixed(1)}KM`}
              </span>
              <span>•</span>
              <span>~{venue.walking_time_minutes} MIN WALK</span>
            </div>
          </div>

          <a
            href={venue.maps_url}
            target="_blank"
            rel="noopener noreferrer"
            class="pixel-button p-2 text-black flex items-center justify-center shrink-0"
            title="Open directions"
          >
            <ExternalLink class="w-4 h-4" />
          </a>
        </div>
      {/each}
    </div>
  </div>
{/if}
