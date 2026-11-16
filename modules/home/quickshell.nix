{ config, ... }:

let
  dots = "${config.home.homeDirectory}/.local/share/nixos-dots";
in
{
  programs.quickshell = {
    enable = true;
    systemd.enable = false;
  };

  xdg.configFile."quickshell".source =
    config.lib.file.mkOutOfStoreSymlink
      "${dots}/dotfiles/quickshell";
}
