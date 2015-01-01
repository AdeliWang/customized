#!/usr/bin/env bash
#set -e
#set -o pipefail
## TODO check OS

export d_root=$(cd "$(dirname $0)/.."; pwd)
export D_PRIV=$(cd $(dirname $0); pwd)
export D_PUB=$d_root/public
mkdir -p ~/.Trash

source $d_root/include/func.sh

echo "prepare to install some app from repository"
apps=("vim"
       "git" )
for var in ${apps[@]};do
    echo $var
    insapp $var
done

handle_bashrc
handle_alias
handle_profile
link_apps $D_PRIV
link_apps $D_PUB

##====EOF=======
