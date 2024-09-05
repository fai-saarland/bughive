# Bug Hive

A collection of tools for Action Policy Testing.

The purpose of this project is to put together all different tools and projects
used in Action Policy Testing, plus some glue code to make them run together.

The project is still active.
Please check our [GitHub repository](https://github.com/fai-saarland/bughive) for newer versions.

## Building the Project

How the different components can be built is described in the following sections.
We only support Linux.

It may also be helpful to have a look at the provided `Dockerfile`.
In case you just want to use the software without building it yourself, you can pull the respective docker image from our [docker hub repository](https://hub.docker.com/repository/docker/janeisenhut/bughive).

## cpddl ASNets

ASNets policy server based on the cpddl implementation requires
[DyNet](https://github.com/clab/dynet). Once it is installed, set the
variable ``DYNET_ROOT`` to the root directory of the DyNet installation (e.g.,
by creating a file ``Makefile.config``) and compile the policy server with:

```sh
  $ make asnets
```

It creates a binary ``./policy-servers/asnets`` providing access to the specified learned
policy run on the specified pddl task via either tcp or unix socket connection.

Examples how to run it:

```sh
  # TCP bind to all addresses on the port 12345
  $ ./policy-servers/asnets *:12345 model.asnets domain.pddl problem.pddl
  # TCP on localhost and port 54321
  $ ./policy-servers/asnets localhost:54321 model.asnets domain.pddl problem.pddl
  # Connection via unix socket located at /tmp/asnets.sock
  $ ./policy-servers/asnets unix:///tmp/asnets.sock model.asnets domain.pddl problem.pddl
```

## GNN policy

The GNN policy server is based on "Learning Generalized Policies Without Supervision Using GNNs" by Ståhlberg, Bonet,
and Geffner.
To start the policy server, first activate the virtual environment that can be
created by `gnn/create-venv.sh` (or make an equivalent local installation of
dependencies listed in the script).
The policy server also requires `pyphrm`, i.e., a python interface to the
pheromone library, which can be built by invoking:
```sh
  $ make pheromone
```

Running the policy server for GNNs is then very similar to running the ASNet server.
However, it also requires a path to the FD driver script (to use its translator
to obtain the task in FDR representation).
```sh
  # TCP bind to all addresses on the port 12345
  $ ./policy-servers/gnns.py \
        --url *:12345 \
        --model 'gnn/data/models/blocks/epoch=112-step=98083.ckpt' \
        --domain gnn/data/pddl/blocks/test/domain.pddl \
        --problem gnn/data/pddl/blocks/test/probBLOCKS-10-0.pddl \
        --fd fd-action-policy-testing/fast-downward.py
```


## Fast Downward Action Policy Testing

The [Fast Downward Action Policy Testing](https://github.com/fai-saarland/fd-action-policy-testing) repository contains the source code for the actual testing tool (added as a git submodule here).

You can compile the testing engine with

```sh
  $ make fd-action-policy-testing
```

Now, you can use the tool e.g., for an execution of the policy as follows:

```sh
  # First start asnets policy server
  $ ./policy-servers/asnets *:12345 model.asnets domain.pddl problem.pddl
  # Then in a different terminal (unless you detach the policy server)
  $ ./fd-action-policy-testing/builds/release/bin/downward \
            --remote-policy localhost:12345 \
            --search 'astar(blind(), pruning=remote_policy_pruning())'
```

Check out the test drivers sections for a more convenient way for invoking the testing tool.
These will start the respective policy servers automatically (choosing a free port) and then invoke the testing tool setting the `--remote-policy` flag accordingly.

The README of the `fd-action-policy-testing` sub-module describes how to configure the testing engine, i.e., how to set the `--search` flag.

## Test Drivers

Instead of starting policy servers and connecting clients to it yourself, you can use the provided test driver scripts.
The ``test_drivers`` directory contains driver scripts for testing both ASNets and GNN based policies.
The scripts first start a policy server using a free port.
After that, they invoke the FD action policy testing tool, connecting it to the policy server.

### ASNet Policy Test Driver

The ASNet policy test driver script is `test_drivers/asnets_test_driver.py`. 
The ASNet policy server is in `./policy-servers/asnets`.
The usage is as follows:

```
usage: asnets_test_driver.py [-h] --model MODEL --domain DOMAIN --problem PROBLEM --downward DOWNWARD --search SEARCH [-t TIMEOUT] [-m MEM] [--fdmem FDMEM] asnet

Driver for debugging remote ASNet policies

positional arguments:
  asnet                 Path to the executable starting the ASNet server

options:
  -h, --help            show this help message and exit
  --model MODEL         Path to the policy model file (default: None)
  --domain DOMAIN       Path to the PDDL domain file, required if no sas file is provided (default: None)
  --problem PROBLEM     Path to the PDDL problem file, required if no sas file is provided (default: None)
  --downward DOWNWARD   Path to the downward executable (not the FD driver script) (default: None)
  --search SEARCH       Search configuration of FD (default: None)
  -t TIMEOUT, --timeout TIMEOUT
                        Time limit for the driver in seconds (default: None)
  -m MEM, --mem MEM     Memory limit for the driver in MiB (default: None)
  --fdmem FDMEM         Set maximal memory limit for FD process in MiB (default: None)
```

### GNN Policy Test Driver

The GNN policy test driver script is `test_drivers/gnns_test_driver.py`. 
The respective policy server is in `./policy-servers/gnns.py`.
The usage is as follows:

```
#usage: gnns_test_driver.py [-h] --gnn GNN [--fd FD] [--sas SAS] [--cpu] --model MODEL --domain DOMAIN --problem PROBLEM --downward DOWNWARD --search SEARCH [-t TIMEOUT] [-m MEM]
                           [--fdmem FDMEM]

Driver for debugging remote GNN policies

options:
  -h, --help            show this help message and exit
  --gnn GNN             Path to the executable starting the GNN server (default: None)
  --fd FD               Path to the FD driver script (for invoking the translator) (default: None)
  --sas SAS             Path to the task sas file (default: None)
  --cpu                 use CPU only in GNN server (default: False)
  --model MODEL         Path to the policy model file (default: None)
  --domain DOMAIN       Path to the PDDL domain file, required if no sas file is provided (default: None)
  --problem PROBLEM     Path to the PDDL problem file, required if no sas file is provided (default: None)
  --downward DOWNWARD   Path to the downward executable (not the FD driver script) (default: None)
  --search SEARCH       Search configuration of FD (default: None)
  -t TIMEOUT, --timeout TIMEOUT
                        Time limit for the driver in seconds (default: None)
  -m MEM, --mem MEM     Memory limit for the driver in MiB (default: None)
  --fdmem FDMEM         Set maximal memory limit for FD process in MiB (default: None)

```
