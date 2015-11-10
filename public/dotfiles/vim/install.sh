#!/bin/bash

git clone https://github.com/VundleVim/Vundle.vim.git ~/.vimrcs/bundle/Vundle.vim
mv ~/.vimrc ~/.vimrc.bakup.`date "+%Y%m%d.%T"`
cp vimrc ~/.vimrc
cp vimrcs/*.vim ~/.vimrcs/
sudo cp bin/tagscope /usr/local/bin/

vim +PluginInstall +qall
