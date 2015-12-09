#!/bin/sh

echo "Cleaning targets..."
rm -rf build dist libs SimpleDFULoader.dmg
echo "Packaging with py2app..."
python setup.py py2app
echo "Fixing dependencies..."
dylibbundler -od -b -x ./Dist/SimpleDFULoader.app/Contents/MacOS/SimpleDFULoader
echo "Making DMG..."
appdmg dmg.json ./SimpleDFULoader.dmg
echo "DONE!"