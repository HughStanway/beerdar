<script lang="ts">
  import { Beer, RefreshCw, Radio, Gamepad2 } from '@lucide/svelte';

  export let loading: boolean = false;
  export let onRefresh: () => void;
</script>

<header class="w-full max-w-xl mx-auto py-3 px-4 flex items-center justify-between border-b-4 border-black mb-4 bg-white shadow-[4px_4px_0px_#000]">
  <!-- Arcade Title -->
  <div class="flex items-center gap-2.5">
    <div class="w-9 h-9 bg-amber-400 border-2 border-black flex items-center justify-center text-black font-bold shadow-[2px_2px_0px_#000]">
      <Beer class="w-5 h-5 fill-black" />
    </div>
    <div>
      <h1 class="text-sm sm:text-base font-heading font-black tracking-tighter text-black flex items-center gap-1.5">
        PUBFINDER
        <span class="text-[9px] bg-black text-amber-300 px-1 py-0.5 font-mono uppercase">8-BIT RADAR</span>
      </h1>
      <p class="text-[10px] text-slate-700 font-mono font-bold">STATELESS SPA • PWA</p>
    </div>
  </div>

  <!-- Actions & Status -->
  <div class="flex items-center gap-2">
    <!-- Live Status -->
    <div class="hidden sm:flex items-center gap-1 text-[10px] font-heading bg-emerald-200 text-black px-2 py-1 border-2 border-black">
      <span class="w-2 h-2 bg-emerald-600 rounded-none animate-ping inline-block"></span>
      <span>P1 ONLINE</span>
    </div>

    <!-- Relocate Button -->
    <button
      on:click={onRefresh}
      disabled={loading}
      class="pixel-button px-3 py-1.5 flex items-center gap-1 text-black font-heading text-[10px]"
      title="Relocate & Refresh"
    >
      <RefreshCw class="w-3.5 h-3.5 {loading ? 'animate-spin' : ''}" />
      <span>GPS</span>
    </button>
  </div>
</header>
