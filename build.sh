#!/bin/bash
# needs to run in ubuntu

version=$(cat version.txt)
mkdir dist
cd src
tar -czf ../dist/torqify_tf_backend.$version.tar.gz .
cd ..

cp ./runner/torqify_tf_backend.sh ./dist/torqify_tf_backend.$version.sh
cat ./dist/torqify_tf_backend.$version.sh | sed -e "s/<VERSION>/${version}/g" > ./dist/torqify_tf_backend2.$version.sh

echo "===> debugging"
ls -l ./dist
echo "print torqify_tf_backend.sh for debugging"
cat ./dist/torqify_tf_backend.$version.sh
