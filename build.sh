#!/bin/bash

# Prepare folders.
if [ -d "./build" ]; then
    echo "Remove build folder."
    rm -rf ./build/*
else
    echo "Create build folder."
    mkdir ./build
fi

# Build backend flask.
echo "Copy python code to build folder..."
cp -a ./flask/* ./build/

# Build frontend react.
echo "Building react..."
cd react
npm run build
cd ..
echo "Move react files to flask folder..."
mv ./react/build ./build/static

# Generate version files.
date +"%Y-%m-%d %H:%M:%S %z" > ./build/build.ver
