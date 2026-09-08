# Slide foundation styles

This folder is the safe extraction target for global, cross-slide contracts.

- `tokens.css`: design tokens and font import.
- `base.css`: Slidev layout shell and default typography.
- `utilities.css`: intentionally tiny shared helper classes.

Migration rule: page-specific selectors such as `.slidev-layout:has(.cycle-map) ...` should move into the owning Vue component or a named scene stylesheet. The legacy `theme.css` remains imported during the transition so visual behavior does not change unexpectedly.
