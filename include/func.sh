#!/bin/bash

throw()
{
  err_no=$1
  echo $2
  exit $err_no
}

insapp()
{
  which $1 2>&1 > /dev/null && return 0
  [ $# -ne 1 ] && throw 255 "parameter error" 
  INSTALL=""
  which yum 2>&1 > /dev/null && INSTALL="yum install -y " 
  which apt-get 2>&1 > /dev/null && INSTALL="sudo apt-get install -y "
  [ "X$INSTALL" == "X" ] && throw 255 "which os ??"
  APP=$1
  $INSTALL $1
}

dl_and_install()
{
    local URL=$1
    local PKG=${URL##*/}
    local D_TMP=/tmp/somefiles
    local D_EXTRACT=$D_TMP/extract 
    local D_PWD=$(pwd)
    mkdir -p $D_TMP
    mkdir -p $D_EXTRACT
    wget -P $D_TMP $URL
    if [ ! -f $D_TMP/$PKG ]; then
        throw 11 "no file:$PKG"     
    fi    

    OPT=
    EXT=${PKG##*.}
    NAME_PKG=${PKG%.tar.$EXT}
    case "$EXT" in
      gz)  OPT="-zxf" ;;
      bz2) OPT="-jxf" ;;
      *) throw 12 "unsupported package" ;;
    esac 
    tar $OPT $D_TMP/$PKG -C $D_EXTRACT
    ls $D_EXTRACT/$NAME_PKG
    cd $D_EXTRACT/$NAME_PKG 
    if [ -f $D_EXTRACT/$NAME_PKG/configure ]; then
        $D_EXTRACT/$NAME_PKG/configure
    fi
    make && sudo make install
    cd $D_PWD
    rm -rf $D_TMP
}
