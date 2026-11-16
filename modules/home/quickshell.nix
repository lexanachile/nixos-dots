{ config, pkgs, ... }:

let
  dots = "${config.home.homeDirectory}/.local/share/nixos-dots";
in
{
  programs.quickshell = {
    enable = true;
    package = pkgs.quickshell;
    systemd.enable = false;
  };
  
  home.packages = with pkgs; [
    power-profiles-daemon

    pywal
    pamixer
    playerctl
    grim
    slurp

    inter
    material-design-icons
  ];

  fonts.fontconfig.enable = true;

  xdg.configFile."quickshell".source =
    config.lib.file.mkOutOfStoreSymlink
      "${dots}/dotfiles/quickshell";
}
