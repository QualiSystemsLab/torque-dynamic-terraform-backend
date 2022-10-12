#!/bin/bash
# needs to run in debian

# exit when any command fails
set -e

version=<VERSION>
package_url="https://github.com/QualiSystemsLab/torque-dynamic-terraform-backend/releases/download/v$version/torqify_tf_backend.$version.tar.gz"

# download python package
echo "===> Downloading 'torqify_tf_backend' package from url: $package_url"
curl -L $package_url -o torqify_tf_backend.tar.gz

# extract package
echo "===> Extracting package"
mkdir torqify_tf_backend
tar -xvf torqify_tf_backend.tar.gz -C ./torqify_tf_backend
cd torqify_tf_backend

# install python dependencies
echo "===> Installing python dependencies"
pip3 install -r requirements.txt

# run python package
echo "===> Running torqify_tf_backend package"
python3 main.py $@

echo "===> Done"