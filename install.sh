#!/bin/bash

# based on script at https://github.com/dinosec/ubertooth-install/blob/master/ubertooth_install.sh
# chmod u+x install_ubertooth_tools.sh

# Versions
VERSION=2017-03-R2
UBER_VERSION=2017-03-R2
# WIRESHARK_VERSION=1.12.6

LIBBTBB_URL=https://github.com/greatscottgadgets/libbtbb/archive/$UBER_VERSION.tar.gz
LIBBTBB_FILENAME=libbtbb-$UBER_VERSION.tar.gz
LIBBTBB_DIR=libbtbb-$UBER_VERSION

UBERTOOTH_URL=https://github.com/greatscottgadgets/ubertooth/releases/download/$UBER_VERSION/ubertooth-$UBER_VERSION.tar.xz
UBERTOOTH_FILENAME=ubertooth-$UBER_VERSION.tar.xz
UBERTOOTH_DIR_HOST=ubertooth-$UBER_VERSION/host
UBERTOOTH_DIR=ubertooth-$UBER_VERSION

# echo
# echo "installing dependencies (linux)..."
# sudo apt-get -y install cmake libusb-1.0-0-dev make gcc g++ libbluetooth-dev \
# pkg-config libpcap-dev python-numpy python-pyside python-qt4


echo
echo "installing libbtbb..."
cd ~
# wget $LIBBTBB_URL -O $LIBBTBB_FILENAME
# tar xf $LIBBTBB_FILENAME
cd ~/libbtbb
mkdir build
cd build
cmake ..
make
sudo make install

echo
echo "installing ubertooth..."
cd ~
# wget $UBERTOOTH_URL -O $UBERTOOTH_FILENAME
# tar xf $UBERTOOTH_FILENAME
cd ~/ubertooth/host
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

# echo
# echo "installing ubertooth BTBB wireshark plugin..."
# cd ~
# sudo apt-get -y install wireshark wireshark-dev libwireshark-dev cmake
# cd $LIBBTBB_DIR/wireshark/plugins/btbb
# mkdir build
# cd build
# cmake -DCMAKE_INSTALL_LIBDIR=$WIRESHARK_PLUGINS_DIR ..
# make
# sudo make install

# echo
# echo "installing ubertooth BT BR/EDR wireshark plugin..."
# cd ~
# sudo apt-get -y install wireshark wireshark-dev libwireshark-dev cmake
# cd $LIBBTBB_DIR/wireshark/plugins/btbredr
# mkdir build
# cd build
# cmake -DCMAKE_INSTALL_LIBDIR=$WIRESHARK_PLUGINS_DIR ..
# make
# sudo make install

echo
echo "Finished!"
