{ pkgs ? import <nixpkgs> {}}:
  pkgs.mkShell {
    nativeBuildInputs = let
      env = pyPkgs : with pyPkgs; [
        reportlab
        requests
      ];
    in with pkgs; [
      (python39.withPackages env)
    ];
}
