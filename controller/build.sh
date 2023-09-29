#!/bin/bash

CWD_DIR="$(pwd)"
SCRIPT_DIR="$(dirname -- "${BASH_SOURCE[0]}")"
cd "${SCRIPT_DIR}"

export RTRM_COMM_DIR="/home/miele/Vivian/Thesis/Thesis-Communication"
export BOOST_DIR="/home/miele/Vivian/Thesis/margot/boost_1_60_0/install"

rm -rf build
mkdir build
(
    cd build && 	\
    cmake .. && 	\
    cmake --build . \
)

cd "${CWD_DIR}"
