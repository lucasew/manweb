# Project Conventions

## General Directives

*   **Error Handling Convention:** All unexpected errors must be routed through a centralized error-reporting function. Silent failures or direct `console.error` (or `print(..., file=sys.stderr)` in Python) calls are forbidden. In `fetch.py`, use the `report_error` utility function to log issues contextually rather than swallowing them or using bare prints.
*   **Tooling:** Use `mise` for all task executions and always pin `mise` tools to specific versions (avoiding `latest` or `lts`).
*   **PR Requirements:** Every PR must include specific sections: `Assumptions`, `Alternatives Not Chosen`, `How To Pivot`, and `Next Knobs`.
*   **Git Requirements:** Never commit tooling, bootstrap, or download artifacts such as `install-mise.sh` or temporary installers. Use explicit `git add <path>` and NEVER `git add .` or `git add -A`.

## Operational Memory

*   `generate-index` -> queries `nix-index` for manuals.
*   `fetch.py` -> downloads and extracts nar archives to generate a JSON manifest.
*   `wasm-client` -> Rust/WASM frontend for reading the manpages.
