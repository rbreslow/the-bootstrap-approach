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
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            stdenv.cc.cc.lib
            (python3.withPackages (ps: with ps; [ pip ]))
            # Numpy dependencies
            zlib
            # For aircraft checklist examples
            texlive.combined.scheme-full
          ];
        };
      }
    );
}
