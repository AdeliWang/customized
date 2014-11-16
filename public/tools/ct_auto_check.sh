#!/bin/bash

#git clone git://cpg-code.cisco.com/mf.git

DIR_MF="~/studio/mf"
cd $DIR_MF
git pull
if [ $? -ne 0 ]; then 
  echo "failed to update mf !!"
  exit 1
fi

DIR_WEB="~/studio/webgui" 
cd $DIR_WEB
git pull
if [ $? -ne 0 ]; then 
  echo "failed to update webgui !!"
  exit 1
fi

DIR_CC_MF="/vob/dsbu_proj/REPO/cpgmgt-service/cpgmgt-service"
DIR_CC_MF_OBJ=$DIR_CC_MF/cpgmgt_service_object
if [ ! -d $DIR_CC_MF ]; then
  echo "please set view!!"
  exit 1
fi

cc_update -m LATEST
DIR_MF_OBJ=$DIR_MF/cpgmgt_service_object
diff -q $DIR_MF_OBJ $DIR_CC_MF_OBJ
