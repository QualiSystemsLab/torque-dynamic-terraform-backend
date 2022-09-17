#!/bin/bash
# needs to run in debian

version=<VERSION>
package_url=https://github.com/QualiSystemsLab/torque-dynamic-terraform-backend/releases/download/v<VERSION>/cloudshell-email-<VERSION>.tar.gz

# get environment id from cli args
env_id=$1

# install curl
echo "===> Installing curl"
apt update
apt install curl

# download python package
echo "===> Downloading package"
curl -s -L  -o torqify_tf_backend.tar.gz

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