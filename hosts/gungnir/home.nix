{ ... }:

{
  imports = [
    ../../profiles/niri-desktop.nix
  ];

# nix-fedora integration
  targets.genericLinux.enable = true;
}
