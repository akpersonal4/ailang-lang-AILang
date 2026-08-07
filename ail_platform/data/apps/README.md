# Bundled Apps

Copies of the canonical benchmark apps shipped inside the wheel so that
`ail benchmark` and `ail static-analyzer` work after a plain
`pip install ailang-lang` (without a source checkout).

Source of truth: the live apps under `apps/` in the repository. Keep these
copies in sync when the canonical apps change (dice_roller, hangman_game,
inventory_mgmt, kanban, static_analyzer).
