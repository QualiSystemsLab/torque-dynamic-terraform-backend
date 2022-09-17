#!/bin/bash
# needs to run in debian

# exit when any command fails
set -e

version=<VERSION>
package_url="https://github.com/QualiSystemsLab/torque-dynamic-terraform-backend/releases/download/v$version/torqify_tf_backend.$version.tar.gz"

# get environment id from cli args
env_id=$1
echo "===> Environment id: $env_id"

# install curl
echo "===> Installing curl"
apt update -y
apt install curl -y

# download python package
echo "===> Downloading package from url: $package_url"
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
echo "===> Running package"
python3 main.py $env_id

echo "===> Done"