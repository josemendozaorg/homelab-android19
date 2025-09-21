{
  description = "Homelab Infrastructure Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          ansible
          ansible-lint
          yamllint
          requests
          pyyaml
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          name = "homelab-infrastructure";

          buildInputs = with pkgs; [
            # Core tools
            pythonEnv
            openssh
            git
            curl
            wget
            vim
            make

            # Container tools
            docker
            docker-compose

            # Network tools
            netcat
            nmap

            # Development tools
            jq
            yq

            # Ansible tools
            ansible-lint
            yamllint
          ];

          shellHook = ''
            echo "🏠 Homelab Infrastructure Development Environment"
            echo "================================================"
            echo "Available tools:"
            echo "  • Ansible: $(ansible --version | head -1)"
            echo "  • Python: $(python --version)"
            echo "  • Docker: $(docker --version)"
            echo ""
            echo "Quick start:"
            echo "  • ansible all -i inventory.yml -m ping"
            echo "  • make help"
            echo ""

            # Set up environment variables
            export ANSIBLE_HOST_KEY_CHECKING=false
            export ANSIBLE_STDOUT_CALLBACK=yaml
            export ANSIBLE_INVENTORY=inventory.yml

            # Create SSH directory if it doesn't exist
            mkdir -p ~/.ssh
            chmod 700 ~/.ssh
          '';

          # Environment variables
          ANSIBLE_HOST_KEY_CHECKING = "false";
          ANSIBLE_STDOUT_CALLBACK = "yaml";
        };

        # Package the environment for building
        packages.default = pkgs.stdenv.mkDerivation {
          name = "homelab-infrastructure";
          src = ./.;

          buildInputs = [ pythonEnv ];

          installPhase = ''
            mkdir -p $out/bin
            cp -r . $out/
          '';
        };
      });
}