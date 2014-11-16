#!/bin/env bash

#
# step 1. run command:< ssh-keygen -t rsa > to gen ssh key on client machine
# step 2. copy the id_rsa.pub and append to  authorized_keys.
##  cat id_dsa.pub >> ~/.ssh/authorized_keys 
# step 3
chmod 600 ~/.ssh/authorized_keys
chmod 700  ~/.ssh

