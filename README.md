# Policy Comparison Oracles for Action Policy Testing

This repository contains the source code for the Policy Comparison Oracles (PCOs) presented in the paper "Policy Comparison Oracles for Action Policy Testing".
They are implemented within the Action-Policy Testing framework.

The purpose of this project is to put together all different tools and projects
used in the paper, plus some glue code to make them run together.
Documentation for the available configurations of Multi-Policy search and PCOs can be found below.

## Building the Project

In case all necessary dependencies are installed, you can build the project by running `make` in the top level directory.
We only support Linux.

## Using Aras

Some oracles depend on Aras.
We have included a version of Aras in resources folder of the fd-action-policy-testing submodule.
You can build it by running `cd resources; unzip aras.zip -d aras && cd aras/src && ./build_all`.

## Example scripts

In the "pco-example.zip" archive, we provide small examplatory python scripts alongside domain and policy files that show how to run Multi-Policy search and PCOs.

## Benchmarks and Policies

The benchmarks and policies used in the paper can be found in the benchmarks directory.

## Fast Downward Action Policy Testing

The fd-action-policy-testing submodule contains the source code for the actual testing tool.

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
The ``test-drivers`` directory contains driver scripts for testing ASNets based policies.
The scripts first start a policy server using a free port.
After that, they invoke the FD action policy testing tool, connecting it to the policy server.

### ASNet Policy Test Driver

The ASNet policy test driver script is `test-drivers/asnets_test_driver.py`. 
The ASNet policy server is in `./policy-servers/asnets`.
The usage is as follows:

```
usage: asnets_test_driver.py [-h] --asnet ASNET --model MODEL [MODEL ...] [--verbose] --domain DOMAIN --problem PROBLEM --downward DOWNWARD --search SEARCH [-t TIMEOUT] [-m MEM]
                             [--fdmem FDMEM]

Driver for debugging remote ASNet policies

options:
  -h, --help            show this help message and exit
  --asnet ASNET         Path to the executable starting the ASNet server (default: None)
  --model MODEL [MODEL ...]
                        Paths to the policy model files (default: None)
  --verbose, -v         More verbose output. (default: False)
  --domain DOMAIN       Path to the PDDL domain file, required if no sas file is provided (default: None)
  --problem PROBLEM     Path to the PDDL problem file, required if no sas file is provided (default: None)
  --downward DOWNWARD   Path to the downward executable (not the FD driver script) (default: None)
  --search SEARCH       Search configuration of FD (default: None)
  -t TIMEOUT, --timeout TIMEOUT
                        Time limit for the driver in seconds (default: None)
  -m MEM, --mem MEM     Memory limit for the driver in MiB (default: None)
  --fdmem FDMEM         Set maximal memory limit for FD process in MiB (default: None)
```

Note that the ASNet policy server can serve mutiple policy models at a time.

Our GNN policy server can only be invoked with a single policy model.

## Multi Policy Search

This section contains documentation about Multi Policy Search.
The concrete configuration options used for runs in the paper are included below.

Uses multiple different (ASNet) Policies during search.
The default configuration simply runs the different policies available and selects the best result.
Tree search starts at the initial state and then runs each policy until a certain depth.
Then a heuristic estimates the cost-to-goal for each of the reached states and tree search continues from the most promising state.

Performance did not seem to improve over the naive approach with tree search in the current implementation.

### Configuration Options

- ```tree_search``` (bool)
- ```along_path``` (bool)
- ```fault_detection``` (bool)
- ```steps_per_cycle``` (int)
- ```number_of_policies``` (int)
- ```prefer_solved``` (bool)
- ```heuristic``` (Heuristic)
- ```remote_policy``` (Policy)

### Tree Search

**Default**: false

Tree search starts at the initial state and then runs each policy consecutively until a certain depth (see ``steps_per_cycle``).
Then a heuristic estimates the cost-to-goal for each of the reached states and tree search continues from the most promising state.

While called tree search here, only the best state is selected and, in theory, runs could produce states that were previously visited before (i.e. more like a graph?).

### Along Path

**Default**: false

Runs (currently 3) policies along each path state of the plan (fragment) returned from search.
If the goal was not reached, this can help find the goal by using different policies on the first policy's path and hoping for them to diverge at some point.
If the goal was reached, a better sub-plan might be found.
The subplan is then stiched onto the original plan, starting where the policy started executing.

### Fault Detection

**Default**: false

Currently not implemented.

The idea is to run the main policy until a goal is reached or the policy loops.
Then, a heuristic is used to examine the path for seemingly suboptimal behavior.
This could e.g. take the form of the heuristic value increasing for a few steps, or stagnating for a prolonged period of time.
This would then be taken as a fragment where running other policies could improve performance.

### Steps per Cycle

**Default**: 10

How many steps the policies should be run in tree search between heuristic decisions.

### Number of Policies

**Default**: 5

Number of policies to be used in search, both for "naive" multi-policy search and tree search.

### Prefer Solved

**Default**: false

Stops the algorithm early if a goal is reached.
This prevents potential cheaper plans to be found later on, but improves runtime/termination.

### Heuristic

**Default**: None

The heuristic to be used in the multi-policy algorithms.
Currently only used for tree search, where the leaf for the next (step-limited) run is chosen according to this heuristic.

### Remote Policy

**Default**: None

Currently configured to only accept RemotePolicy, but could be adapted to accept any type of policy or an array thereof.

### MPS configurations used in paper

Each multi-policy search $\text{M}_n$ corresponds to the fast downward call:

```C++
mult_policy(num_policies=n)
for n in {1..5}
```

## Policy Comparison Oracle

This section contains documentation about Policy Comparison Oracles (PCOs).
The concrete configuration options used for runs in the paper are included below.

PCOs use multiple secondary policies to find bugs in a primary policy.

### Configuration

- ```qual_oracle``` (Oracle)
- ```maintain_upper_bounds``` (bool)
- ```majority_vote``` (bool)
- ```num_offset_runs``` (int)
- ```amount_offset``` (int)
- ```num_per_state``` (int)
- ```choose_policies``` (enum)
- ```ignore_quality_bugs``` (bool)
- ```num_per_path_state``` (int)
- ```run_prob``` (double)
- ```parent_propagation``` (bool)
- ```register_unsolved``` (bool)

### PCO configurations used in paper

The exact oracle configuration passed to fast downward through the ``pool_policy_tester`` search configuration.

- PCOP (Plain PCO):

    ```C++
    policy_comparison_oracle(
        num_per_state=5,
        choose_policies="online_pq",
        maintain_upper_bounds=false
    )
    ```

- PCOE (Extended PCO):

    ```C++
    policy_comparison_oracle(
        num_per_state=5,
        choose_policies="online_pq",
        maintain_upper_bounds=true,
        num_per_path_state=1,
        run_prob=0.3
    )
    ```

- CO (Combined Oracle):

    ```C++
    composite_oracle(
        qual_oracle={ehc_config},
        quant_oracle={aras_config},
        metamorphic_oracle={ebmo_pcto_integration_prop_config}
    )

    ehc_config = planner_oracle(
        oracle=internal_planner(conf=ehc_ff, max_planner_time=60)
    )

    aras_config = aras(
        aras_dir="{aras_dir}",
        aras_max_time_limit=60
    )

    ebmo_pcto_integration_prop_config = bound_maintenance_pcto_oracle(
        lookahead_heuristic=ff(),
        consider_intermediate_states=true,
        max_lookahead_state_visits=100,
        update_parents=true,
        pcto_oracle={pcto_5_online_pq_config}
    )

    pcto_5_online_pq_config = policy_comparison_oracle(
        num_per_state=5,
        choose_policies="online_pq",
        maintain_upper_bounds=true,
        num_per_path_state=1,
        run_prob=0.3,
        ignore_quality_bugs=false
    )
    ```

### Qual Oracle

**Default**: None

If specified, this oracle will be used for quality bugs.
That is, it fully substitutes the policy comparison approach.
Can be useful as policy comparison is relatively slow compared to e.g. EHC.

### Maintain Upper Bounds

**Default**: true

If enabled, upper bounds are maintained along all policy execution paths initiated by the oracle.
Furthermore, in the current implementation, the Upper Bounds class can be passed to a modified version of the Bound Maintenance Oracle (BMO), which then also inserts its upper bounds into the same space.
This enables bound sharing and respective synergies.

### Majority Vote

**Default**: false

If enabled, multiple policies are executed and a majority vote is cast.
If multiple options are equally chosen, the choice is not further specified.

Does work with upper bounds enabled, does **not** work with online policy selection (as policy performance cannot be evaluated seperately in this case).

### Num Offset Runs

**Default**: 0

Number of additional runs that are offset by ```amount_offset``` from the pool state.
Offset runs are **only** started from the **pool state**, i.e. never from intermediate path states, even when ```num_offset_runs``` and ```num_per_path_state``` are both larger than 0.

### Amount Offset

**Default**: 1

Length of every random walk when ```num_offset_runs``` is larger than zero.
Currently no option for "up to length".

### Num Per State

**Default**: None

Number of portfolio policies run on the pool state.
Set to value ``-1`` to run all available policies.
No default value defined to make this decision conscious.

### Choose Policies

**Default**: "Normal"

Options are ``normal``, ``random``, ``online_sample``, ``online_pq``.

- ``normal``: Execute policies in-order, as given to fast downward.
- ``random``: Randomly sample from all available policies.
- ``online_sample``: Maintain ranking of best performing portfolio policies, take from best ones with 50% chance and sample randomly with 50% chance.
- ``online_pq``: Maintain ranking of best performing portfolio policies, run only best ones.

Both ``online_sample`` and ``online_pq`` rank previous policy performance by $R_{\pi} = \pi_{bugs}/\pi_{runs}$, i.e. the ratio between number of bugs found by portfolio policy $\pi$ and number of $\pi's$ total policy runs

### Ignore Quality Bugs

**Default**: false

If the policy under test does not reach the goal, refrain from finding a path to the goal through the portfolio policies, i.e. do not process qualitative bug candidates.
Might be useful to speed up execution on a pool of states, if qualitative bugs are not of interest.

### Num Per Path State

**Default**: 0

Number of portfolio policies run per state on the primary policy's path.
Portfolio policies will be chosen according to the ``choose_policy`` option.

### Run Prob

**Default**: 1.0

Probability of running any policy on any particular state of the primary policy's path.
Only relevant if ``num_per_path_state`` is large than 0.
For every path state it is first decided wether any policies are run (according to ``run_prob``), if yes then all ``num_per_path_state`` policies are run, without exception.

### Parent Propagation

**Default**: true

Whether improved bounds are propagated to their parents through the cached policy paths in the upper bounds handling.
Only relevant if ``maintain_upper_bounds`` is enabled.

### Register Unsolved

**Default**: false (should be changed in the future)

Whether policy runs that are conducted through the upper bounds framework should be registered for later bound propagation, even if they do not reach a goal.

This affects two things:
First, whether the path is registered.
Improved upper bounds can be propagated backwards through these paths (also up to the pool states, finding bugs).

Second, whether that path is processed once to spread the derivable upper bounds.
It will not only be registered, but also be processed backwards, trying to propagate bounds through that path.
As the policy did not reach a goal, this will initially be UNSOLVED.
If a state is crossed where the upper bound is less than UNSOLVED, that bound will be used and further propagated.

