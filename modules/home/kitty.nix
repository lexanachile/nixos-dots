{ config, pkgs, ... }:

let
  dots = "${config.home.homeDirectory}/.local/share/nixos-dots";
in
{
  home.packages = with pkgs; [
    kitty
    nerd-fonts.jetbrains-mono
  ];

  xdg.configFile."kitty".source =
    config.lib.file.mkOutOfStoreSymlink
      "${dots}/dotfiles/kitty";
}
