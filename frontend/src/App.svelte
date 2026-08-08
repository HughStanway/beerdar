<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { NearestResponse } from './lib/types';
  import { calculateBearing } from './lib/geo';
  import Navbar from './lib/components/Navbar.svelte';
  import Compass from './lib/components/Compass.svelte';
  import HeroCard from './lib/components/HeroCard.svelte';
  import AlternativesList from './lib/components/AlternativesList.svelte';
  import { MapPin, AlertTriangle, RefreshCw, Compass as CompassIcon, Sparkles, Zap, ShieldAlert } from '@lucide/svelte';

  let loading = true;
  let error: string | null = null;
  let userLat: number | null = null;
  let userLon: number | null = null;
  let responseData: NearestResponse | null = null;
  let bearing = 0;
  let loadingSeconds = 0;
  let timerInterval: any = null;

  // Preset locations
  const DEMO_PRESETS = [
    { name: 'Central London (Covent Garden)', lat: 51.5117, lon: -0.124 },
    { name: 'Ware, Hertfordshire', lat: 51.8115, lon: -0.0298 },
    { name: 'Manchester (Northern Quarter)', lat: 53.4831, lon: -2.2355 }
  ];

  function startTimer() {
    loadingSeconds = 0;
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      loadingSeconds += 1;
    }, 1000);
  }

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
  }

  async function fetchNearest(lat: number, lon: number) {
    loading = true;
    error = null;
    startTimer();

    // 15 second client abort controller fallback
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    try {
      const res = await fetch(`/api/v1/nearest?lat=${lat}&lon=${lon}&limit=5`, {
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!res.ok) {
        let errorDetail = `SERVER ERROR ${res.status}`;
        try {
          const errBody = await res.json();
          if (errBody && errBody.detail) {
            errorDetail = errBody.detail;
          }
        } catch (_) {}
        throw new Error(errorDetail);
      }

      const data: NearestResponse = await res.json();
      responseData = data;

      if (data.primary_venue) {
        bearing = calculateBearing(
          lat,
          lon,
          data.primary_venue.coordinates.latitude,
          data.primary_venue.coordinates.longitude
        );
      }
    } catch (err: any) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        error = 'RADAR TIMEOUT (10s): Public Overpass API server took too long to respond. Try clicking a demo zone below or retrying.';
      } else {
        error = err.message || 'SERVER CONNECTION FAILURE';
      }
    } finally {
      stopTimer();
      loading = false;
    }
  }

  function requestLocation() {
    loading = true;
    error = null;
    startTimer();

    if (!navigator.geolocation) {
      error = 'GEOLOCATION NOT SUPPORTED BY BROWSER';
      stopTimer();
      loading = false;
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userLat = pos.coords.latitude;
        userLon = pos.coords.longitude;
        fetchNearest(userLat, userLon);
      },
      (geoErr) => {
        console.warn('Geolocation permission/error:', geoErr);
        error = `GPS ACCESS DENIED: ${geoErr.message.toUpperCase()}. PICK DEMO ZONE BELOW.`;
        stopTimer();
        loading = false;
      },
      { enableHighAccuracy: true, timeout: 8000, maximumAge: 30000 }
    );
  }

  function loadPreset(lat: number, lon: number) {
    userLat = lat;
    userLon = lon;
    fetchNearest(lat, lon);
  }

  onMount(() => {
    requestLocation();
  });

  onDestroy(() => {
    stopTimer();
  });
</script>

<div class="min-h-screen flex flex-col items-center justify-between p-3 sm:p-6 max-w-xl mx-auto">
  <Navbar {loading} onRefresh={requestLocation} />

  <main class="w-full flex-1 flex flex-col items-center justify-start">
    {#if loading}
      <!-- Retro Arcade Loading Screen with Live Seconds Counter -->
      <div class="w-full pixel-container p-8 my-8 text-center flex flex-col items-center justify-center bg-white shadow-[6px_6px_0px_#000]">
        <div class="w-20 h-20 bg-amber-300 border-4 border-black flex items-center justify-center mb-6 shadow-[4px_4px_0px_#000]">
          <CompassIcon class="w-10 h-10 text-black animate-spin" />
        </div>
        <h2 class="text-xs sm:text-sm font-heading text-black uppercase animate-blink">SCANNING SATELLITE RADAR...</h2>
        <p class="text-xs font-mono text-slate-800 mt-2 font-bold bg-amber-100 px-3 py-1 border-2 border-black inline-block">
          TIME ELAPSED: {loadingSeconds}s / 10s
        </p>
        <p class="text-[10px] font-mono text-slate-500 mt-3">[ QUERYING OPENSTREETMAP OVERPASS NODES ]</p>
      </div>
    {:else if error}
      <!-- Retro Error Screen with Explicit Feedback -->
      <div class="w-full pixel-container p-6 text-center my-6 bg-rose-100 border-4 border-black shadow-[6px_6px_0px_#000]">
        <div class="w-12 h-12 bg-black text-rose-400 border-2 border-black flex items-center justify-center mx-auto mb-3 shadow-[2px_2px_0px_#000]">
          <ShieldAlert class="w-7 h-7 text-rose-500" />
        </div>
        <h3 class="text-xs sm:text-sm font-heading font-bold text-black mb-2 uppercase">RADAR SYSTEM ALERT</h3>

        <!-- Clear Error Feedback Message Box -->
        <div class="text-xs font-mono text-slate-900 mb-5 bg-white p-3 border-3 border-black font-bold text-left leading-relaxed shadow-[3px_3px_0px_#000]">
          <div class="text-[10px] font-heading text-rose-700 uppercase mb-1">ERROR DETAILS:</div>
          {error}
        </div>

        <button
          on:click={requestLocation}
          class="w-full py-3 px-4 pixel-button mb-4 flex items-center justify-center gap-2"
        >
          <RefreshCw class="w-4 h-4" />
          <span>RETRY LIVE GPS RADAR</span>
        </button>

        <div class="border-t-4 border-black pt-4 mt-2">
          <p class="text-[10px] font-heading text-black uppercase mb-3">SELECT DEMO ZONE INSTANT LOAD:</p>
          <div class="flex flex-col gap-2">
            {#each DEMO_PRESETS as preset}
              <button
                on:click={() => loadPreset(preset.lat, preset.lon)}
                class="w-full p-2.5 bg-white border-2 border-black hover:bg-amber-300 text-xs font-mono text-black font-bold flex items-center justify-between transition-all shadow-[2px_2px_0px_#000]"
              >
                <span class="truncate">{preset.name}</span>
                <MapPin class="w-4 h-4 text-black shrink-0 ml-2" />
              </button>
            {/each}
          </div>
        </div>
      </div>
    {:else if responseData}
      {#if responseData.primary_venue}
        <!-- Retro Compass -->
        <Compass
          {bearing}
          distanceMeters={responseData.primary_venue.distance_meters}
          walkingTimeMinutes={responseData.primary_venue.walking_time_minutes}
        />

        <!-- Primary Hero Card -->
        <HeroCard venue={responseData.primary_venue} {bearing} />

        <!-- Alternatives List -->
        <AlternativesList alternatives={responseData.alternatives} />
      {:else}
        <!-- No Venues Found -->
        <div class="w-full pixel-container p-8 text-center my-6 bg-amber-100 border-4 border-black shadow-[6px_6px_0px_#000]">
          <MapPin class="w-10 h-10 text-black mx-auto mb-3" />
          <h3 class="text-xs font-heading font-bold text-black uppercase">NO PUBS FOUND IN ZONE</h3>
          <p class="text-xs font-mono text-slate-700 mt-2 font-bold">Try increasing search radius or picking another zone.</p>
        </div>
      {/if}
    {/if}
  </main>

  <!-- Retro Arcade Footer -->
  <footer class="w-full max-w-xl mx-auto px-4 mt-8 mb-6">
    <div class="w-full py-3.5 px-4 text-center text-[10px] font-heading text-black border-4 border-black bg-white shadow-[4px_4px_0px_#000]">
      <span>PUBFINDER BEER RADAR • ACQUIRE GPS TO CONTINUE</span>
    </div>
  </footer>
</div>
