import { describe, expect, test } from "bun:test";
import {
  encodeNavLockCookie,
  parseNavLockCookie,
  resolveNavFsm,
  resolvePresentation,
  resolveViewport,
} from "../src/lib/components/shell/nav-fsm";

describe("parseNavLockCookie", () => {
  test("treats 1/locked/true as locked", () => {
    expect(parseNavLockCookie("1")).toBe("locked");
    expect(parseNavLockCookie("locked")).toBe("locked");
    expect(parseNavLockCookie("TRUE")).toBe("locked");
  });

  test("everything else is unlocked", () => {
    expect(parseNavLockCookie(undefined)).toBe("unlocked");
    expect(parseNavLockCookie(null)).toBe("unlocked");
    expect(parseNavLockCookie("0")).toBe("unlocked");
    expect(parseNavLockCookie("unlocked")).toBe("unlocked");
    expect(parseNavLockCookie("")).toBe("unlocked");
  });
});

describe("encodeNavLockCookie", () => {
  test("round-trips through parse", () => {
    expect(parseNavLockCookie(encodeNavLockCookie("locked"))).toBe("locked");
    expect(parseNavLockCookie(encodeNavLockCookie("unlocked"))).toBe("unlocked");
  });
});

describe("resolveViewport", () => {
  test("mobile below rail floor", () => {
    expect(resolveViewport(false, false)).toBe("mobile");
    expect(resolveViewport(false, true)).toBe("mobile");
  });

  test("tablet at or above rail and below desk", () => {
    expect(resolveViewport(true, false)).toBe("tablet");
  });

  test("desk at or above desk floor", () => {
    expect(resolveViewport(true, true)).toBe("desk");
  });
});

describe("resolvePresentation", () => {
  test("unlocked always drawer", () => {
    expect(resolvePresentation("unlocked", "mobile")).toBe("drawer");
    expect(resolvePresentation("unlocked", "tablet")).toBe("drawer");
    expect(resolvePresentation("unlocked", "desk")).toBe("drawer");
  });

  test("locked forces drawer on mobile only", () => {
    expect(resolvePresentation("locked", "mobile")).toBe("drawer");
    expect(resolvePresentation("locked", "tablet")).toBe("rail");
    expect(resolvePresentation("locked", "desk")).toBe("rail");
  });
});

describe("resolveNavFsm", () => {
  test("packages preference, viewport, presentation, and active", () => {
    expect(
      resolveNavFsm({ preference: "locked", viewport: "tablet", active: "/chatui/" }),
    ).toEqual({
      preference: "locked",
      viewport: "tablet",
      presentation: "rail",
      active: "/chatui/",
    });
  });

  test("presentation is never stored — every combination is derived on demand", () => {
    for (const preference of ["locked", "unlocked"] as const) {
      for (const viewport of ["mobile", "tablet", "desk"] as const) {
        const state = resolveNavFsm({ preference, viewport, active: "/profile/" });
        expect(state.presentation).toBe(resolvePresentation(preference, viewport));
      }
    }
  });
});
