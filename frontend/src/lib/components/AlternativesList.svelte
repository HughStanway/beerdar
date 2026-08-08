<script lang="ts">
  import type { Venue } from '../types';
  import { MapPin, Footprints, ExternalLink, ListFilter, ChevronDown, ChevronUp, Clock, Compass } from '@lucide/svelte';
  import { slide } from 'svelte/transition';

  export let alternatives: Venue[] = [];

  // Track which alternative card is currently expanded
  let expandedVenueId: string | null = null;

  function toggleExpand(id: string) {
    if (expandedVenueId === id) {
      expandedVenueId = null;
    } else {
      expandedVenueId = id;
    }
  }
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
        {@const isExpanded = expandedVenueId === venue.id}
        
        <div 
          class="pixel-card-cyan transition-all duration-150 overflow-hidden"
          class:bg-amber-100={isExpanded}
        >
          <!-- Card Header Click Area -->
          <button 
            type="button"
            on:click={() => toggleExpand(venue.id)}
            class="group w-full p-3 flex items-center justify-between gap-3 text-left focus:outline-none cursor-pointer"
            aria-expanded={isExpanded}
          >
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="px-1.5 py-0.5 bg-black text-amber-300 text-[9px] font-heading font-bold">
                  #{idx + 2}
                </span>
                <h4 class="text-sm font-bold text-black truncate uppercase group-hover:text-amber-800 transition-colors">{venue.name}</h4>
              </div>

              <div class="flex items-center gap-2.5 text-xs font-mono text-slate-800 mt-1">
                <span class="font-bold">
                  {venue.distance_meters < 1000 ? `${venue.distance_meters}M` : `${(venue.distance_meters/1000).toFixed(1)}KM`}
                </span>
                <span>•</span>
                <span>~{venue.walking_time_minutes} MIN WALK</span>
              </div>
            </div>

            <!-- Expand Toggle Icon Button (Responsive Hover & Active Effects) -->
            <div class="w-8 h-8 pixel-icon-button flex items-center justify-center text-black shrink-0">
              {#if isExpanded}
                <ChevronUp class="w-4 h-4 stroke-[3]" />
              {:else}
                <ChevronDown class="w-4 h-4 stroke-[3]" />
              {/if}
            </div>
          </button>

          <!-- Expanded Sliding Details Panel -->
          {#if isExpanded}
            <div 
              transition:slide={{ duration: 250 }}
              class="px-3 pb-4 pt-1 border-t-2 border-black bg-white"
            >
              <!-- Type & Status Badges -->
              <div class="flex flex-wrap items-center justify-between gap-2 my-2">
                <span class="px-2 py-0.5 bg-black text-amber-300 text-xs font-heading uppercase">
                  TYPE: {venue.type}
                </span>
                <span class="px-2 py-0.5 bg-emerald-200 border-2 border-black text-black text-[10px] font-heading uppercase">
                  TARGET #{idx + 2}
                </span>
              </div>

              <!-- Address Info -->
              {#if venue.address}
                <div class="my-2.5 p-2 bg-amber-50 border-2 border-black text-xs font-mono text-black flex items-start gap-2">
                  <MapPin class="w-4 h-4 text-black shrink-0 mt-0.5" />
                  <span>
                    {[venue.address.street, venue.address.city, venue.address.postcode].filter(Boolean).join(', ')}
                  </span>
                </div>
              {/if}

              <!-- Opening Hours -->
              {#if venue.opening_status?.raw}
                <div class="my-2.5 p-2 bg-cyan-100 border-2 border-black text-xs font-mono text-black flex items-center gap-2">
                  <Clock class="w-4 h-4 text-black shrink-0" />
                  <span class="truncate font-semibold">{venue.opening_status.raw}</span>
                </div>
              {/if}

              <!-- Detailed Metrics Grid -->
              <div class="grid grid-cols-2 gap-2.5 my-3">
                <div class="pixel-card p-2.5 flex items-center gap-2.5">
                  <div class="w-7 h-7 bg-black text-amber-400 border-2 border-black flex items-center justify-center font-bold shrink-0">
                    <MapPin class="w-3.5 h-3.5" />
                  </div>
                  <div class="min-w-0">
                    <div class="text-[8px] font-heading uppercase text-black font-bold">DISTANCE</div>
                    <div class="text-xs font-bold font-mono text-black truncate">
                      {venue.distance_meters < 1000 ? `${venue.distance_meters} M` : `${(venue.distance_meters/1000).toFixed(2)} KM`}
                    </div>
                  </div>
                </div>

                <div class="pixel-card-green p-2.5 flex items-center gap-2.5">
                  <div class="w-7 h-7 bg-black text-emerald-400 border-2 border-black flex items-center justify-center font-bold shrink-0">
                    <Footprints class="w-3.5 h-3.5" />
                  </div>
                  <div class="min-w-0">
                    <div class="text-[8px] font-heading uppercase text-black font-bold">WALK TIME</div>
                    <div class="text-xs font-bold font-mono text-black truncate">
                      ~{venue.walking_time_minutes} MIN
                    </div>
                  </div>
                </div>
              </div>

              <!-- Coordinates Info -->
              {#if venue.coordinates}
                <div class="my-2 text-[10px] font-mono text-slate-700 flex items-center gap-1 font-bold">
                  <Compass class="w-3 h-3 text-black" />
                  <span>GPS: {venue.coordinates.latitude.toFixed(4)}, {venue.coordinates.longitude.toFixed(4)}</span>
                </div>
              {/if}

              <!-- Navigation Button -->
              <a
                href={venue.maps_url}
                target="_blank"
                rel="noopener noreferrer"
                class="w-full mt-2.5 py-2.5 px-3 pixel-button flex items-center justify-center gap-2 text-center text-black text-xs uppercase"
              >
                <span>NAVIGATE GOOGLE MAPS</span>
                <ExternalLink class="w-3.5 h-3.5" />
              </a>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
{/if}
