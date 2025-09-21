# Legacy shell.nix for non-flake users
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "homelab-infrastructure";

  buildInputs = with pkgs; [
    # Python with Ansible
    (python311.withPackages (ps: with ps; [
      ansible
      ansible-lint
      yamllint
      requests
      pyyaml
    ]))

    # Essential tools
    openssh
    git
    curl
    wget
    vim
    make

    # Container tools
    docker
    docker-compose

    # Network utilities
    netcat
    nmap

    # Development tools
    jq
    yq
  ];

  shellHook = ''
    echo "🏠 Homelab Infrastructure (Legacy Nix Shell)"
    echo "============================================"
    echo "Run 'ansible --version' to verify installation"
    echo "Use 'make help' to see available commands"

    export ANSIBLE_HOST_KEY_CHECKING=false
    export ANSIBLE_STDOUT_CALLBACK=yaml
  '';
}