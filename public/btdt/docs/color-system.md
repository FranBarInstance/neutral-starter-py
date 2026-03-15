# BTDT Color System & Aesthetic Design Guide

This document defines the professional standards for generating and maintaining color palettes within the Bootstrap Dynamic Themes engine.

---

## 📋 Core Architecture & Rules

### 1. Fundamental principles of color harmony

```
- The colors in a palette should feel like a "family": cohesive, not random.
- Avoid colors that "vibrate" against each other (two saturated complementary colors
  with similar brightness cause visual fatigue).
- Maintain a balance between warm colors (reds, oranges, yellows)
  and cool colors (blues, greens, violets).
- The palette should work on both light and dark backgrounds.
```

---

### 2. Saturation and lightness rules

```
- Not all colors should have the same saturation. Varying intensity
  creates visual hierarchy.
- Functional colors (success, danger, warning, info) can be more
  saturated because they are used sparingly.
- Primary and secondary are seen more frequently: if they are too saturated,
  they tire the eyes.
- 60-30-10 rule:
    · 60% dominant color (light/dark/background)
    · 30% secondary color (secondary/primary)
    · 10% accent color (CTA buttons, badges, alerts)
```

---

### 3. Bootstrap semantic roles (respect conventions)

```
- PRIMARY:    Main brand color. Should be the most recognizable.
              Often blue, but can be any color.
              Must have enough contrast with white for text.

- SECONDARY:  Complementary or analogous to primary.
              More neutral/muted than primary.
              Serves as support, should NOT compete with primary.

- SUCCESS:    Always in the GREEN family.
              Universally associated with "correct/completed/positive."
              Avoid lime green or neon; prefer medium greens.

- DANGER:     Always in the RED family.
              Associated with "error/delete/danger."
              Pure red (#ff0000) is aggressive; soften slightly.

- WARNING:    Always in the YELLOW/ORANGE family.
              Associated with "caution/attention."
              ⚠️ Pure yellow has very little contrast with white.
              Use amber/gold tones and dark text on it.

- INFO:       In the LIGHT BLUE/CYAN family.
              Associated with "information/help/note."
              Must clearly differentiate from primary if primary is blue.

- LIGHT:      Very light gray or off-white.
              Never pure white (#ffffff), better with a subtle tint
              (warm: #f8f5f0, cool: #f0f4f8).

- DARK:       Very dark gray or almost black.
              Never pure black (#000000); use blacks with a tint
              (warm: #2d2a26, cool: #1a1d23).
              Must contrast well with light.
```

---

### 4. Contrast and accessibility (WCAG)

```
- Minimum contrast ratio for text on color:
    · Normal text: 4.5:1 (WCAG AA)
    · Large text (>18px bold): 3:1 (WCAG AA)
    · Ideal: 7:1 (WCAG AAA)

- If the background color is dark → text should be white/light.
- If the background color is light → text should be black/dark.

- WARNING is the most problematic: yellow needs dark text (#000 or #212529),
  never white text.

- Verify that primary and secondary work as button backgrounds
  with readable white text. If not, the color is too light.

- Colors should not convey information BY COLOR ALONE
  (consider icons, text, patterns).
```

---

### 5. Color combination methods

```
MONOCHROMATIC (safest):
  - A single hue, varying saturation and lightness.
  - Primary: medium blue, Secondary: grayish blue.
  - Result: elegant and understated, never fails.

ANALOGOUS (harmonious):
  - Colors adjacent on the color wheel (30-60° apart).
  - E.g., Primary blue + Secondary blue-violet.
  - Creates a sense of cohesion and calm.

COMPLEMENTARY (strong contrast):
  - Opposite colors on the wheel (180°).
  - E.g., Primary blue + orange accents.
  - ⚠️ Use the complementary color sparingly (only accents).

SPLIT-COMPLEMENTARY (balanced):
  - One color + the two adjacent to its complement.
  - E.g., Blue + yellow-orange + red-orange.
  - More versatile and less aggressive than pure complementary.

TRIADIC (vibrant):
  - Three equidistant colors (120° apart).
  - E.g., Blue + red + yellow.
  - ⚠️ Can be chaotic; lower saturation on 2 of the 3.
```

---

### 6. Temperature and color psychology

```
WARM COLORS (energy, action, urgency):
  - Red:      passion, urgency, danger
  - Orange:   creativity, enthusiasm, youth
  - Yellow:   optimism, attention, caution

COOL COLORS (calm, trust, professionalism):
  - Blue:     trust, security, corporate
  - Green:    nature, success, growth
  - Violet:   luxury, creativity, mystery

NEUTRALS (balance, elegance):
  - Gray:     professionalism, neutrality, sobriety
  - Beige:    warmth, naturalness, approachability

TIP: The complete palette should have a coherent "overall temperature."
  - If primary is cool blue → light should be a cool gray (not beige).
  - If primary is warm orange → dark should be a warm gray (not bluish).
```

---

### 7. Common mistakes to avoid

```
❌ Using neon or extremely saturated colors for primary/secondary.
❌ Primary and info being almost the same (both similar blues).
❌ Success and info being almost the same (both blue-greens).
❌ Danger and warning being almost the same (both reddish-oranges).
❌ Using pure black (#000) or pure white (#fff) as dark/light.
❌ "Rainbow" palette where each color seems from a different brand.
❌ Warning with white text (almost always illegible).
❌ Forgetting hover/focus states (the color should allow
   darkening/lightening by 10-15% without breaking).
❌ Colors that only work on screen but not in dark mode.
```

---

### 8. Final validation checklist

```
☐ Does primary stand out as the main color?
☐ Does secondary support without competing with primary?
☐ Are success, danger, warning, and info intuitive without reading the label?
☐ Does each color have enough contrast for text on top?
☐ Does warning work with dark text?
☐ Do light and dark have a tint coherent with the palette's temperature?
☐ Is no pair of colors so similar that they could be confused?
☐ Does the palette look good in light mode AND dark mode?
☐ Do the colors allow for generating lighter/darker variants (tints/shades)?
☐ Could a colorblind user distinguish success from danger? (red/green)
```

---
