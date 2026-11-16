{ config, pkgs, inputs, ... }:

let 
  dots = "${config.home.homeDirectory}/.local/share/nixos-dots";
in
{
  imports = [
    inputs.walker.homeManagerModules.default
  ];

  home.packages = with pkgs; [
    wl-clipboard
    imagemagick
  ];

  programs.walker = {
    enable = true;
    runAsService = true;
    config = {};
  };

  programs.elephant = {
    enable = true;
    installService = true;

    providers = [
      "desktopapplications"
      "runner"
      "calc"
      "files"
      "providerlist"
      "clipboard"
    ];
  };

  xdg.configFile."walker".source =
    config.lib.file.mkOutOfStoreSymlink
      "${dots}/dotfiles/walker";

  xdg.configFile."elephant/elephant.toml".source =
    config.lib.file.mkOutOfStoreSymlink
      "${dots}/dotfiles/elephant/elephant.toml";

  xdg.configFile."elephant/clipboard.toml".source =
    config.lib.file.mkOutOfStoreSymlink 
      "${dots}/dotfiles/elephant/clipboard.toml";
}
