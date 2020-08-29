
@echo off

echo Prepare folders.
rmdir /s /q build
mkdir build

echo Copy python flask to build folder.
xcopy /e /h flask build

echo Building react...
cd react
npm run build
cd ..

echo Move react files to flask folder...
move react/build build/static

