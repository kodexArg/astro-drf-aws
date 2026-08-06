<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]]
     LIVE-DOC:END -->

<!--
  Seven color rows of ONE palette — canvas, dots, surface, foreground,
  primary, secondary, accent. ThemeCard mounts it once per mode.
  Text fields show sRGB hex digits (static `#` + 6-ch input); storage
  accepts `#rrggbb` (and packs may still hold oklch until edited).
-->
<script lang="ts">
  import { Label } from "$lib/components/ui/label";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import {
    COLOR_KEYS,
    sanitizeHexDigits,
    toHexDigits,
    type ThemeColors,
  } from "$lib/theme";
  import { t } from "../../../i18n";
  import type { MessageKey } from "../../../i18n";

  let {
    palette = $bindable<ThemeColors>({}),
    disabled = false,
    idPrefix = "palette",
  }: {
    palette?: ThemeColors;
    disabled?: boolean;
    idPrefix?: string;
  } = $props();

  /** Focus-scoped buffer so incomplete hex does not snap back mid-edit. */
  let editingKey = $state<keyof ThemeColors | null>(null);
  let draftDigits = $state("");

  const COLOR_LABELS: Record<keyof ThemeColors, MessageKey> = {
    canvas: "appearance_color_canvas",
    dots: "appearance_color_dots",
    surface: "appearance_color_surface",
    foreground: "appearance_color_foreground",
    primary: "appearance_color_primary",
    secondary: "appearance_color_secondary",
    accent: "appearance_color_accent",
  };

  function swatch(value: string | undefined): string {
    const digits = toHexDigits(value);
    return digits ? `#${digits}` : "#888888";
  }

  function displayDigits(key: keyof ThemeColors): string {
    if (editingKey === key) return draftDigits;
    return toHexDigits(palette[key]);
  }

  function setKey(key: keyof ThemeColors, value: string): void {
    if (editingKey === key) {
      editingKey = null;
      draftDigits = "";
    }
    palette = { ...palette, [key]: value };
  }

  function clearKey(key: keyof ThemeColors): void {
    if (editingKey === key) {
      editingKey = null;
      draftDigits = "";
    }
    const next = { ...palette };
    delete next[key];
    palette = next;
  }

  function beginEdit(key: keyof ThemeColors): void {
    editingKey = key;
    draftDigits = toHexDigits(palette[key]);
  }

  function endEdit(key: keyof ThemeColors): void {
    if (editingKey !== key) return;
    editingKey = null;
    draftDigits = "";
  }

  function onHexInput(key: keyof ThemeColors, raw: string): void {
    const cleaned = sanitizeHexDigits(raw);
    if (cleaned.length === 0) {
      clearKey(key);
      return;
    }
    if (cleaned.length === 6) {
      setKey(key, `#${cleaned}`);
      return;
    }
    editingKey = key;
    draftDigits = cleaned;
  }

  function onSwatchInput(key: keyof ThemeColors, value: string): void {
    const digits = toHexDigits(value) || sanitizeHexDigits(value.replace(/^#/, ""));
    if (digits.length === 6) setKey(key, `#${digits}`);
  }
</script>

<div class="flex flex-col gap-3">
  {#each COLOR_KEYS as key (key)}
    <div class="flex flex-col gap-1.5">
      <Label for={`${idPrefix}-${key}`}>{t(COLOR_LABELS[key])}</Label>
      <div class="flex min-w-0 flex-wrap items-center gap-2">
        <input
          type="color"
          aria-label={t(COLOR_LABELS[key])}
          value={swatch(palette[key])}
          oninput={(e) => onSwatchInput(key, (e.currentTarget as HTMLInputElement).value)}
          {disabled}
          class="color-swatch h-9 w-9 shrink-0 cursor-pointer rounded-md border border-input disabled:cursor-not-allowed disabled:opacity-50"
        />
        <div class="flex shrink-0 items-center gap-0.5">
          <span class="select-none font-mono text-sm text-muted-foreground" aria-hidden="true">#</span>
          <Input
            id={`${idPrefix}-${key}`}
            placeholder="rrggbb"
            spellcheck={false}
            autocomplete="off"
            maxlength={6}
            size={6}
            value={displayDigits(key)}
            onfocus={() => beginEdit(key)}
            onblur={() => endEdit(key)}
            oninput={(e) => onHexInput(key, (e.currentTarget as HTMLInputElement).value)}
            {disabled}
            class="box-content w-[6ch] min-w-[6ch] max-w-[6ch] shrink-0 px-1.5 font-mono uppercase"
            aria-label={`# ${t(COLOR_LABELS[key])}`}
          />
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          class="shrink-0"
          onclick={() => clearKey(key)}
          {disabled}
          aria-label={t("appearance_color_clear")}
        >
          ×
        </Button>
      </div>
    </div>
  {/each}
</div>

<style>
  /* Kill the UA color-input chrome (inset swatch + padding) — solid square only. */
  input.color-swatch {
    appearance: none;
    -webkit-appearance: none;
    padding: 0;
    overflow: hidden;
    background: transparent;
  }

  input.color-swatch::-webkit-color-swatch-wrapper {
    padding: 0;
  }

  input.color-swatch::-webkit-color-swatch {
    border: none;
    border-radius: 0;
  }

  input.color-swatch::-moz-color-swatch {
    border: none;
    border-radius: 0;
  }
</style>
