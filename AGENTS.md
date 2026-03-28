# Project Conventions

## General Guidelines
* **Tooling:** Always use `mise` for tool execution. Ensure tools are pinned to specific versions instead of `latest` or `lts`.
* **Testing:** Pass tests locally before committing, and consider edge cases beyond standard automation.
* **Error Handling:** Centralized error reporting MUST be used for all unexpected errors (`utils_error.py` -> `report_error`). Do not use bare `print` to stderr. No silent failures or ignored exceptions.
* **PR Requirements:** Every PR must include: Assumptions, Alternatives Not Chosen, How To Pivot, and Next Knobs.

## Operational Memory Mappings

* `generate-index` -> Fetches manual metadata via nix-index.
* `fetch.py` -> Downloads and extracts NAR archives, generating a JSON manifest.
* `wasm-client/` -> Rust/WASM frontend codebase for manpage reading.
* `.jules/` -> AI agent journals and execution memory rules.
* `utils_error.py` -> Centralized error reporting utility.
