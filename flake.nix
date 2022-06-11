{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        lib = nixpkgs.lib;
        pkgs = import nixpkgs { inherit system; };

        pythontex = with pkgs; stdenv.mkDerivation {
          name = "pythontex";

          src = fetchFromGitHub {
            owner = "gpoore";
            repo = "pythontex";
            rev = "v0.18";
            sha256 = "sha256-3UGfECuHLtmfd6Zwc35VMsy6MZp1rOWRivg1PyxPlcA=";
          };

          dontPatchShebangs = true;

          installPhase = ''
            install -Dt $out/bin ./pythontex/*
            mv $out/bin/pythontex3.py $out/bin/pythontex
          '';
        };
      in
      {
        devShell = with pkgs; (buildFHSUserEnv {
          name = "the-bootstrap-approach";
          targetPkgs = _: [
            stdenv.cc.cc.lib
            (python3.withPackages (ps: with ps; [ pip ]))
            # Numpy dependencies
            zlib
            # For aircraft checklist examples
            pythontex
            texlive.combined.scheme-full
          ];
        }).env;
      }
    );
}
