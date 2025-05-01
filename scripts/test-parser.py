#! /usr/bin/env python
import math
import os

from lab.parser import Parser
import re

# any bug reports after TIME_LIMIT will be ignored (includes stored time to compute a simulation)
# can be below the time limit that was actually given to the tool
# in case this coincides you may use the attribute "time_limit" stored in the "static-properties" file instead
TIME_LIMIT = 7 * 24 * 60 * 60

# include data on when each bug was reported, necessary e.g. for number of bugs over time plots
# including this will significantly increase the size of the resulting properties file
INCLUDE_OVER_TIME_DATA = False


def add_patterns():
    parser.add_pattern("node", r"node: (.+)\n", type=str, file="driver.log", required=True)
    parser.add_pattern("exit_code", r"exit code: (.+)\n", type=int, file="driver.log")
    parser.add_pattern("time_limit", r'"time_limit": (.+)\n', type=int, file="static-properties")
    parser.add_pattern("search_time", r"Actual search time: (.+)s\n", type=float)
    parser.add_pattern("testing_time", r"Testing time: (.+)s\n", type=float)
    parser.add_pattern("total_time", r"Total time: (.+)s\n", type=float)
    parser.add_pattern("stored_simulation_time", r"Computed numeric dominance function in (.+)s\n", type=float)
    parser.add_pattern("search_completed_msg", r"(Search stopped without finding a solution.)", type=str)
    parser.add_pattern("search_aborted_msg", r"(Time limit reached. Abort search.)", type=str)
    parser.add_pattern("out_of_mem_abort_msg", r"(Memory limit reached. Abort search.)", type=str)
    parser.add_pattern("abstention_msg", "(Abstaining from problem.)", type=str)
    # summary
    parser.add_pattern("num_tests", r"Conducted tests: (\d+)\n", type=int)
    parser.add_pattern("num_total_bugs", r"Bugs found: (\d+)\n", type=int)
    parser.add_pattern("num_total_qual_bugs", r"Unsolved state bugs: (\d+)\n", type=int)
    parser.add_pattern("num_policy_solved_states", r"States solved by policy: (\d+)\n", type=int)
    # regions
    # parser.add_pattern("num_regions", r"Number of regions: (\d+)\n", type=int)
    # parser.add_pattern("num_bug_regions", r"Number of bug regions: (\d+)\n", type=int)
    # fuzzer
    parser.add_pattern("fuzzing_time", r"Fuzzing time: (.+)s\n", type=float)
    parser.add_pattern("num_fuzzing_steps", r"Fuzzing steps: (\d+)\n", type=int)
    parser.add_pattern("num_fuzzing_duplicate_states", r"Duplicate states: (\d+)\n", type=int)
    parser.add_pattern("num_fuzzing_intermediate_states", r"Intermediate states added during random walks: (\d+)\n",
                       type=int)
    parser.add_pattern("num_fuzzing_filtered_states", r"States filtered out: (\d+)\n", type=int)
    parser.add_pattern("num_fuzzing_dead_ends", r"Identified dead ends: (\d+)\n", type=int)
    parser.add_pattern("num_fuzzing_failed_attempts", r"Failed attempts: (\d+)\n", type=int)
    # novelty
    parser.add_pattern("num_unique_1_fact_sets", r"Unique 1-fact-sets: (\d+)\n", type=int)
    parser.add_pattern("num_unique_2_fact_sets", r"Unique 2-fact-sets: (\d+)\n", type=int)
    # pool
    parser.add_pattern("pool_size", r"Pool size: (\d+)\n", type=int)
    parser.add_pattern("load_pool_size", r"... loaded (\d+) entries\n", type=int)
    parser.add_pattern("max_pool_size", r"Max pool size: (\d+)\n", type=int)
    parser.add_pattern("num_pool_bugs", r"Pool bug states: (\d+)\n", type=int)
    parser.add_pattern("num_non_pool_bugs", r"Non-pool bug states: (\d+)\n", type=int)
    parser.add_pattern("num_qual_pool_bugs", r"Qualitative pool bug states: (\d+)\n", type=int)
    parser.add_pattern("num_quant_pool_bugs", r"Non-qualitative pool bug states: (\d+)\n", type=int)
    parser.add_pattern("num_unconfirmed_pool_states", r"Pool unconfirmed states: (\d+)\n", type=int)
    parser.add_pattern("num_solved_pool_states", r"Solved pool states: (\d+)\n", type=int)
    # misc
    parser.add_pattern("numldsim_computed_msg", r"(Numeric LDSim computed.)", type=str)
    parser.add_pattern("engine_init_time", r"Testing engine initialized \[t=(.+)s\]\n", type=float)
    parser.add_pattern("out_of_mem_server_msg", r"(DefaultCPUAllocator: can't allocate memory)", type=str)
    parser.add_pattern("python_out_of_mem_msg", r"(MemoryError:)", type=str)


def count_over_time(time_points):
    x = [0]
    y = [0]
    for time_point in sorted(list(time_points)):
        if time_point > x[-1]:
            x.append(time_point)
            y.append(y[-1] + 1)
        else:
            assert (time_point == x[-1])
            y[-1] += 1
    return [x, y]


def parse_bug_reports(content, props):
    # if "stored_simulation_time" in props:
    #    cutoff_time = TIME_LIMIT - props["stored_simulation_time"]
    # else:
    #    cutoff_time = TIME_LIMIT
    cutoff_time = TIME_LIMIT

    if props["search_completed"] and props["total_time"] > cutoff_time:
        del props["total_time"]
        del props["testing_time"]
        del props["search_time"]
        props["error"] = "search_out_of_time"
        props["search_completed"] = 0

    # read bug reports
    qual_bug_reports_tmp = re.findall(r"^(?:\(Updated\) )?Result for StateID=#(\d+)(?: \[TestNumber=\d+\])?:"
                                      r" qualitative bug found \[t=(.+)s\]$", content, re.M)
    qual_bug_reports = [(int(b), float(t)) for b, t in qual_bug_reports_tmp if float(t) < cutoff_time]
    quant_bug_reports_tmp = re.findall(r"^(?:\(Updated\) )?Result for StateID=#(\d+)(?: \[TestNumber=\d+\])?:"
                                       r" quantitative bug found with value=(\d+) \[t=(.+)s\]$", content, re.M)
    quant_bug_reports = [(int(b), int(v), float(t)) for b, v, t in quant_bug_reports_tmp if float(t) < cutoff_time]
    unclassified_bug_reports_tmp = re.findall(
        r"^(?:\(Updated\) )?Result for StateID=#(\d+)(?: \[TestNumber=\d+\])?:"
        r" unclassified bug found with value=(\d+) \[t=(.+)s\]$", content, re.M)
    unclassified_bug_reports = [(int(b), int(v), float(t)) for b, v, t in unclassified_bug_reports_tmp if
                                float(t) < cutoff_time]
    if INCLUDE_OVER_TIME_DATA:
        props["qual_bug_reports"] = qual_bug_reports
        props["quant_bug_reports"] = quant_bug_reports
        props["unclassified_bug_reports"] = unclassified_bug_reports
    all_bugs_to_time = {}
    qual_bugs_to_time = {}
    quant_bugs_to_time = {}
    unclassified_bugs_to_time = {}
    bugs_to_bug_values = {}
    for b, t in qual_bug_reports:
        all_bugs_to_time[b] = min(t, all_bugs_to_time.get(b)) if (b in all_bugs_to_time) else t
        qual_bugs_to_time[b] = min(t, qual_bugs_to_time.get(b)) if (b in qual_bugs_to_time) else t
        bugs_to_bug_values[b] = math.inf
    for b, v, t in quant_bug_reports:
        all_bugs_to_time[b] = min(t, all_bugs_to_time.get(b)) if (b in all_bugs_to_time) else t
        quant_bugs_to_time[b] = min(t, quant_bugs_to_time.get(b)) if (b in quant_bugs_to_time) else t
        bugs_to_bug_values[b] = max(v, bugs_to_bug_values.get(b)) if (b in bugs_to_bug_values) else v
    for b, v, t in unclassified_bug_reports:
        all_bugs_to_time[b] = min(t, all_bugs_to_time.get(b)) if (b in all_bugs_to_time) else t
        bugs_to_bug_values[b] = max(v, bugs_to_bug_values.get(b)) if (b in bugs_to_bug_values) else v
        # make sure a bug is only counted in unclassified category if it is not in qual or quant categories
        if b not in qual_bugs_to_time and b not in quant_bugs_to_time:
            unclassified_bugs_to_time[b] = min(t, unclassified_bugs_to_time.get(b)) if (
                    b in unclassified_bugs_to_time) else t
    props["num_total_bugs"] = len(all_bugs_to_time)
    props["num_total_qual_bugs"] = len(qual_bugs_to_time)
    props["num_total_quant_bugs"] = len(quant_bugs_to_time)
    props["num_total_unclassified_bugs"] = len(unclassified_bugs_to_time)
    assert props["num_total_bugs"] == props["num_total_qual_bugs"] + props["num_total_quant_bugs"] + props[
        "num_total_unclassified_bugs"]
    if INCLUDE_OVER_TIME_DATA:
        props["num_bugs_over_time"] = count_over_time(all_bugs_to_time.values())
        props["num_qual_bugs_over_time"] = count_over_time(qual_bugs_to_time.values())
        props["num_quant_bugs_over_time"] = count_over_time(quant_bugs_to_time.values())
        props["num_unclassified_bugs_over_time"] = count_over_time(unclassified_bugs_to_time.values())

    # determine submitted pool states (submitted from pool to oracle also if test is not finished)
    run_policy_messages = re.findall(r"^Policy on StateID=#(\d+) (?:.*)\[t=(.+)s\]$", content, re.M)
    submitted_pool_states = []
    for state, t in run_policy_messages:
        if float(t) < cutoff_time:
            submitted_pool_states.append(int(state))
    submitted_pool_states = sorted(list(set(submitted_pool_states)))
    unsolved_pool_state_messages = re.findall(
        r"^Policy on StateID=#(\d+)(?: \[TestNumber=\d+\])?:  not solved(?:.*)\[t=(.+)s\]$", content, re.M)
    solved_pool_state_messages = re.findall(
        r"^Policy on StateID=#(\d+)(?: \[TestNumber=\d+\])?:  policy_cost=(\d+) \[t=(.+)s\]$", content, re.M)
    unclassified_pool_state_messages = re.findall(
        r"^Policy on StateID=#(\d+)(?: \[TestNumber=\d+\])?:  aborted.*\[t=(.+)s\]$", content, re.M)
    # policy_cost_map maps state to policy cost value (-1 if state is known not solved by pi)
    # contains no entry if value is unknown (e.g., because evaluation was aborted)
    policy_cost_map = {int(state): int(policy_cost) for state, policy_cost, _ in solved_pool_state_messages}
    for state, _ in unsolved_pool_state_messages:
        policy_cost_map[int(state)] = -1
    if 0 in policy_cost_map:
        cost_value = policy_cost_map[0]
        props["first_state_pi_cost"] = "unsolved" if cost_value == -1 else str(cost_value)
    else:
        props["first_state_pi_cost"] = "unknown"
    props["first_state_known_solved"] = int(
        props["first_state_pi_cost"] != "unsolved" and props["first_state_pi_cost"] != "unknown")
    props["first_state_known_unsolved"] = int(props["first_state_pi_cost"] == "unsolved")
    props["first_state_unknown_if_solved"] = int(props["first_state_pi_cost"] == "unknown")
    submitted_pool_states_unsolved = []
    submitted_pool_states_solved = []
    submitted_pool_states_unknown = []
    for state, t in unsolved_pool_state_messages:
        if float(t) < cutoff_time:
            submitted_pool_states_unsolved.append(int(state))
    for state, t, policy_cost in solved_pool_state_messages:
        if float(t) < cutoff_time:
            submitted_pool_states_solved.append(int(state))
    for state, t in unclassified_pool_state_messages:
        if float(t) < cutoff_time:
            if int(state) in qual_bugs_to_time:
                submitted_pool_states_unsolved.append(int(state))
            elif int(state) in quant_bugs_to_time:
                submitted_pool_states_solved.append(int(state))
            else:
                submitted_pool_states_unknown.append(int(state))
    submitted_pool_states_unsolved = sorted(list(set(submitted_pool_states_unsolved)))
    submitted_pool_states_solved = sorted(list(set(submitted_pool_states_solved)))
    submitted_pool_states_unknown = sorted(list(set(submitted_pool_states_unknown)))
    assert len(submitted_pool_states) == len(submitted_pool_states_unsolved) + len(submitted_pool_states_solved) + len(
        submitted_pool_states_unknown)

    # determine tested states
    test_result_messages = re.findall(r"^Result for StateID=#(\d+) \[TestNumber=.*\[t=(.+)s\]$", content, re.M)
    tested_pool_states = []
    for state, t in test_result_messages:
        if float(t) < cutoff_time:
            tested_pool_states.append(int(state))
    tested_pool_states = sorted(list(set(tested_pool_states)))
    props["tested_pool_states"] = tested_pool_states
    props["num_tests"] = len(tested_pool_states)
    tested_solved_pool_states = []
    tested_unsolved_pool_states = []
    tested_unknown_pool_states = []
    for state in tested_pool_states:
        assert state in submitted_pool_states
        if state in submitted_pool_states_solved:
            tested_solved_pool_states.append(state)
        elif state in submitted_pool_states_unsolved:
            tested_unsolved_pool_states.append(state)
        else:
            assert state in submitted_pool_states_unknown
            tested_unknown_pool_states.append(state)
    props["tested_pool_states_solved"] = tested_solved_pool_states
    props["num_tested_pool_states_solved"] = len(tested_solved_pool_states)
    props["tested_pool_states_unsolved"] = tested_unsolved_pool_states
    props["num_tested_pool_states_unsolved"] = len(tested_unsolved_pool_states)
    props["tested_pool_states_unknown"] = tested_unknown_pool_states
    props["num_tested_pool_states_unknown"] = len(tested_unknown_pool_states)

    # determine pool bugs
    all_pool_bugs_to_time = {b: t for b, t in all_bugs_to_time.items() if b in tested_pool_states}
    pool_qual_bugs_to_time = {b: t for b, t in qual_bugs_to_time.items() if b in tested_pool_states}
    pool_quant_bugs_to_time = {b: t for b, t in quant_bugs_to_time.items() if b in tested_pool_states}
    pool_unclassified_bugs_to_time = {b: t for b, t in unclassified_bugs_to_time.items() if b in tested_pool_states}
    num_pool_bugs_over_time = count_over_time(all_pool_bugs_to_time.values())
    num_qual_pool_bugs_over_time = count_over_time(pool_qual_bugs_to_time.values())
    num_quant_pool_bugs_over_time = count_over_time(pool_quant_bugs_to_time.values())
    num_unclassified_pool_bugs_over_time = count_over_time(pool_unclassified_bugs_to_time.values())

    if INCLUDE_OVER_TIME_DATA:
        props["num_pool_bugs_over_time"] = num_pool_bugs_over_time
        props["num_qual_pool_bugs_over_time"] = num_qual_pool_bugs_over_time
        props["num_quant_pool_bugs_over_time"] = num_quant_pool_bugs_over_time
        props["num_unclassified_pool_bugs_over_time"] = num_unclassified_pool_bugs_over_time

    props["num_pool_bugs"] = num_pool_bugs_over_time[1][-1]
    test_bugs = sorted(list(all_pool_bugs_to_time.keys()))
    props["test_bugs"] = test_bugs
    assert props["num_pool_bugs"] == len(props["test_bugs"])
    props["num_non_pool_bugs"] = props["num_total_bugs"] - props["num_pool_bugs"]
    props["num_qual_pool_bugs"] = num_qual_pool_bugs_over_time[1][-1]
    props["qual_test_bugs"] = sorted(list(pool_qual_bugs_to_time.keys()))
    assert props["num_qual_pool_bugs"] == len(props["qual_test_bugs"])
    props["num_quant_pool_bugs"] = num_quant_pool_bugs_over_time[1][-1]
    props["quant_test_bugs"] = sorted(list(pool_quant_bugs_to_time.keys()))
    assert props["num_quant_pool_bugs"] == len(props["quant_test_bugs"])
    props["num_unclassified_pool_bugs"] = num_unclassified_pool_bugs_over_time[1][-1]
    props["unclassified_test_bugs"] = sorted(list(pool_unclassified_bugs_to_time.keys()))
    assert props["num_unclassified_pool_bugs"] == len(props["unclassified_test_bugs"])

    first_state_is_bug = int(0 in test_bugs)
    props["first_state_is_bug"] = int(0 in test_bugs)
    props["max_first_state_finite_bug_value"] = 0
    first_state_bug_value = bugs_to_bug_values[0] if first_state_is_bug else None
    if first_state_is_bug:
        if first_state_bug_value < math.inf:
            props["max_first_state_finite_bug_value"] = first_state_bug_value

    # bug values
    test_bugs_below_5 = set()
    test_bugs_between_5_and_10 = set()
    test_bugs_between_10_and_20 = set()
    test_bugs_between_20_and_50 = set()
    test_bugs_between_50_and_100 = set()
    test_bugs_over_100_but_finite = set()
    total_finite_test_bug_value = 0
    max_finite_test_bug_value = 0
    # relative bug value: bug value / policy cost for solved states
    relative_bug_value_in_percent_sum = 0  # use to compute avg
    relative_bug_value_ctr = 0
    max_relative_bug_value_in_percent = 0
    test_bugs_below_5_percent = set()
    test_bugs_between_5_and_10_percent = set()
    test_bugs_between_10_and_20_percent = set()
    test_bugs_between_20_and_50_percent = set()
    test_bugs_between_50_and_100_percent = set()
    for b in test_bugs:
        assert b in bugs_to_bug_values
        bug_value = bugs_to_bug_values[b]
        assert bug_value > 0
        if bug_value < math.inf:
            total_finite_test_bug_value += bug_value
            max_finite_test_bug_value = max(max_finite_test_bug_value, bug_value)
        if bug_value < 5:
            test_bugs_below_5.add(b)
        elif bug_value < 10:
            test_bugs_between_5_and_10.add(b)
        elif bug_value < 20:
            test_bugs_between_10_and_20.add(b)
        elif bug_value < 50:
            test_bugs_between_20_and_50.add(b)
        elif bug_value < 100:
            test_bugs_between_50_and_100.add(b)
        elif bug_value < math.inf:
            test_bugs_over_100_but_finite.add(b)
        # handle relative bug values
        if bug_value == math.inf or b not in policy_cost_map:
            continue
        policy_cost = policy_cost_map[b]
        assert policy_cost > 0
        relative_bug_value_in_percent = (bug_value / policy_cost) * 100
        relative_bug_value_in_percent_sum += relative_bug_value_in_percent
        max_relative_bug_value_in_percent = max(max_relative_bug_value_in_percent, relative_bug_value_in_percent)
        relative_bug_value_ctr += 1
        if relative_bug_value_in_percent < 5:
            test_bugs_below_5_percent.add(b)
        elif relative_bug_value_in_percent < 10:
            test_bugs_between_5_and_10_percent.add(b)
        elif relative_bug_value_in_percent < 20:
            test_bugs_between_10_and_20_percent.add(b)
        elif relative_bug_value_in_percent < 50:
            test_bugs_between_20_and_50_percent.add(b)
        elif relative_bug_value_in_percent <= 100:
            test_bugs_between_50_and_100_percent.add(b)
    props["test_bugs_below_5"] = len(test_bugs_below_5)
    props["test_bugs_between_5_and_10"] = len(test_bugs_between_5_and_10)
    props["test_bugs_between_10_and_20"] = len(test_bugs_between_10_and_20)
    props["test_bugs_between_20_and_50"] = len(test_bugs_between_20_and_50)
    props["test_bugs_between_50_and_100"] = len(test_bugs_between_50_and_100)
    props["test_bugs_over_100_but_finite"] = len(test_bugs_over_100_but_finite)
    props["total_finite_test_bug_value"] = total_finite_test_bug_value
    props["max_finite_test_bug_value"] = max_finite_test_bug_value
    props["bugs_below_5_percent"] = len(test_bugs_below_5_percent)
    props["bugs_between_5_and_10_percent"] = len(test_bugs_between_5_and_10_percent)
    props["bugs_between_10_and_20_percent"] = len(test_bugs_between_10_and_20_percent)
    props["bugs_between_20_and_50_percent"] = len(test_bugs_between_20_and_50_percent)
    props["bugs_between_50_and_100_percent"] = len(test_bugs_between_50_and_100_percent)
    if relative_bug_value_ctr:
        props["avg_relative_bug_value_in_percent"] = relative_bug_value_in_percent_sum / relative_bug_value_ctr
    props["max_relative_bug_value_in_percent"] = max_relative_bug_value_in_percent

    if first_state_is_bug:
        assert 0 in bugs_to_bug_values
        bug_value = bugs_to_bug_values[0]
        assert bug_value > 0
        if bug_value == math.inf:
            props["first_state_qualitative_bug"] = 1
        else:
            props["first_state_qualitative_bug"] = 0
            props["first_state_bugs_below_5"] = int(bug_value < 5)
            props["first_state_bugs_between_5_and_10"] = int(5 <= bug_value < 10)
            props["first_state_bugs_between_10_and_20"] = int(10 <= bug_value < 20)
            props["first_state_bugs_between_20_and_50"] = int(20 <= bug_value < 50)
            props["first_state_bugs_between_50_and_100"] = int(50 <= bug_value < 100)
            props["first_state_bugs_over_100_but_finite"] = int(bug_value >= 100)
    else:
        props["first_state_bugs_below_5"] = 0
        props["first_state_bugs_between_5_and_10"] = 0
        props["first_state_bugs_between_10_and_20"] = 0
        props["first_state_bugs_between_20_and_50"] = 0
        props["first_state_bugs_between_50_and_100"] = 0
        props["first_state_bugs_over_100_but_finite"] = 0
        props["first_state_qualitative_bug"] = 0
    if (0 in policy_cost_map and policy_cost_map[0] > 0) and first_state_is_bug:
        first_state_relative_bug_value_in_percent = (first_state_bug_value / policy_cost_map[0]) * 100
        props["first_state_bugs_below_5_percent"] = int(first_state_relative_bug_value_in_percent < 5)
        props["first_state_bugs_between_5_and_10_percent"] = int(5 <= first_state_relative_bug_value_in_percent < 10)
        props["first_state_bugs_between_10_and_20_percent"] = int(10 <= first_state_relative_bug_value_in_percent < 20)
        props["first_state_bugs_between_20_and_50_percent"] = int(20 <= first_state_relative_bug_value_in_percent < 50)
        props["first_state_bugs_between_50_and_100_percent"] = int(
            50 <= first_state_relative_bug_value_in_percent < 100)
        props["first_state_bugs_over_100_percent_but_finite"] = int(first_state_relative_bug_value_in_percent >= 100)
    else:
        props["first_state_bugs_below_5_percent"] = 0
        props["first_state_bugs_between_5_and_10_percent"] = 0
        props["first_state_bugs_between_10_and_20_percent"] = 0
        props["first_state_bugs_between_20_and_50_percent"] = 0
        props["first_state_bugs_between_50_and_100_percent"] = 0
        props["first_state_bugs_over_100_percent_but_finite"] = 0

    # compute ratios
    if ("pool_size" not in props) and "load_pool_size" in props:
        props["pool_size"] = props["load_pool_size"]
    if props["num_tests"] > 0:
        props["bugs_per_test"] = props["num_pool_bugs"] / props["num_tests"]
    if props["num_tested_pool_states_solved"] > 0:
        props["bugs_per_test_quant"] = props["num_quant_pool_bugs"] / props["num_tested_pool_states_solved"]
    if props["num_tested_pool_states_unsolved"] > 0:
        props["bugs_per_test_qual"] = props["num_qual_pool_bugs"] / props["num_tested_pool_states_unsolved"]
    if props["num_tested_pool_states_unknown"] > 0:
        props["bugs_per_test_unclassified"] = props["num_unclassified_pool_bugs"] / props[
            "num_tested_pool_states_unknown"]


def set_derived_flags(content, props):
    memory_reports = re.findall(r"^Peak memory: (.+) KB$", content, re.M)
    max_memory_kb = 0
    for memory_report in memory_reports:
        max_memory_kb = max(max_memory_kb, float(memory_report))
    if max_memory_kb:
        props["memory_usage_mb"] = max_memory_kb / 1024
    props["qldsim_computed"] = int("numldsim_computed_msg" in props)
    # determine error
    if props["exit_code"] == 2:
        props["error"] = "connection_error"
    elif "out_of_mem_server_msg" in props or "python_out_of_mem_msg" in props:
        props["error"] = "server_out_of_memory"
    elif props["exit_code"] == 3:
        props["error"] = "driver_error"
        props.add_unexplained_error(f"Driver error.")
    elif props["exit_code"] == 4:
        props["error"] = "driver_timeout"
    elif props["exit_code"] == -11:
        props["error"] = "segmentation_fault"
        props.add_unexplained_error("Segmentation fault!")
    elif props["exit_code"] == -9 or props["exit_code"] == 247:
        props["error"] = "killed"
    elif props["exit_code"] == 22 or "out_of_mem_abort_msg" in props:
        props["error"] = "search_out_of_memory"
    elif props["exit_code"] == 23:
        props["error"] = "search_out_of_time"
    elif props["exit_code"] == 35:
        props["error"] = "remote_policy_error"
    elif props["exit_code"] == -24 or props["exit_code"] == 232:
        props["error"] = "time_out"
    elif "search_completed_msg" in props and props["exit_code"] == 12:
        props["error"] = "none"
    else:
        props["error"] = "unclassified_error"
        props.add_unexplained_error(f"Unclassified error! No known category. Exit code {props['exit_code']}.")
    props["search_completed"] = int("search_completed_msg" in props and props["error"] == "none" and props["num_tests"] == props["pool_size"])


def filter_run_err(content, props):
    if props["error"] == "server_out_of_memory" or props["error"] == "remote_policy_error":
        if os.path.exists("run.err"):
            with open("run.err") as f:
                content = f.read()
            if (
                    content == "Error: Cannot get response for GetFDRStateOperator :: Unexpected error in RPC handling\nphrmPolicyFDRStateOperator failed\nRemote policy error"
                    or content == "Error: Cannot get response for GetFDRStateOperator :: Unexpected error in RPC handling\nphrmPolicyFDRStateOperator failed"):
                open("run.err", "w").close()


if __name__ == "__main__":
    parser = Parser()
    add_patterns()
    parser.add_function(set_derived_flags)
    parser.add_function(parse_bug_reports)
    parser.add_function(filter_run_err)
    parser.parse()
    files_to_remove = [
        "aras_output.sas",
        "aras_sas_plan_input",
        "elapsed.time",
        "output",
        "plan_numbers_and_cost"
    ]
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
