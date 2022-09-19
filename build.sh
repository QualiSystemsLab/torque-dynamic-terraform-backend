#!/bin/bash
# needs to run in ubuntu

version=$(cat version.txt)
mkdir dist
cd src
tar -czf ../dist/torqify_tf_backend.$version.tar.gz .
cd ..

cat ./runner/torqify_tf_backend.sh | sed -e "s/<VERSION>/${version}/g" > ./dist/torqify_tf_backend.$version.sh

echo "===> list dist folder"
ls -l ./dist
