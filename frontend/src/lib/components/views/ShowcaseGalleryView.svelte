<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]] · [[adr-23-showcase-ready-components]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]] · [[COMPONENTIZATION]]
     LIVE-DOC:END -->

<script lang="ts">
  import { Button } from "$lib/components/ui/button";
  import { Badge } from "$lib/components/ui/badge";
  import * as Alert from "$lib/components/ui/alert";
  import { Separator } from "$lib/components/ui/separator";
  import { SectionTitle } from "$lib/components/primitives/titles";
  import { NumericValue, StatusBadge } from "$lib/components/data";
  import { EntityGrid, EntityCard, SummaryCard, type EntityStat, type SummaryItem } from "$lib/components/dashboard";
  import type { Snippet } from "svelte";

  type GalleryCopy = {
    title: string;
    intro: string;
    recoTitle: string;
    recoBody: string;
    typography: string;
    typographyNote: string;
    scaleH1: string;
    scaleH2: string;
    scaleH3: string;
    buttonsBadges: string;
    data: string;
    dataTable: string;
    numericValue: string;
    chipFilterBar: string;
    pagination: string;
    collapsible: string;
    tree: string;
    dashboard: string;
    metricTiles: string;
    entityGrid: string;
    summaryCard: string;
    summaryTitle: string;
    chat: string;
    chatNote: string;
    form: string;
    select: string;
    combobox: string;
    checkbox: string;
    switchTitle: string;
    datePicker: string;
    dateRangePicker: string;
    pinInput: string;
    tagsInput: string;
    calendar: string;
    rangeCalendar: string;
    slider: string;
    toggleGroup: string;
    navigation: string;
    tabs: string;
    dropdownMenu: string;
    contextMenu: string;
    menubar: string;
    tableOfContents: string;
    overlay: string;
    accordion: string;
    tooltip: string;
    popover: string;
    hoverCard: string;
    scrollArea: string;
    drawer: string;
    feedback: string;
    progress: string;
    toast: string;
    auth: string;
    theme: string;
    shell: string;
    shellNote: string;
    shellNavDrawer: string;
    shellNavItem: string;
    shellNavBadge: string;
    shellNavbarIcon: string;
    shellSurface: string;
  };

  let {
    entities = [],
    summaryItems = [],
    copy = {} as GalleryCopy,
    "data-table": dataTable,
    "chip-filter-bar": chipFilterBar,
    pagination,
    collapsible,
    tree,
    "metric-tiles": metricTiles,
    select,
    combobox,
    checkbox,
    switch: switchSnippet,
    "date-picker": datePicker,
    "date-range-picker": dateRangePicker,
    "pin-input": pinInput,
    "tags-input": tagsInput,
    calendar,
    "range-calendar": rangeCalendar,
    slider,
    "toggle-group": toggleGroup,
    tabs,
    "dropdown-menu": dropdownMenu,
    "context-menu": contextMenu,
    menubar,
    "table-of-contents": tableOfContents,
    chat,
    "overlay-triggers": overlayTriggers,
    accordion,
    tooltip,
    popover,
    "hover-card": hoverCard,
    "scroll-area": scrollArea,
    drawer,
    progress,
    toast,
    auth,
    "theme-toggle": themeToggle,
    "shell-nav-drawer": shellNavDrawer,
    "shell-nav-item": shellNavItem,
    "shell-nav-badge": shellNavBadge,
    "shell-navbar-icon": shellNavbarIcon,
    "shell-surface": shellSurface,
  }: {
    entities?: { title: string; subtitle: string; stats: EntityStat[]; status: string }[];
    summaryItems?: SummaryItem[];
    copy?: GalleryCopy;
    "data-table"?: Snippet;
    "chip-filter-bar"?: Snippet;
    pagination?: Snippet;
    collapsible?: Snippet;
    tree?: Snippet;
    "metric-tiles"?: Snippet;
    select?: Snippet;
    combobox?: Snippet;
    checkbox?: Snippet;
    switch?: Snippet;
    "date-picker"?: Snippet;
    "date-range-picker"?: Snippet;
    "pin-input"?: Snippet;
    "tags-input"?: Snippet;
    calendar?: Snippet;
    "range-calendar"?: Snippet;
    slider?: Snippet;
    "toggle-group"?: Snippet;
    tabs?: Snippet;
    "dropdown-menu"?: Snippet;
    "context-menu"?: Snippet;
    menubar?: Snippet;
    "table-of-contents"?: Snippet;
    chat?: Snippet;
    "overlay-triggers"?: Snippet;
    accordion?: Snippet;
    tooltip?: Snippet;
    popover?: Snippet;
    "hover-card"?: Snippet;
    "scroll-area"?: Snippet;
    drawer?: Snippet;
    progress?: Snippet;
    toast?: Snippet;
    auth?: Snippet;
    "theme-toggle"?: Snippet;
    "shell-nav-drawer"?: Snippet;
    "shell-nav-item"?: Snippet;
    "shell-nav-badge"?: Snippet;
    "shell-navbar-icon"?: Snippet;
    "shell-surface"?: Snippet;
  } = $props();
</script>

<div class="mx-auto max-w-5xl p-8 flex flex-col gap-8">
  <div class="flex flex-col gap-2">
    <p class="text-muted-foreground">{copy.intro}</p>
  </div>

  <Alert.Root>
    <Alert.Title>{copy.recoTitle}</Alert.Title>
    <Alert.Description>{copy.recoBody}</Alert.Description>
  </Alert.Root>

  <Separator />

  <section class="flex flex-col gap-3">
    <SectionTitle as="h2">{copy.typography}</SectionTitle>
    <p class="text-sm text-muted-foreground">{copy.typographyNote}</p>
    <SectionTitle as="h1">{copy.scaleH1}</SectionTitle>
    <SectionTitle as="h2">{copy.scaleH2}</SectionTitle>
    <SectionTitle as="h3">{copy.scaleH3}</SectionTitle>
  </section>

  <Separator />

  <section class="flex flex-col gap-4">
    <SectionTitle as="h2">{copy.buttonsBadges}</SectionTitle>
    <div class="flex flex-wrap gap-3">
      <Button>Default</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="destructive">Destructive</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link" href="#">Link</Button>
    </div>
    <div class="flex flex-wrap gap-3">
      <Badge>Default</Badge>
      <Badge variant="secondary">Secondary</Badge>
      <Badge variant="destructive">Destructive</Badge>
      <Badge variant="outline">Outline</Badge>
    </div>
    <div class="flex flex-wrap gap-3">
      <StatusBadge status="approved" />
      <StatusBadge status="pending" />
      <StatusBadge status="rejected" />
    </div>
  </section>

  <Separator />

  <section class="flex flex-col gap-6">
    <SectionTitle as="h2">{copy.data}</SectionTitle>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.dataTable}</SectionTitle>
      {@render dataTable?.()}
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.numericValue}</SectionTitle>
      <div class="flex flex-wrap gap-6">
        <NumericValue value={128400} currency="USD" />
        <NumericValue value={-5200} currency="USD" />
      </div>
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.chipFilterBar}</SectionTitle>
      {@render chipFilterBar?.()}
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.pagination}</SectionTitle>
      {@render pagination?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-xl">
      <SectionTitle as="h3">{copy.collapsible}</SectionTitle>
      {@render collapsible?.()}
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.tree}</SectionTitle>
      {@render tree?.()}
    </div>
  </section>

  <Separator />

  <section class="flex flex-col gap-6">
    <SectionTitle as="h2">{copy.dashboard}</SectionTitle>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.metricTiles}</SectionTitle>
      {@render metricTiles?.()}
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.entityGrid}</SectionTitle>
      <EntityGrid>
        {#each entities as entity (entity.title)}
          <EntityCard title={entity.title} subtitle={entity.subtitle} stats={entity.stats} status={entity.status} />
        {/each}
      </EntityGrid>
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.summaryCard}</SectionTitle>
      <SummaryCard title={copy.summaryTitle} items={summaryItems} />
    </div>
  </section>

  <Separator />

  <section class="flex flex-col gap-6">
    <SectionTitle as="h2">{copy.form}</SectionTitle>

    <div class="flex flex-col gap-2 max-w-xs">
      <SectionTitle as="h3">{copy.select}</SectionTitle>
      {@render select?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-xs">
      <SectionTitle as="h3">{copy.combobox}</SectionTitle>
      {@render combobox?.()}
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.checkbox}</SectionTitle>
      {@render checkbox?.()}
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.switchTitle}</SectionTitle>
      {@render switchSnippet?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-xs">
      <SectionTitle as="h3">{copy.datePicker}</SectionTitle>
      {@render datePicker?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-sm">
      <SectionTitle as="h3">{copy.dateRangePicker}</SectionTitle>
      {@render dateRangePicker?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-sm">
      <SectionTitle as="h3">{copy.pinInput}</SectionTitle>
      {@render pinInput?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-sm">
      <SectionTitle as="h3">{copy.tagsInput}</SectionTitle>
      {@render tagsInput?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-xs">
      <SectionTitle as="h3">{copy.calendar}</SectionTitle>
      {@render calendar?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-sm">
      <SectionTitle as="h3">{copy.rangeCalendar}</SectionTitle>
      {@render rangeCalendar?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-sm">
      <SectionTitle as="h3">{copy.slider}</SectionTitle>
      {@render slider?.()}
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.toggleGroup}</SectionTitle>
      {@render toggleGroup?.()}
    </div>
  </section>

  <Separator />

  <section class="flex flex-col gap-3">
    <SectionTitle as="h2">{copy.navigation}</SectionTitle>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.tabs}</SectionTitle>
      {@render tabs?.()}
    </div>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.dropdownMenu}</SectionTitle>
      {@render dropdownMenu?.()}
    </div>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.contextMenu}</SectionTitle>
      {@render contextMenu?.()}
    </div>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.menubar}</SectionTitle>
      {@render menubar?.()}
    </div>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.tableOfContents}</SectionTitle>
      {@render tableOfContents?.()}
    </div>
  </section>

  <Separator />

  <section class="flex flex-col gap-3">
    <SectionTitle as="h2">{copy.chat}</SectionTitle>
    <p class="text-sm text-muted-foreground">{copy.chatNote}</p>
    <div class="relative h-[28rem] w-full overflow-hidden rounded-xl border">
      {@render chat?.()}
    </div>
  </section>

  <Separator />

  <section class="flex flex-col gap-4">
    <SectionTitle as="h2">{copy.overlay}</SectionTitle>
    <div class="flex flex-wrap gap-3">
      {@render overlayTriggers?.()}
    </div>
    <div class="flex flex-col gap-2 max-w-xl">
      <SectionTitle as="h3">{copy.accordion}</SectionTitle>
      {@render accordion?.()}
    </div>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.tooltip}</SectionTitle>
      {@render tooltip?.()}
    </div>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.popover}</SectionTitle>
      {@render popover?.()}
    </div>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.hoverCard}</SectionTitle>
      {@render hoverCard?.()}
    </div>
    <div class="flex flex-col gap-2 max-w-xl">
      <SectionTitle as="h3">{copy.scrollArea}</SectionTitle>
      {@render scrollArea?.()}
    </div>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.drawer}</SectionTitle>
      {@render drawer?.()}
    </div>
  </section>

  <Separator />

  <section class="flex flex-col gap-3">
    <SectionTitle as="h2">{copy.feedback}</SectionTitle>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.progress}</SectionTitle>
      {@render progress?.()}
    </div>
    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.toast}</SectionTitle>
      {@render toast?.()}
    </div>
  </section>

  <Separator />

  <section class="flex flex-col gap-3" aria-label={copy.auth}>
    <!-- AuthPanel owns its Card.Title ("Sesión"); no gallery SectionTitle here. -->
    {@render auth?.()}
  </section>

  <Separator />

  <section class="flex flex-col gap-3">
    <SectionTitle as="h2">{copy.theme}</SectionTitle>
    {@render themeToggle?.()}
  </section>

  <Separator />

  <section class="flex flex-col gap-6">
    <SectionTitle as="h2">{copy.shell}</SectionTitle>
    <p class="text-sm text-muted-foreground">{copy.shellNote}</p>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.shellNavDrawer}</SectionTitle>
      {@render shellNavDrawer?.()}
    </div>

    <div class="flex flex-col gap-2 max-w-xs">
      <SectionTitle as="h3">{copy.shellNavItem}</SectionTitle>
      <ul class="flex flex-col gap-1">
        {@render shellNavItem?.()}
      </ul>
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.shellNavBadge}</SectionTitle>
      {@render shellNavBadge?.()}
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.shellNavbarIcon}</SectionTitle>
      {@render shellNavbarIcon?.()}
    </div>

    <div class="flex flex-col gap-2">
      <SectionTitle as="h3">{copy.shellSurface}</SectionTitle>
      {@render shellSurface?.()}
    </div>
  </section>
</div>
