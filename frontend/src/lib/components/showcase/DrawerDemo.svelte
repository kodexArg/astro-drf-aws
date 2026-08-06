<!-- LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
     Governed by: [[adr-08-frontend-and-design-system]]
     Docs: [[FRONTEND]] · [[DESIGN-SYSTEM]]
     LIVE-DOC:END -->

<!--
  Component-gallery demo of overlay/Drawer — docks to the right viewport
  edge (product rule: left = shell menu / NavDrawer; showcase Drawer is a
  right-side context panel). Default size L (18rem); Collapsed by default;
  same composition-over-a-real-component pattern as the other showcase/*Demo
  wrappers (adr-22, COMPONENTIZATION).
-->
<script lang="ts">
  import { Drawer } from "$lib/components/overlay";
  import { t } from "../../../i18n";
</script>

<p class="text-sm text-muted-foreground">{t("demo_drawer_note")}</p>

<Drawer
  side="right"
  size="L"
  title={t("demo_drawer_right_title")}
  openLabel={t("drawer_open")}
  closeLabel={t("drawer_close")}
>
  <p>{t("demo_drawer_right_body")}</p>
</Drawer>
