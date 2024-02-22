# Bug Hive

A collection of tools for Action Policy Testing.

The purpose of this project is to put together all different tools and projects
used in Action Policy Testing, plus some glue code to make them run together.

## cpddl ASNets

The ASNet policy server based on the cpddl implementation requires
[DyNet](https://github.com/clab/dynet) library. Once it is installed, set the
variable ``DYNET_ROOT`` to the root directory of the DyNet installation (e.g.,
by creating a file ``Makefile.config``) and compile the policy server with:

```sh
  $ make asnets
```

It creates a binary ``./policy-servers/asnets`` providing access to the specified learned
policy run on the specified pddl task via either tcp or unix socket connection.

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
## New Fuzzing Biases Paper

This branch contains the version of the source code that was used for running the experiments for the ICAPS 2024 paper "New Fuzzing Biases for Action Policy Testing":

```
@InProceedings{eisenhut-et-al-icaps24, 
    title     = {New Fuzzing Biases for Action Policy Testing},
    author    = {Eisenhut, Jan and Schuler, Xandra and Fišer, Daniel and Höller, Daniel and Christakis, Maria and Hoffmann, Jörg},
    booktitle = {Proceedings of the 44th International Conference on Automated Planning and Scheduling ({ICAPS}'24), 2024},
    year      = {2024}
}
```
Please have a look at the master branch for the current version of the project.

### Benchmarks

The benchmarks (including the policy files) are located the `benchmarks` folder.

### Building

After making sure the dependencies are installed (see above). You can build the project using the provided Makefile (by running `make all`).

### Usage

Please use the test drivers in the `test_drivers` directory to run the tool.

Here are two basic examples (for ASNets and GNNs) for the general way you can invoke the test drivers (assuming you are in the root directory of this repository).

```sh
./test_drivers/asnets_test_driver.py policy-servers/asnets --model <path/to/asnet/policy> \
  --domain <path/to/domain/file> --problem <path/to/problem/file> \
  --downward fd-action-policy-testing/builds/release/bin/downward \
  --search <search config>
```

```sh
./test_drivers/gnns_test_driver.py --gnn policy-servers/gnns.py --model <path/to/gnn/policy> \
  --domain <path/to/domain/file> --problem <path/to/problem/file> \
  --fd fd-action-policy-testing/fast-downward.py
  --downward fd-action-policy-testing/builds/release/bin/downward \
  --search <search config>
```

#### Fuzzing Step

Here is an example for `<search config>` for the fuzzing step.

```
pool_fuzzer(max_steps=10000000,max_pool_size=100,eval=hmax(),max_walk_length=5,pool_file=<path/to/pool/file/for/result>,penalize_policy_fails=true,bias_budget=200,cache_bias=false[,bias=<bias>])
```
where bias=<bias> must be omitted if no bias is to be used. 

Here is a selection of bias configs you can choose:

* policy quality bias: `plan_length_bias(horizon=50)`
* detour bias with FF: `detour_bias(h=ff(),horizon=50,omit_maximization=false)`
* detour bias with hstar: `detour_bias(horizon=50,ipo=internal_planner_plan_cost_estimator(conf=astar_lmcut,continue_after_time_out=false),omit_maximization=true)`
* surface bias with FF: `surface_bias(h=ff(),horizon=50, omit_maximization=false)`
* surface bias with hstar: `surface_bias(horizon=50,ipo=internal_planner_plan_cost_estimator(conf=astar_lmcut,continue_after_time_out=false),omit_maximization=true)`
* loopiness bias with FF: `loopiness_bias(h=ff(), horizon=50,omit_maximization=false)`
* loopiness bias with hstar: `loopiness_bias(horizon=50,ipo=internal_planner_plan_cost_estimator(conf=astar_lmcut,continue_after_time_out=false),omit_maximization=false)`

#### Precomputing Dominance Functions

If you use an oracle that requires computing a dominance function, you might want to procompute it and store it in a simulation file (in order to load it multiple times).
You can achieve that by selecting `<search config>` to:

```
dummy_engine(testing_method=dummy_oracle(abs=builder_massim(merge_strategy=merge_dfp(),limit_transitions_merge=10000),write_sim_and_exit=true,sim_file=<path/to/sim/file/for/result>,max_simulation_time=1800,max_total_time=7200))
```

#### Oracle Step

In order to run the oracle, you can select this `<search config>`:
```
pool_policy_tester(max_time=<time limit in seconds>,pool_file=<path/to/pool/file>,testing_method=<oracle>)
```
where `<oracle>` could be:

```
composite_oracle(qual_oracle=estimator_based_oracle(oracle=internal_planner_plan_cost_estimator(conf=ehc_ff,max_planner_time=300)),\
quant_oracle=aras(aras_dir=<path/to/aras/tool>,aras_max_time_limit=300),\
metamorphic_oracle=iterative_improvement_oracle(conduct_lookahead_search=true,lookahead_heuristic=ff(),consider_intermediate_states=true,read_simulation=true,sim_file=<path/to/simulation/file>))
```
