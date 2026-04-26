---
sidebar_position: 6
title: "Morph (MorphLLM) as primary provider"
description: "Use Morph’s OpenAI-compatible API for main chat, auxiliary tasks, and MCP tools while keeping Honcho as the memory backend"
---

# Morph (MorphLLM) as primary provider

Hermes does **not** need a dedicated “Morph” provider in code. Morph exposes an **OpenAI-compatible** HTTP API, so you configure the main model as `provider: custom` with `base_url: https://api.morphllm.com/v1` and route auxiliary side-tasks to the **same** credentials using `provider: main` (or explicit `base_url` / `api_key` per task).

**Honcho** stays on the memory path: set `memory.provider: honcho` and keep your existing Honcho / `~/.honcho` setup. Do not point memory embeddings at Morph unless you intentionally replace Honcho’s retrieval stack.

## Where Hermes resolves providers (for debugging)

| Concern | Primary files |
|--------|----------------|
| Main model / runtime | `hermes_cli/runtime_provider.py` (`resolve_runtime_provider`), `run_agent.py` (agent client) |
| Config load + `${VAR}` expansion | `hermes_cli/config.py` (`load_config`, `_expand_env_vars`) |
| Auxiliary + compression + MCP sampling LLM | `agent/auxiliary_client.py` (`call_llm`, `_resolve_task_provider_model`, `resolve_provider_client`) |
| Context compaction summaries | `agent/context_compressor.py` (calls `call_llm(task="compression", ...)`) |
| MCP servers + sampling | `tools/mcp_tool.py` (`_load_mcp_config`, sampling uses `task="mcp"`) |
| External memory provider | `memory.provider` in config; Honcho plugin (`plugins/memory/honcho/`) |

## Recommended layout

1. **Main brain**: `model.provider: custom`, Morph `base_url`, model id in `default`, API key via `api_key: "${MORPH_API_KEY}"` (or `OPENAI_API_KEY` set to the same value).
2. **Auxiliary tasks** (compression, session search, vision, web extract, approval, MCP sampling, flush memories): set `provider: main` so they follow the main Morph endpoint — **or** set each task’s `base_url` / `api_key` explicitly to Morph (redundant but very explicit).
3. **Compression**: Either rely on `auxiliary.compression.provider: main`, or set `compression.summary_provider: main` (both converge on the same auxiliary router; see [Context compression](/docs/developer-guide/context-compression-and-caching)).
4. **MCP**: Register `@morphllm/morphmcp` under `mcp_servers` with `MORPH_API_KEY` and `ENABLED_TOOLS` in `env`.
5. **Memory**: Leave `memory.provider: honcho` unchanged.

Avoid leaving auxiliary providers on `auto` if you want **zero** silent fallback to OpenRouter when Morph is misconfigured — `auto` can still pick other backends. Using `main` or explicit `base_url` for Morph is the explicit pattern.

## Default profile (`~/.hermes/config.yaml`)

Replace `<MORPH_MODEL_ID>` with the model id Morph documents for chat (from the Morph dashboard or API).

```yaml
# --- Main inference (Morph, OpenAI-compatible) ---
model:
  provider: custom
  base_url: "https://api.morphllm.com/v1"
  default: "<MORPH_MODEL_ID>"
  api_key: "${MORPH_API_KEY}"

# --- Context compression: use same provider as main ---
compression:
  enabled: true
  summary_provider: main
  # summary_model: optional override; omit to use auxiliary resolution + main model defaults

# --- Auxiliary tasks: all follow main (Morph) ---
auxiliary:
  vision:
    provider: main
  web_extract:
    provider: main
  compression:
    provider: main
    timeout: 120
  session_search:
    provider: main
  skills_hub:
    provider: main
  approval:
    provider: main
  mcp:
    provider: main
  flush_memories:
    provider: main

# --- Honcho memory (unchanged) ---
memory:
  provider: honcho

# --- Morph MCP: fast edit + WarpGrep-style search ---
mcp_servers:
  morph:
    command: "npx"
    args: ["-y", "@morphllm/morphmcp"]
    env:
      MORPH_API_KEY: "${MORPH_API_KEY}"
      ENABLED_TOOLS: "edit_file,warpgrep_codebase_search"
    timeout: 120
    connect_timeout: 60
    # Optional: restrict which MCP tools Hermes exposes
    # tools:
    #   include: ["edit_file", "warpgrep_codebase_search"]
```

### Environment (`~/.hermes/.env`)

```bash
MORPH_API_KEY=sk-...
```

If you prefer not to use `${MORPH_API_KEY}` in YAML, you can set `OPENAI_API_KEY` to the same key; Hermes uses that for custom endpoints when `api_key` is omitted.

## Named profile (e.g. `sec` or `web3`)

Profiles use a separate config file: `~/.hermes/profiles/<name>/config.yaml`. Copy the same blocks as above into that file. Each profile can use a different `model.default` or the same Morph key.

Launch with:

```bash
hermes -p sec chat
```

Honcho peer / workspace settings remain in Honcho’s own config; `hermes honcho` commands still apply per profile when documented.

## Verify Morph is used

1. **Config dump**

   ```bash
   hermes config
   ```

   Confirm `model.base_url` is `https://api.morphllm.com/v1` and auxiliary providers show `main` (or your explicit Morph `base_url`).

2. **Logs on auxiliary calls** — Hermes logs lines like `Auxiliary compression: using main (...)` with a base URL. Enable debug logging if your install supports it (e.g. `HERMES_LOG_LEVEL=DEBUG` or project-specific log env — check your `hermes` version).

3. **Sanity API call** (optional)

   ```bash
   curl -sS https://api.morphllm.com/v1/models \
     -H "Authorization: Bearer $MORPH_API_KEY" | head
   ```

## Verify Honcho memory still works

```bash
hermes honcho status
hermes memory status   # if available in your build
```

Start a short chat, add a memory-dependent action your setup uses, and confirm Honcho still records sessions (same as before). Nothing in the Morph model block replaces Honcho unless you change `memory.provider`.

## MCP sampling

If an MCP server requests LLM sampling, Hermes routes the completion through `auxiliary.mcp` (`call_llm(task="mcp", ...)`). With `auxiliary.mcp.provider: main`, sampling uses Morph like the rest.

## Risks and fallbacks

| Risk | Mitigation |
|------|------------|
| Wrong or missing `MORPH_API_KEY` | Main chat fails fast; fix `.env` or `model.api_key` |
| Auxiliary `auto` silently using OpenRouter | Set `provider: main` or explicit Morph `base_url` for each task |
| Vision / multimodal on a text-only Morph model | Vision calls may error; use a vision-capable model on `auxiliary.vision` or keep `auto` for vision only |
| MCP `npx` missing | Install Node.js; or run the Morph MCP server via another supported command |

## Related docs

- [Configuration](/docs/user-guide/configuration)
- [Fallback providers](/docs/user-guide/features/fallback-providers)
- [Use MCP with Hermes](/docs/guides/use-mcp-with-hermes)
- [Honcho](/docs/user-guide/features/honcho)
- [MCP config reference](/docs/reference/mcp-config-reference)
