#!/bin/bash

set -e

SRC_DIRECTORY="$HOME/.deploy"
ANSIBLE_DIRECTORY="$SRC_DIRECTORY/osx_provision"

# Download and install Command Line Tools
if [[ ! -x /usr/bin/gcc ]]; then
    echo "Info   | Install   | xcode"
    xcode-select --install
fi

# Download and install Homebrew
if [[ ! -x /usr/local/bin/brew ]]; then
    echo "Info   | Install   | homebrew"
    ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/homebrew/go/install)"
fi

# Modify the PATH
export PATH=/usr/local/bin:$PATH

# Download and install Ansible
if [[ ! -x /usr/local/bin/ansible ]]; then
    brew install ansible
    brew install caskroom/cask/brew-cask
fi

# Make the code directory
mkdir -p ${SRC_DIRECTORY}

# Provision the box
# ansible-playbook --ask-sudo-pass -i inventory local.yml --connection=local
ansible-playbook --ask-sudo-pass -i ${ANSIBLE_DIRECTORY}/inventory ${ANSIBLE_DIRECTORY}/local.yml --connection=local

# Link the casks.
~/.bin/link-casks