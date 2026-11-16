{
  description = "all of my nix";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

    home-manager = {
      url = "github:nix-community/home-manager/master";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    elephant.url = "github:abenz1267/elephant";
    walker = {
      url = "github:abenz1267/walker";
      inputs.elephant.follows = "elephant";
    };
  };

  outputs = inputs@{ nixpkgs, home-manager, ... }:
    let
      mkHome = {
        system,
        username,
        homeDirectory,
        userModule,
        hostModule,
      }:

      home-manager.lib.homeManagerConfiguration {
       pkgs = import nixpkgs {
        inherit system;
        config.allowUnfree = true;
       };

        modules = [
        userModule
         hostModule
         {
           home = {
             inherit username homeDirectory;
              stateVersion = "26.05";
            };
          }
        ];

        extraSpecialArgs = {
          inherit inputs;
        };
      };
    in
    {
      homeConfigurations = {
        "aliaksei@gungnir" = mkHome {
        system = "x86_64-linux";
        username = "aliaksei";
        homeDirectory = "/home/aliaksei";

        userModule = ./users/aliaksei/home.nix;
        hostModule = ./hosts/gungnir/home.nix;
      };
    };
  };
}

