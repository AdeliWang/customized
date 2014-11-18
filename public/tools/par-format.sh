#!/usr/bin/env bash
dev=$1
echo -e "o\nn\np\n\n\n\n\nw\n" | fdisk $1
mkfs.ext4 $dev1
