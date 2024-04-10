#!/bin/bash

# Array containing SSH addresses of the VMs
#vms=("ubuntu@node0" "ubuntu@node1" "ubuntu@snf-74112" "ubuntu@snf-74113" "ubuntu@snf-74114")
vms=("ubuntu@192.168.0.3:~")

# Git repository URL to clone
repo_url="https://github.com/terezann/ChatBlock.git"

# Directory to clone the repository into
from_dir="/home/terez/development/distributed/"

# Perform git clone operation on each VM
for vm in "${vms[@]}"; do
    echo "Cloning repository on $vm..."
    scp -r "$from_dir" "$vm"
    ssh "$vm" "git clone $repo_url"
    echo "Done cloning repository on $vm"
done

