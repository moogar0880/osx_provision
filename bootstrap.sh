#!/bin/bash

set -e

SRC_DIRECTORY="$HOME/.deploy"
ANSIBLE_DIRECTORY="$SRC_DIRECTORY/ansible"
ANSIBLE_CONFIGURATION_DIRECTORY="$HOME/.ansible.d"

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
fi

# Make the code directory
mkdir -p ${SRC_DIRECTORY}

# Clone down ansible
if [[ ! -d ${ANSIBLE_DIRECTORY} ]]; then
    git clone -b devel git://github.com/danieljaouen/ansible.git ${ANSIBLE_DIRECTORY}
fi

# Use the forked Ansible
source ${ANSIBLE_DIRECTORY}/hacking/env-setup > /dev/null

# Clone down the Ansible repo
if [[ ! -d ${ANSIBLE_CONFIGURATION_DIRECTORY} ]]; then
    git clone git@bitbucket.org:danieljaouen/ansible-base-box.git ${ANSIBLE_CONFIGURATION_DIRECTORY}
    (cd ${ANSIBLE_CONFIGURATION_DIRECTORY} && git submodule init && git submodule update)
fi

# Provision the box
ansible-playbook --ask-sudo-pass -i ${ANSIBLE_CONFIGURATION_DIRECTORY}/inventories/osx ${ANSIBLE_CONFIGURATION_DIRECTORY}/site.yml --connection=local

# Link the casks.
~/.bin/link-casks