# AILang AI Model Guide

How different AI coding tools consume and utilize AILang documentation.

---

## Claude Code

**Behavior:** Auto-reads `AGENTS.md` from repo root on each session start.

**Recommended setup:**
- Ensure `AGENTS.md` is up to date at repo root (already done)
- Claude Code will automatically follow §2 Mandatory Reading Order (reads PROJECT_MEMORY.md → Playbook → Master Prompt → specs in order)
- The Validation Checklist (§6) will be applied by default

**No manual action needed.**

---

## Cursor

**Behavior:** Does NOT auto-read `AGENTS.md`. Uses indexed project docs.

**Recommended setup:**
1. Open Cursor → Settings → Rules
2. Set **User Rules** to: `You MUST read AGENTS.md from the repo root before writing any AILang code.`
3. Optionally, add `AGENTS.md` content under **Project Rules** (`.cursorrules`)

**Alternative:** Create a `.cursorrules` file at repo root:
```
You MUST read AGENTS.md from the repo root before writing any AILang code.
You MUST follow the Validation Checklist in AGENTS.md §5.
You MUST check examples/patterns/ for pre-written recipes before writing filter/map/reduce/split/find.
```

---

## Windsurf

**Behavior:** Reads `AGENTS.md` from repo root (same as Claude Code).

**Recommended setup:**
- Ensure `AGENTS.md` is up to date (already done)
- No manual action needed

---

## GitHub Copilot Chat

**Behavior:** Does NOT auto-read `AGENTS.md`. No persistent project context.

**Recommended setup:**
- For each session, paste `AGENTS.md` into the chat context
- Or reference: `Read AGENTS.md from the repo root — it contains the mandatory pre-read checklist, validation gates, and encoding constraints`

---

## Cline / Claude Dev (VS Code Extension)

**Behavior:** Can auto-read `AGENTS.md` and `CLINE.md` if configured.

**Recommended setup:**
1. Install Cline extension
2. Ensure `AGENTS.md` is at repo root (already done)
3. In Cline settings, add a custom instruction: `Always read AGENTS.md from the repo root before writing any AILang code.`

---

## ChatGPT / Generic LLM Chat

**Behavior:** No project awareness, no file system access.

**Recommended setup:**
- Paste the contents of `AGENTS.md` and `docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md` into the chat
- This covers all mandatory rules and engineering workflow

---

## Summary Table

| Tool | Auto-reads AGENTS.md | Setup Required |
|------|:--------------------:|:--------------:|
| Claude Code | ✅ | None |
| Cursor | ❌ | .cursorrules or User Rules |
| Windsurf | ✅ | None |
| Copilot Chat | ❌ | Manual paste per session |
| Cline | ✅ (if configured) | Add custom instruction |
| ChatGPT | ❌ | Paste AGENTS.md + AILANG_DEVELOPMENT_PLAYBOOK.md |

---

## Benchmark Models & Providers

AILang's Engineering Benchmark framework (`benchmarks/providers/`) supports 4 AI providers. The benchmark protocol (`docs/benchmarks/INVENTORY_BENCHMARK_HARNESS.md`) requires a minimum of 3 models, one per tier:

| Tier | Provider | Model |
|:----:|----------|-------|
| 1 | Anthropic | `claude-sonnet-4-20250514` |
| 2 | OpenAI | `gpt-4o-2025-05-13` |
| 3 | Open-weight | `deepseek-coder-v2` or `llama-4-70b` |

**Provider abstraction:** `benchmarks/providers/base.py` defines the `AIProvider` interface. Concrete implementations: `openai_provider.py`, `anthropic_provider.py`, `google_provider.py`, `local_provider.py`.

**Configuration:** API keys via environment variables:
```
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY=...
GOOGLE_API_KEY=...
```

**Calibration:** `python -m benchmarks calibrate` validates measurement consistency across providers before a benchmark run.

**Temperature:** All benchmark runs use temperature `0.0` for deterministic output.

---

## CI Pipeline

A GitHub Actions workflow (`.github/workflows/ci.yml`) validates every PR against:

1. **pytest** — 522 test suite
2. **black** — Python formatting
3. **ruff** — Python linting
4. **mypy** — Python type checking
5. **ail build** — all `.ail` files in `apps/`, `ai_benchmarks/`, `examples/patterns/`
6. **ail run** — all compiled apps
7. **Documentation links** — verify all `[text](path)` references resolve
8. **Benchmark summary** — auto-generated build/run rate table
