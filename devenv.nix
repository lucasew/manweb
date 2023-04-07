{ pkgs, ... }:

{
  # https://devenv.sh/basics/
  env.GREET = "devenv";

  # https://devenv.sh/packages/
  packages = [
    pkgs.git
    (pkgs.rust-bin.fromRustupToolchainFile ./rust-toolchain.toml)
    pkgs.wasm-bindgen-cli
    pkgs.wasm-pack
    pkgs.stdenv.cc
  ];

  # https://devenv.sh/scripts/
  scripts.hello.exec = "echo hello from $GREET";
  scripts.teste.exec = "echo eoq";

  enterShell = ''
    hello
    git --version
  '';


  # https://devenv.sh/languages/
  # languages.nix.enable = true;

  # https://devenv.sh/pre-commit-hooks/
  # pre-commit.hooks.shellcheck.enable = true;

  # https://devenv.sh/processes/
  # processes.ping.exec = "ping example.com";

  # See full reference at https://devenv.sh/reference/options/
}
