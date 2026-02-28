# Repository Conventions

## Operational Memory

Where to find things in this repository:

* `README.md` -> Project overview and goals.
* `wasm-client/` -> The Rust/WebAssembly front-end for reading manpages in the browser.
* `fetch.py` -> Python script using `nix-index` to fetch manpage archives from the Nix cache (`cache.nixos.org`), extract them using `xz` and `nix nar cat`, and index them into `man2prog.json`.
* `generate-index` -> Shell script calling `nix-index-database` to generate a list of available manuals to `man.txt`.
* `devenv.nix` / `devenv.yaml` -> Development environment definitions using `devenv.sh` with Nix, including dependencies like Rust, `wasm-bindgen-cli`, and `wasm-pack`.

## Error Handling

* **Centralized Error Reporting:** All code paths that handle unexpected errors MUST funnel through a centralized error-reporting function. Never call `console.error` directly at the call site for unrecoverable errors. Ensure errors are either propagated or logged with sufficient context (message, stack, relevant metadata).
* **No Silent Failures:** Every `catch` block, every `.catch()`, or error callback that is not an expected/recoverable condition MUST report the error. Do not swallow exceptions.
