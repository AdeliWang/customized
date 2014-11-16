#!/usr/bin/env bash

set +e

d_cur=$(pwd)

mkdir -p ~/.Trash

rm ~/.customize
ln -s $d_cur ~/.customize

test -f ~/.bashrc || touch ~/.bashrc
[ $(grep -c bash_aliases ~/.bashrc) -eq 0 ] && echo "test -f ~/.bash_aliases && source ~/.bash_aliases" >> ~/.bashrc

fn=bash_profile
[ -f ~/.$fn ] && rm -f ~/.$fn
ln -s $d_cur/dotfiles/tmux/$fn ~/.$fn

fn=bash_aliases
[ -f ~/.$fn ] && rm -f ~/.$fn
ln -s $d_cur/dotfiles/$fn ~/.$fn

fn=tmux.conf
[ -f ~/.$fn ] && rm -f ~/.$fn
ln -s $d_cur/dotfiles/tmux/$fn ~/.$fn
