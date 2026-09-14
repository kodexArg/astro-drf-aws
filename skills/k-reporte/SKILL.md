---
name: k-reporte
description: SOLO ESPAÑOL. Construye UN reporte HTML oscuro, mobile-first y autocontenido (Presentation Orange) a partir del cierre de un trabajo, del último mensaje del asistente, o de instrucciones explícitas del usuario — valida mermaid y guarda en ~/Documents/k-reporte/. Primero enruta la intención (resumen de job · brief del último mensaje · brief explícito). Traduce TODO el input al español y escribe el reporte + la respuesta de chat en español. Usar cuando kodex corre /k-reporte o pide un reporte HTML en español / para el celular / WhatsApp en español. El gemelo en inglés es /k-report. Estética fija: near-black cálido, naranja racionado, Nunito + DM Mono, Lucide, mermaid temático. Nunca improvisar diseño.
version: v0.1.0
---

> [!info] In force on this repo (Team Party map)
> Remap mold citations: constitution [[adr-24-constitution]], layout [[adr-25-harness-layout]],
> agent contract [[adr-26-agent-contract]], guardians [[adr-27-guardians-and-delivery]].
> Product SSOT: `docs/constitution/PRD.md`. Do not invent station/product law.


# k-reporte (Español)

**SSOT path:** `skills/k-reporte/`  
**Assets compartidos:** `references/` y `scripts/` → softlinks in-tree a `../k-report/` (una sola copia de tokens, templates, validador).  
**Gemelo en inglés:** `/k-report` → `skills/k-report/`.

Construir **un** archivo HTML oscuro autocontenido — mobile-first, legible en desktop — del sistema **Presentation Orange**. Se rellenan templates fijos; no se inventa una estética nueva.

---

## Ley de idioma (no negociable)

Esta skill es **100% español**.

1. **Respuesta de chat** a kodex después de correr la skill: solo español.
2. **Todo el copy del reporte** (títulos, kickers, cuerpo, chips, takeaway, figcaptions): solo español.
3. **Traducir el input al español** antes de escribir el reporte — último mensaje, markdown adjunto, contenido de paths, notas del usuario, etiquetas de diagramas visibles. Conservar identificadores de código, paths, nombres de paquetes y APIs tal cual; traducir la prosa alrededor.
4. Si el usuario mezcló inglés + español, **normalizar a español** en el artefacto.
5. No derivar a `/k-report` salvo que el usuario invoque explícitamente el inglés (`/k-report` o “in English”). Esta skill queda en español de punta a punta.

Voz: tersa, headings en minúscula, middot `·` para beats, flecha `→` para transformación. Preferir español rioplatense natural (vos / “pedímelo”) cuando el tono lo pida; sin relleno tutorial.

---

## Router de intención (correr primero — cada invocación)

Antes del HTML, clasificar el pedido en **exactamente una** ruta. Priorizar señales del **mismo turno**. Si dos rutas encajan:

**C (explícito) > A (resumen de job) > B (brief del último mensaje)**

### Ruta A — Resumen al cerrar un job (muy frecuente)

El usuario (o el asistente) acaba de terminar un trabajo y quiere un **cierre compartible**: qué se hizo, qué queda, paths/comandos clave, estado.

| Señal (ejemplos) | → Ruta A |
|---|---|
| `/k-reporte` justo después de un fix multi-paso sin prosa extra | A |
| “reportá esto”, “cerrá con un reporte”, “status report”, “resumen del job” | A |
| “qué hicimos”, “ship summary”, “listo — reportalo” | A |
| `/k-reporte` pelado cuando el tramo previo fue ejecución/verificación, no una explicación conceptual larga | A |

**Qué producir:** un reporte **status / decision** apretado. **Se puede resumir** el trabajo completado a partir de la conversación — comprimir, estructurar, tirar ruido. Templates preferidos: `status-report.html` o `decision-summary.html`. 0–2 mermaid solo si clarifican flujo (pipeline, before→after). **No inventar** hechos que no aparecieron en la sesión.

### Ruta B — Brief del último mensaje (re-explicar / compartir)

El usuario quiere un **reporte standalone del último mensaje** — prosa más rica, más charts, estructura más clara — porque no lo terminó de entender, o quiere reenviarlo.

| Señal (ejemplos) | → Ruta B |
|---|---|
| “brief del último mensaje”, “reportá la última respuesta”, “hacé un reporte de eso” | B |
| “no lo entendí”, “explicámelo de nuevo como reporte”, “para compartir” | B |
| `/k-reporte` pelado cuando el último turno del asistente fue una explicación conceptual larga | B |
| “más diagramas”, “más claro”, “versión para el celu de eso” | B |

**Qué producir:** tomar el **último mensaje sustantivo del asistente** como fuente de verdad y **reescribirlo** en prosa de reporte en español clara (revisión, no paste frío). **Se puede**:

- reestructurar headings y kickers
- agregar mermaid que vuelva visuales las mismas ideas
- expandir bullets densos a párrafos cortos legibles
- sumar chips / un takeaway

**No se puede** inventar claims técnicos, números o decisiones ausentes de esa fuente (ni de correcciones explícitas del usuario en el mismo turno). Preferir: `concept-explainer.html`, `comparison.html` / `comparison-interactive.html`, o `stat-highlight.html` si dominan números.

### Ruta C — Brief explícito (manda la instrucción del usuario)

El usuario nombra forma, audiencia, secciones o constraints.

| Señal (ejemplos) | → Ruta C |
|---|---|
| “comparación interactiva de X vs Y” | C |
| “reporte de stats solo con estas tres métricas…” | C |
| “decision summary para el equipo: elegimos Postgres” | C |
| Markdown/archivo adjunto + “usá esto como cuerpo del reporte” | C |
| Cualquier nombre de template o outline de secciones | C |

**Qué producir:** seguir la instrucción del usuario **por encima** de los defaults A/B. Fuente = contenido adjunto si hay, si no último mensaje + sus constraints. Sigue siendo solo español. Estética fija. Un solo template (intención dominante).

### Self-check del router (una línea, privado, después actuar)

Decir en silencio: `route=A|B|C · source=… · template=… · lang=es` y ejecutar. No preguntar la ruta salvo que no haya fuente (primer turno sin respuesta previa ni adjunto).

> [!important] Fuente por defecto
> Sin markdown/path en el turno → la **última respuesta sustantiva del asistente** es la fuente (A o B definen cuánto se reescribe). Adjunto/path en el mismo turno gana. Preguntar solo si no hay nada que reportar.

### Qué significa ahora “no soy un summarizer”

| Absoluto viejo | Ahora |
|---|---|
| Nunca resumir / nunca escribir | **Depende de la ruta.** A: resumir el job. B: revisar/enriquecer el último mensaje. C: obedecer el brief. |
| Nunca inventar | Sigue absoluto: **sin hechos nuevos**, sin research, sin improvisar diseño. |

---

## La única regla de diseño

La estética vive bajo `references/` (softlink al paquete inglés). Pipeline: ruta → fuente (→ español) → template → relleno → validar → guardar → reportar path. Sin colores, fonts, radii, frameworks ni layouts nuevos.

## Pipeline

1. **Rutear** (A / B / C) con las tablas de arriba.
2. **Idioma:** normalizar toda la prosa fuente a **español**.
3. **Contrato de diseño (una vez):** `references/design-tokens.css` se embebe verbatim. `references/EXTRACTED-DESIGN-SYSTEM.md` solo para juicios — no re-fetchear URLs.
4. **Fuente:** adjunto/path > último mensaje del asistente > (solo si vacío) preguntar y parar.
5. **Elegir un template** de `references/templates/` (mapeo abajo).
6. **Rellenar** en español:
   - `# / ##` → `<h1>/<h2>` (minúscula; el CSS las mantiene).
   - eyebrow tipo `03 · QUÉ ES` → `<p class="kicker">`.
   - párrafos → `<p>`; `**bold**` → `<strong>`. **Racionar `<strong>`** — como mucho la frase de carga por pasaje.
   - fence ```lang → `<pre><code>`; diff `+`/`-` → `<pre class="diff">` con `<span class="add">` / `<span class="del">`.
   - ```mermaid → `<div class="diagram"><pre class="mermaid">…</pre></div>` con `%%{init}%%` que incluya `themeVariables.fontSize:'15px'`, kit classDef (`references/mermaid-guide.md`), **loader RULE 3 verbatim** (`MERMAID_FS`, nunca `MIN_H`). **REGLA DURA: nunca emitir `{{ }}` ni placeholders `{ }` sueltos dentro de mermaid**. Etiquetas literales en español minúscula. State diagrams: forma `s1 : etiqueta` (sin espacios/llaves en ids). Estilo con `class id hero|step|cool|ok|bad`.
   - UNA conclusión → `<div class="takeaway">`. Como máximo una.
   - tags → `<span class="chip ok|work|stop">` dentro de `<div class="chips">` si hay varios.
   - hook del hero = **una** línea tensa.
   - iconos → Lucide SVG inline (`references/icons.md`); un acento por sección; `.icon-lg` naranja en hero.
   - **imágenes** solo si el caller pasa una → `.figure` (ver Imágenes).
7. **Emitir UN archivo.** CSS inline; Google Fonts + mermaid CDN. Compare interactivo: un IIFE vanilla (`references/interactive-compare.md`). Sin React/npm.
8. **Gate de validación** (obligatorio) — abajo.
9. **Guardar (obligatorio):** `mkdir -p ~/Documents/k-reporte` y escribir  
   `~/Documents/k-reporte/<slug>-YYYYMMDD.html`. Si el usuario nombró otra carpeta, copiar **también** ahí; el archivo de archivo siempre queda. Reportar path(s) absolutos.
10. **Cierre en el path (sin canal de envío):** el archivo guardado **es** la
    entrega. Reportar en el chat el path absoluto y el `<h1>` + una línea en
    español, y terminar ahí. Este harness **no** trae paso de envío: sin
    Telegram, sin bot token, sin push saliente. Si el caller lo quiere en otro
    lado, nombra la carpeta (el paso 9 escribe la copia extra) o lo mueve.

## Gate de validación (obligatorio)

```bash
python3 skills/k-reporte/scripts/validate_mermaid.py <artifact.html>
```

(Equivale a `skills/k-report/scripts/…` — mismo script vía softlink.)

- Exit `0` → guardar y reportar el path.
- Exit `1` → arreglar mermaid (casi siempre llaves o ids de state), re-correr hasta `0`.
- **Nunca entregar un artefacto que falle el gate.**

Tier 1 (stdlib) siempre. Tier 2: `bunx @mermaid-js/mermaid-cli` con `PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium` y `--no-sandbox`; degrada a WARN si falta. `--selftest` para fixtures.

## Imágenes (solo si el caller adjunta una)

Nunca inventar imágenes. Path o paste (guardar el paste a un path primero).

1. Copiar a `<report-dir>/assets/<name>`; original intacto.
2. Ref relativa:  
   `<figure class="figure figure--veil"><img src="./assets/<name>" alt="…"><figcaption>… · uso local</figcaption></figure>`  
   Slot vacío: `.image-slot`.
3. **ADVERTIR siempre:** *"La imagen es de **uso local** — se ve al abrir el .html en esta máquina (con su carpeta `assets/`), pero NO viaja si mandás solo el .html por WhatsApp. Para un archivo realmente portable, pedímelo incrustado (base64)."*  
   Base64 solo si piden explícitamente un archivo portable único.

## Mapeo de templates

| Contenido / lean de la ruta | Template |
|---|---|
| status / progreso + código + flujo (A canónico) | `status-report.html` |
| concepto en pasos, denso en diagramas (B canónico) | `concept-explainer.html` |
| dos opciones lado a lado | `comparison.html` (naranja = A, teal = B) |
| lo mismo + tabs | `comparison-interactive.html` + `interactive-compare.md` |
| pocas métricas que importan | `stat-highlight.html` |
| decisión + racional / cierre | `decision-summary.html` |

Un template dominante; el resto como secciones. No coser dos esqueletos.

## Hard constraints (nunca violar)

- **Mobile-first, no mobile-only:** viewport meta; base ~480px; enhance a `≥768px` / `≥1024px` (~660 / ~880px).
- **Dark:** near-black cálido, tipo cream, **un** `.po-glow` naranja off-center. ~un acento naranja por sección.
- **Type:** Nunito 400/500/800 + DM Mono vía Google Fonts. Headings minúscula; mayúscula solo en kickers.
- **Surface:** pocas formas, corners cuadrados (pills solo en chips), hairlines 1.5px, sin drop shadows (solo el halo). Left rule > card. Motion detrás de `prefers-reduced-motion: no-preference`.
- **Mermaid primero en la página:** loader RULE 3 verbatim; `fontSize:'15px'`; tipografía del diagrama = body; grab-to-pan; sin fondo blanco en el svg.
- **Templates** ya embeben `design-tokens.css` — no editar CSS a mano dentro del template; editar `references/design-tokens.css` (en el paquete inglés) y re-inline a los seis templates.
- **Autocontenido:** un solo `.html`.

## Referencias

Viven en el softlink `skills/k-reporte/references/` → `skills/k-report/references/`:

- `design-tokens.css`, `mermaid-guide.md`, `icons.md`, `templates/` (6), `interactive-compare.md`, `EXTRACTED-DESIGN-SYSTEM.md`
- `scripts/validate_mermaid.py`

**Relacionadas**

| Skill | Path | Rol |
|---|---|---|
| `k-report` | `skills/k-report/` | gemelo inglés (mismo pipeline, ley EN) |
| `kdx-design-system` | máquina-global (fuera del harness) | HTML libre; reportes fijos siguen acá |

Repo de diseño (si existe): `~/Dev/design.kodexarg.com` — sincronizar `references/` del paquete inglés si cambian tokens.

## Self-check antes de entregar

- [ ] Ruta A/B/C elegida con la prioridad correcta
- [ ] Todo el reporte + chat en **español**; input traducido
- [ ] Un archivo; legible en phone + desktop
- [ ] Naranja racionado; un glow; headings minúscula; kickers mayúscula
- [ ] Mermaid: init temático + loader `MERMAID_FS`; gate exit 0
- [ ] Guardado en `~/Documents/k-reporte/`
- [ ] Path absoluto reportado en el chat (sin canal de envío)
- [ ] Sin hechos nuevos; sin improvisar diseño
