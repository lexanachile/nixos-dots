{ config, pkgs, ... }:

let
  dots = "${config.home.homeDirectory}/.local/share/nixos-dots";
in
{
  home.packages = with pkgs; [
    niri
  ];

  xdg.configFile."niri".source = 
    config.lib.file.mkOutOfStoreSymlink
      "${dots}/dotfiles/niri";

  xdg.configFile."systemd/user/niri.service".source = 
    "${pkgs.niri}/lib/systemd/user/niri.service";

  xdg.configFile."systemd/user/niri-shutdown.target".source =
    "${pkgs.niri}/lib/systemd/user/niri-shutdown.target";

  xdg.configFile."xdg-desktop-portal/niri-portals.conf".source =
    "${pkgs.niri}/share/xdg-desktop-portal/niri-portals.conf";
}
