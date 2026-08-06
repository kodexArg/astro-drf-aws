"""LIVE-DOC:START — astro-drf-aws live-doc; see [[adr-19-live-doc-backlinks]]
Governed by: [[adr-14-auth]] · [[adr-07-api-and-backend]]
Docs: [[BACKEND]] · [[AUTH]]
API: [[API]]
LIVE-DOC:END"""

import re

from rest_framework import serializers

from apps.users.models import User

READ_ONLY_FIELDS = ["sub", "email", "given_name", "family_name", "picture", "groups"]

THEME_TOP_LEVEL_KEYS = {"mode", "bgPreset", "sidebarSide", "colors", "radius"}
THEME_COLOR_KEYS = {"canvas", "dots", "surface", "foreground", "primary", "secondary", "accent"}
THEME_MODE_CHOICES = {"light", "dark"}
THEME_BG_PRESET_CHOICES = {"default", "melt"}
THEME_SIDEBAR_SIDE_CHOICES = {"left", "right"}

_COLOR_RE = re.compile(r"^(#[0-9a-fA-F]{3,8}|rgb(a)?\(.*\)|hsl\(.*\)|oklch\(.*\))$")
_COLOR_FORBIDDEN_CHARS = frozenset(";{}<>\"'")
_COLOR_FORBIDDEN_SUBSTRINGS = ("url", "expression")

# Mirrors frontend/src/lib/theme.ts's RADIUS_PATTERN exactly — the server is
# the boundary, not the frontend's re-sanitization ([[GLOSSARY]]: theme_config).
_RADIUS_RE = re.compile(r"^[0-9]*\.?[0-9]+(px|rem|em|%|vh|vw|ch)$")

# Mirrors the frontend shell's NAV_ITEMS hrefs (the closed nav registry,
# [[API]] — POST /api/assistant/ask/), plus the empty default — the server is
# the boundary, not the frontend's own routing ([[adr-25-page-context-assistant]]).
DEFAULT_PAGE_CHOICES = {
    "",
    "/",
    "/chatui/",
    "/showcase/components/",
    "/profile/",
}


def _is_valid_color(value):
    if not isinstance(value, str) or not _COLOR_RE.match(value):
        return False
    if any(char in value for char in _COLOR_FORBIDDEN_CHARS):
        return False
    lowered = value.lower()
    return not any(substring in lowered for substring in _COLOR_FORBIDDEN_SUBSTRINGS)


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)

    class Meta:
        model = User
        fields = READ_ONLY_FIELDS + [
            "nickname",
            "avatar_visible",
            "chat_drawer_enabled",
            "theme_config",
        ]
        read_only_fields = ["sub", "email", "given_name", "family_name", "picture"]

    def validate_theme_config(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("theme_config must be an object.")
        unknown = set(value) - THEME_TOP_LEVEL_KEYS
        if unknown:
            raise serializers.ValidationError(f"Unknown theme_config key(s): {sorted(unknown)}.")
        if "mode" in value and value["mode"] not in THEME_MODE_CHOICES:
            raise serializers.ValidationError("mode must be one of: light, dark.")
        if "bgPreset" in value and value["bgPreset"] not in THEME_BG_PRESET_CHOICES:
            raise serializers.ValidationError("bgPreset must be one of: default, melt.")
        if "sidebarSide" in value and value["sidebarSide"] not in THEME_SIDEBAR_SIDE_CHOICES:
            raise serializers.ValidationError("sidebarSide must be one of: left, right.")
        if "colors" in value:
            colors = value["colors"]
            if not isinstance(colors, dict):
                raise serializers.ValidationError("colors must be an object.")
            unknown_modes = set(colors) - THEME_MODE_CHOICES
            if unknown_modes:
                raise serializers.ValidationError(
                    f"colors must be keyed by mode (light/dark); unknown key(s): {sorted(unknown_modes)}."
                )
            for mode, palette in colors.items():
                if not isinstance(palette, dict):
                    raise serializers.ValidationError(f"colors.{mode} must be an object.")
                unknown_colors = set(palette) - THEME_COLOR_KEYS
                if unknown_colors:
                    raise serializers.ValidationError(
                        f"Unknown colors.{mode} key(s): {sorted(unknown_colors)}."
                    )
                for key, color in palette.items():
                    if not _is_valid_color(color):
                        raise serializers.ValidationError(
                            f"colors.{mode}.{key} is not a valid color value."
                        )
        if "radius" in value:
            radius = value["radius"]
            if not isinstance(radius, str) or not _RADIUS_RE.match(radius):
                raise serializers.ValidationError("radius must be a valid CSS length (px/rem/em/%/vh/vw/ch).")
        return value

    def validate(self, attrs):
        if self.instance is not None:
            for name in ("email", "given_name", "family_name", "picture"):
                if name in self.initial_data and self.initial_data[name] != getattr(self.instance, name):
                    raise serializers.ValidationError({name: "This field is read-only."})
            if "groups" in self.initial_data:
                current = list(self.instance.groups.values_list("name", flat=True))
                if self.initial_data["groups"] != current:
                    raise serializers.ValidationError({"groups": "This field is read-only."})
            if "sub" in self.initial_data and self.initial_data["sub"] != self.instance.sub:
                raise serializers.ValidationError({"sub": "This field is read-only."})
        return attrs
