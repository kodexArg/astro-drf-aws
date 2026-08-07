import { describe, expect, test } from "bun:test";
import { Glob } from "bun";
import path from "node:path";

// adr-08 rule 9's SSOT backend: only PUBLIC_* env reaches the client bundle
// ([[adr-08-frontend-and-design-system]] rule 7).

const SRC = path.join(import.meta.dir, "..", "src");

/** Server-only modules that legitimately read a non-PUBLIC server var — never
 * bundled to the browser. Exact paths only, never a directory wildcard. */
const SERVER_ONLY_ALLOWLIST = new Set([
  "lib/authGate.ts", // Astro middleware helper: reads BACKEND_API_URL server-side
  "middleware.ts",
]);

const SECRET_STEMS = ["COGNITO_", "MSGRAPH_", "DJANGO_", "SECRET_", "AWS_", "DB_"];

const ENV_REF = /\bimport\.meta\.env\.([A-Z0-9_]+)|\bprocess\.env\.([A-Z0-9_]+)/g;

function clientFiles(): string[] {
  const glob = new Glob("**/*.{svelte,ts}");
  return [...glob.scanSync(SRC)]
    .map((p) => p.replaceAll(path.sep, "/"))
    .filter((p) => !SERVER_ONLY_ALLOWLIST.has(p))
    .sort();
}

function astroTemplates(): string[] {
  const glob = new Glob("**/*.astro");
  return [...glob.scanSync(SRC)].map((p) => p.replaceAll(path.sep, "/")).sort();
}

/** `.astro` frontmatter (between the `---` fences) is server-only and out of
 * scope; only what follows can ship to the client (inline `<script>`s). */
function clientPortion(source: string): string {
  const first = source.indexOf("---");
  if (first === -1) return source;
  const second = source.indexOf("---", first + 3);
  if (second === -1) return source;
  return source.slice(second + 3);
}

function envRefs(source: string): string[] {
  return [...source.matchAll(ENV_REF)].map((m) => m[1] ?? m[2]);
}

function namesSecretStem(name: string): boolean {
  return SECRET_STEMS.some((stem) => name.startsWith(stem));
}

const files = clientFiles();
const astroFiles = astroTemplates();

describe("adr-08 rule 7 — client bundle sees PUBLIC_* only", () => {
  test("the suite discovers real subjects", () => {
    expect(files.length).toBeGreaterThan(50);
    expect(astroFiles.length).toBeGreaterThan(0);
  });

  test("the detector actually catches a secret-bearing reference", () => {
    expect(envRefs('import.meta.env.COGNITO_CLIENT_SECRET')).toEqual([
      "COGNITO_CLIENT_SECRET",
    ]);
    expect(namesSecretStem("COGNITO_CLIENT_SECRET")).toBe(true);
    expect(namesSecretStem("PUBLIC_BACKEND_URL")).toBe(false);
  });

  for (const rel of files) {
    test(`${rel} reads no env var outside PUBLIC_*`, async () => {
      const source = await Bun.file(path.join(SRC, rel)).text();
      const offenders = envRefs(source).filter((name) => !name.startsWith("PUBLIC_"));
      expect(`${rel}: ${offenders.join(", ")}`).toBe(`${rel}: `);
    });

    test(`${rel} names no secret-bearing env stem`, async () => {
      const source = await Bun.file(path.join(SRC, rel)).text();
      const offenders = SECRET_STEMS.filter((stem) => source.includes(stem));
      expect(`${rel}: ${offenders.join(", ")}`).toBe(`${rel}: `);
    });
  }

  for (const rel of astroFiles) {
    test(`${rel} client-shipped portion reads no env var outside PUBLIC_*`, async () => {
      const source = await Bun.file(path.join(SRC, rel)).text();
      const offenders = envRefs(clientPortion(source)).filter(
        (name) => !name.startsWith("PUBLIC_"),
      );
      expect(`${rel}: ${offenders.join(", ")}`).toBe(`${rel}: `);
    });
  }

  test("every SERVER_ONLY_ALLOWLIST entry names a file that actually exists", async () => {
    const glob = new Glob("**/*.ts");
    const all = new Set([...glob.scanSync(SRC)].map((p) => p.replaceAll(path.sep, "/")));
    for (const rel of SERVER_ONLY_ALLOWLIST) {
      expect(all.has(rel)).toBe(true);
    }
  });
});
