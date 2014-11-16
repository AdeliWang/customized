#!/bin/bash

throw()
{
  err_no=$1
  echo $2
  exit $err_no
}

app_install()
{
  [ $# -ne 1 ] && throw 255 "parameter error" 
  INSTALL=""
  which yum 2>&1 > /dev/null && INSTALL="yum install -y " 
  which apt-get 2>&1 > /dev/null && INSTALL="apt-get install -y "
  [ "X$INSTALL" == "X" ] && throw 255 "which os ??"
  APP=$1
  $INSTALL $1
}
