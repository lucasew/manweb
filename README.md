# manweb

Read manpages on the browser.

Powered by Nix, or at least the consequences of the ecosystem.

It's very experimental and still doesn't work so far.

## Architecture & Flow

This project reads system manuals extracted from Nix archives and displays them on a WebAssembly frontend. The pipeline consists of the following tools:

1. **Index Generation (`generate-index`)**: Generates a raw text file (`man.txt`) detailing the manuals available from the `nix-index-database` by searching for `/man/man[0-9]/.*.gz`.
2. **Fetching & Extracting (`fetch.py`)**: Consumes the raw text index (`man.txt`), downloads the relevant nar archives from `cache.nixos.org`, extracts the manual files locally using `xz` and `nix nar cat`, and generates a JSON manifest (`man2prog.json`) containing metadata for the manuals.
3. **Frontend Presentation (`wasm-client`)**: A Rust-based WebAssembly application that is meant to serve as the user interface for parsing and reading the extracted manpages inside the browser.
