# Bug Hive

A collection of tools for Action Policy Testing.

The purpose of this project is to put together all different tools and projects
used in Action Policy Testing, plus some glue code to make them run together.

## cpddl ASNets

ASNets policy server based on the cpddl implementation requires
[DyNet](https://github.com/clab/dynet) library. Once it is installed, set the
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

``fd-action-policy-testing`` includes an example how to implement client
connecting to policy servers. Compile it with

```sh
  $ make fd-action-policy-testing
```

Now, you can use for an execution of the policy by

```sh
  # First start asnets policy server
  $ ./policy-servers/asnets *:12345 model.asnets domain.pddl problem.pddl
  # Then in a different terminal (unless you detach the policy server)
  $ ./fd-action-policy-testing/builds/release/bin/downward \
            --remote-policy localhost:12345 \
            --search 'astar(blind(), pruning=remote_policy_pruning())'
```
