# Multipass Orchestrator

This is an UNOFFICIAL orchestrator using the [UNOFFICIAL Multipass Python SDK](https://github.com/okyanusoz/multipass-sdk)

## Installation

You need Multipass to use this orchestrator.

The version of multipass-sdk on pypi is out of date, first you have to install multipass-sdk from github:
```
pip install git+https://github.com/okyanusoz/multipass-sdk.git@main#egg=multipass-sdk
```

Next simply run:
```
pip install git+https://github.com/hdumcke/multipass-orchestrator@main#egg=multipass-orchestrator
```

Or, to install from source:


Clone this repo:

```
git clone --depth=1 https://github.com/hdumcke/multipass-orchestrator
```


Then run:
```
python setup.py install
```

## Usage

Usage is really simple:

Write a yaml file describing the environment you want to deploy and deploy it with:

```
mpo-deploy <config.yaml>
```

And when done:

```
mpo-delete <config.yaml>
```

### How it works

In your yaml configuration file you provide a list of VM names and attributes for each of these virtual machines. The mandatory attributes are:

- **cpu**: The numbers of virtual cpu for this instance
- **mem**: The amount of memory for this virtual instance
- **disk**: The disk size for this virtual instance
- **image**: The Ubuntu image for this virtual instance

Please refer to the Multipass documentation if you want to know more about these parameters and their values.

To customize the instance and run scripts use these optional parameters:

- **cloud_init** The path to a cloud-init file, useful to inject ssh keys
- **git_repos** A list of git repos that will be cloned in the instance. You can add a -b parameter to specify a branch
- **build_scripts** A list of paths to the build scripts in the above repos
- **run_scripts** A list of paths to scripts in the above repo that will be run after the build scripts

## Examples

```
git clone --depth=1 https://github.com/hdumcke/multipass-orchestrator
cd tests
multipass list
mpo-deploy simple.yaml
multipass list
multipass shell vm1
exit # leave vm
mpo-delete simple.yaml
multipass list
mpo-deploy test-environment.yaml
multipass list
ssh -o "IdentitiesOnly=yes" -i id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ubuntu@192.168.64.32 # use IP addess shown with multipass list
ls -la # see injected build and run script, see build and run log files
exit # leave vm
mpo-delete test-environment.yaml
multipass list
```
