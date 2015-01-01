#!/usr/bin/env bash
#set +e
os=$(uname -s)
[[ "$os" != "Darwin" ]] && echo -e "just support mac os!!!\nExit !!!!" &&  exit 1

export d_root=$(cd "$(dirname $0)/.."; pwd)
export D_PRIV=$(cd $(dirname $0); pwd)
export D_PUB=$d_root/public
mkdir -p ~/.Trash

source $d_root/include/func.sh
handle_bashrc
handle_alias
handle_profile
link_apps $D_PRIV
link_apps $D_PUB

##====EOF=======
