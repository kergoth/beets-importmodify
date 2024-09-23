{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    nativeBuildInputs = [
      (pkgs.python310.withPackages (ps: with ps; [ pip pyyaml ]))
      pkgs.python39
      pkgs.python38
    ];
}
