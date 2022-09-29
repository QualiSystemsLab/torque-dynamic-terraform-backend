[![CI](https://github.com/QualiSystemsLab/torque-dynamic-terraform-backend/actions/workflows/CI.yml/badge.svg)](https://github.com/QualiSystemsLab/torque-dynamic-terraform-backend/actions/workflows/CI.yml)
[![Coverage Status](https://coveralls.io/repos/github/QualiSystemsLab/torque-dynamic-terraform-backend/badge.svg?branch=master)](https://coveralls.io/github/QualiSystemsLab/torque-dynamic-terraform-backend?branch=master)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python/)

# torque-dynamic-terraform-backend


## Why use "dynamic terraform backend" in Torque?
It's generally considered a best practice to use remote backends in Terraform to save the state file in a remote location. 
There are a lot of advantages compared to local state.

Part of the benefits of using Torque with Terraform is that it helps keep your Terraform code DRY (don't repeat yourself).
Which means that you can reuse the same Terraform configuration to launch multiple environments without duplicating your code. 
The same Terraform code can be used in multiple blueprint templates where each blueprint can be used to launch multiple environments. 

![image](https://user-images.githubusercontent.com/6730546/191409441-f777e42d-8a7a-47e8-a552-ebf357b295b4.png)

If your Terraform code is using a remote backend, and you will use it "as is" in Torque then bad things will happen because
multiple, completely separate and standalone, environment executions will try to use the same state file. Use solution to avoid 
this issue and to "torqify" your remote backend. This solution will automatically detect the backend configuration and inject
the Torque environment ID to the name of the state file ensuring that the Terraform execution in each standalone environment
has a unique state file.

## Installing

1. Download "torqify_tf_backend.X.Y.Z.sh" file from the latest release. 
2. Commit this script to a Torque Asset repo that is connected to your Torque space.
3. For any TF grain yaml that you want to "torqify" it's backend configurations, add a "pre-tf-init" script section 
that references the "torqify_tf_backend.X.Y.Z.sh" script. Example:
```yaml
pre-tf-init:
  source:
    store: <repo name in Torque>
    path : <path in repository>/torqify_tf_backend.x.y.z.sh
  arguments: '{{ sandboxid | downcase }}'
```
Note: "torqify_tf_backend.X.Y.Z.sh" is a simple bootstrap script. It will install some dependencies on the Torque agent,
next it will download the main python package and run it (that's where the magic happens). All the arguments that were 
provided to this runner script will be forwarded as is to the main python file.

## Basic Usage

The following shows an example of how to use this solution with a Torque Terraform grain. Look at the "pre-tf-init" section for usage example. 

Replace all placeholders "<...>" with real values. For more information about Torque yaml syntax refer to [Torque docs](https://docs.qtorque.io/blueprint-designer-guide/blueprints).

```yaml
grains:
  <grain_name>:
    kind: terraform
    tf-version: 1.2.9
    spec:
      source:
        store: <repo name in Torque>
        path: <path in repository>
      scripts: 
        pre-tf-init:
          source:
            store: <repo name in Torque>
            path : <path in repository>/torqify_tf_backend.0.1.2.sh
          arguments: '{{ sandboxid | downcase }}'
      host:
        name: <host execution name>
      inputs:
        - input1: '{{ .inputs.value1 }}'
        - input1: '{{ .inputs.value2 }}'
      outputs:
      - output1
      - output2    
```

## CLI Interface
```
usage: torqify_tf_backend [-h] [-d] [-e [EXCLUDE [EXCLUDE ...]]] sandbox_id

Automatically add sandbox id to terraform remote backend

positional arguments:
  sandbox_id            The Torque sandbox ID. This value will be used for uniqueness.

optional arguments:
  -h, --help            show this help message and exit
  -d, --data            If this flag is provided, will also add sandbox id to all remote_state data sources.To exclude certain remote_state data sources use the '-e' option.
  -e [EXCLUDE [EXCLUDE ...]], --exclude [EXCLUDE [EXCLUDE ...]]
                        Use this flag to provide a list of names of remote_state data sources to exclude from adding the sandbox id automatically. If this flag is provided without also
                        specifying the '-d'/'--data' flag then it will be ignored.
```

## Supported remote backends

The following remote backends are currently supported:
* [s3](https://www.terraform.io/language/settings/backends/s3)
* [gcs](https://www.terraform.io/language/settings/backends/gcs)
* [azurerm](https://www.terraform.io/language/settings/backends/azurerm)


## License
[Apache License 2.0](https://github.com/QualiSystemsLab/torque-dynamic-terraform-backend/blob/master/LICENSE)
