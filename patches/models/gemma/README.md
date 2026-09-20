# Gemma historical source boundary

The v0.5.19 five-CVM handoff contains no independently replayable Gemma-only
patch bytes that are valid against the maintained v0.5.20 upstream base. Its
profile is preserved only as historical evidence. Shared Qwen/GGUF behavior is
not selected for Gemma by model name. A future Gemma patch must identify an
architecture/load-format guard and a v0.5.20 parent before selection.
