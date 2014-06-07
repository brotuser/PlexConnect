#!/bin/bash
sudo apt-get install libjpeg-dev

MACHINE_TYPE=`uname -m`
if [ ${MACHINE_TYPE} == 'x86_64' ]; then
  sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib
  sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib
  sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib
else
  sudo ln -s /usr/lib/i386-linux-gnu/libjpeg.so /usr/lib/
  sudo ln -s /usr/lib/i386-linux-gnu/libfreetype.so.6 /usr/lib/
  sudo ln -s /usr/lib/i386-linux-gnu/libz.so /usr/lib/
fi

sudo easy_install pip

pip install pillow  -I

