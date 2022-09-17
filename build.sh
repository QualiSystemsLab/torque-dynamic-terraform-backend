#!/bin/bash
# needs to run in ubuntu

version=$(cat version.txt)
cd src
tar -czf ../dist/torqify_tf_backend.$version.tar.gz .
cd ..

cp torqify_tf_backend.sh ./dist/torqify_tf_backend.$version.sh
cat ./dist/torqify_tf_backend.$version.sh | sed -e "s/<VERSION>/${version}/g" > ./dist/torqify_tf_backend.$version.sh