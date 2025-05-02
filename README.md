# Bug Hive

A collection of tools for Action Policy Testing.

The purpose of this project is to put together all different tools and projects
used in Action Policy Testing, plus some glue code to make them run together.

## ICAPS'25 paper

This branch contains the version of the source code that was used for running the experiments for the ICAPS 2025 paper "On Picking Good Policies: Leveraging Action-Policy Testing in Policy Training":

```
@InProceedings{eisenhut-et-al-icaps25, 
    title     = {On Picking Good Policies: Leveraging Action-Policy Testing in Policy Training},
    author    = {Eisenhut, Jan and Fišer, Daniel and Valera, Isabel and Hoffmann, Jörg},
    booktitle = {Proceedings of the 45th International Conference on Automated Planning and Scheduling ({ICAPS}'25)},
    year      = {2025}
}
```

### Benchmarks

The benchmarks (pddl files) are in `benchmarks.zip`. For the examples below we assume you unzip it in the bughive directory, i.e., by running `unzip benchmarks.zip` in the top level directory.

### Building

You can build the project using the provided Makefile in the top-level directory.

On Ubuntu, all required resources should be available using apt (e.g., boost, grpc, protobuf). The boost version must be at least 1.74.

### Lab

Testing during training uses (the local environment of the) lab framework (upstream documentation, see [here](https://lab.readthedocs.io/en/stable/)).

We use a slightly adapted version, provided in `lab.zip`.

To set up a virtual environment using this lab version, you can do the following:

```
unzip lab.zip
cd lab
python3 -m venv --prompt custom-lab .venv
source .venv/bin/activate
pip install -U pip wheel
pip install --editable .
```
The environment must also include toml (`pip install toml`).

### ASNets Training

The `configs` directory contains configuration files for the variants shown in the paper. Note that for the line and tree configurations, there is a number of equivalent configurations: as training does not depend on the test result, one can reach the same policy by testing each trained policy immediately after if was trained (as used here), by testing everything offline after training or by using a parallel testing server.

Here is an example for how it can be invoked (make sure the project is build, `benchmarks.zip` is unzipped, and lab is activated):

```
cd /path/to/bughive
mkdir tmp
cd tmp
./../prepare-train-run.sh debug-domain ../configs/debug.toml
./train.sh
```

After each training epoch a `.stats` file is generated. It contains the rankings the policy selection is based on.

### Testing Final Policies

For running policy testing on the final policies (on the test set), we recommend using the provided ASNets test driver (see `./test_drivers/asnets_test_driver.py --help`).

We precomputed pools and simulation files. The search configuration for the oracle step is:

`pool_policy_tester(pool_file="<path/to/pool_file>", testing_method=composite_oracle(qual_oracle=estimator_based_oracle(oracle=internal_planner_plan_cost_estimator(conf=ehc_ff, max_planner_time=60)),quant_oracle=aras(aras_dir="<path/to/aras>",aras_max_time_limit=60),metamorphic_oracle=iterative_improvement_oracle(conduct_lookahead_search=true,lookahead_heuristic=ff(),consider_intermediate_states=true,read_simulation=true, sim_file="<path/to/sim_file>")), read_policy_cache=false, max_time=43200, abstain_if_first_state_not_known_solved=true)`






