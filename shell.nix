{ pkgs ? import <nixpkgs> {}}:
  pkgs.mkShell {
    nativeBuildInputs = let
      env = pyPkgs : with pyPkgs; [
        reportlab
      ];
    in with pkgs; [
      (python39.withPackages env)
    ];
}
