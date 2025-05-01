#! /usr/bin/env python
import os.path
import glob
import sys

from lab.reports import Attribute
from downward.reports.absolute import AbsoluteReport
from lab.experiment import Experiment
from lab.environments import LocalEnvironment

policy_directory = os.getcwd()
testing_directory = os.path.dirname(policy_directory)
bughive_path = os.path.abspath(os.path.realpath(os.path.join(testing_directory, "bughive")))
parser_path = os.path.join(bughive_path, "scripts", "test-parser.py")
driver_path = os.path.join(bughive_path, "test_drivers", "asnets_test_driver.py")
fd_path = os.path.join(bughive_path, "fd-action-policy-testing", "builds", "release", "bin", "downward")
policy_driver = os.path.join(bughive_path, "policy-servers", "asnets")
time_limit = 2 * 60
memory_limit = 4096 - 10

basic_int_attributes = [
    Attribute("search_completed", absolute=True, min_wins=False),
    Attribute("pool_size", min_wins=False),
    Attribute("num_tests", min_wins=False),
    Attribute("num_tested_pool_states_solved", min_wins=False),
    Attribute("num_tested_pool_states_unsolved", min_wins=False),
    Attribute("num_tested_pool_states_unknown", min_wins=False),
    Attribute("num_pool_bugs", min_wins=False),
    Attribute("num_qual_pool_bugs", min_wins=False),
    Attribute("num_quant_pool_bugs", min_wins=False),
    Attribute("first_state_known_solved", min_wins=False),
    Attribute("first_state_known_unsolved", min_wins=False),
    Attribute("first_state_is_bug", min_wins=False),
    Attribute("first_state_qualitative_bug", min_wins=False),
]


def write_results():
    try:
        import simplejson as json
        assert json  # Silence pyflakes
    except ImportError:
        import json
    import toml
    properties_file = os.path.join(policy_directory, "data", "condor-test-eval", "properties")
    assert os.path.exists(properties_file)
    props = dict()
    try:
        with open(properties_file, 'r') as f:
            props.update(json.load(f))
    except IOError as e:
        print(str(type(e)) + " error " + str(e), file=sys.stderr)
        exit(1)
    attribute_data = {attribute: list() for attribute in basic_int_attributes}
    num_runs = len(props)
    num_ignored_runs = 0
    for run_name, run in props.items():
        if run["error"] != "none":
            error_str = run["error"]
            print(f'Warning for {run_name}: error string is "{error_str}"')
            if run["error"] in ["driver_error", "segmentation_fault", "killed", "unclassified_error"]:
                exit(1)
        if "abstention_msg" in run:
            num_ignored_runs += 1
            print(f"Ignoring run {run_name}, testing engine abstained.")
            continue
        if int(run["num_tests"]) < 1:
            print(f"Warning for {run_name}: no tested states even though tester did not abstain.")
            num_ignored_runs += 1
            continue
        for attribute in basic_int_attributes:
            if attribute not in run:
                print(f"Fatal error in {run_name}: no attribute {attribute} in properties file", file=sys.stderr)
                sys.exit(1)
            attribute_data[attribute].append(run[attribute])
    aggregate_values = dict()
    aggregate_values["num_instances"] = num_runs
    if num_ignored_runs == num_runs:
        # default values for everything
        aggregate_values["search_completed"] = 0
        aggregate_values["pool_size"] = 0
        aggregate_values["num_tests"] = 0
        aggregate_values["num_tested_pool_states_solved"] = 0
        aggregate_values["num_tested_pool_states_unsolved"] = 0
        aggregate_values["num_tested_pool_states_unknown"] = 0
        aggregate_values["num_pool_bugs"] = 0
        aggregate_values["num_qual_pool_bugs"] = 0
        aggregate_values["num_quant_pool_bugs"] = 0
        aggregate_values["first_state_known_solved"] = 0
        aggregate_values["first_state_known_unsolved"] = 0
        aggregate_values["first_state_is_bug"] = 0
        aggregate_values["first_state_qualitative_bug"] = 0
    for attribute in basic_int_attributes:
        aggregate_values[attribute] = attribute.function(attribute_data[attribute])
    aggregate_values["testing_complete_all_instances"] = int(num_runs == (aggregate_values["search_completed"]))
    with open("results.toml", "w") as toml_file:
        toml.dump(aggregate_values, toml_file)


def get_domain_file():
    file = os.path.join(testing_directory, "domain.pddl")
    assert (os.path.exists(file))
    return file


def get_model_file():
    candidates = glob.glob(os.path.join(policy_directory, "*.policy"))
    assert (len(candidates) == 1)
    return candidates[0]


def get_domain_name(domain_directory):
    return os.path.basename(domain_directory)


def get_problem_files():
    pddl_files = sorted(glob.glob(os.path.join(testing_directory, "validate", "*.pddl")))
    assert pddl_files
    return pddl_files


def create_experiment(env):
    exp_ = Experiment(environment=env)
    exp_.add_resource("test_driver", driver_path, symlink=True)
    exp_.add_resource("fd", fd_path)
    exp_.add_resource("policy_driver", policy_driver)
    exp_.add_parser(parser_path)
    return exp_


def add_runs(exp_):
    domain_file = get_domain_file()
    policy_file = get_model_file()
    for problem_file in get_problem_files():
        problem_name = os.path.splitext(os.path.basename(problem_file))[0]
        run = exp_.add_run()
        run.add_resource("problem_file", problem_file, symlink=True)
        sim_file_path = f"{os.path.splitext(problem_file)[0]}.dfpmasqsim-10000-74"
        run.add_resource("sim_file", sim_file_path, symlink=True)
        pool_file_path = f"{os.path.splitext(problem_file)[0]}.pool50"
        use_pool = os.path.exists(pool_file_path)
        if use_pool:
            run.add_resource("pool_file", pool_file_path, symlink=True)
        run.add_resource("domain_file", domain_file, symlink=True)
        policy_name = "asnet"
        # ehc_config = (f"estimator_based_oracle(oracle="
        #               f"internal_planner_plan_cost_estimator(conf=ehc_ff, max_planner_time=300))")
        # aras_config = f'aras(aras_dir="{aras_dir}",aras_max_time_limit=30)'
        metamorphic_oracle_config = (f'iterative_improvement_oracle(conduct_lookahead_search=true,'
                                     f'lookahead_heuristic=ff(),consider_intermediate_states=true,'
                                     f'read_simulation=true, sim_file="{{sim_file}}")')
        # combined_oracle_config = (f'composite_oracle(qual_oracle={ehc_config},quant_oracle={aras_config},'
        #                          f'metamorphic_oracle={metamorphic_oracle_config})')
        oracle_config = metamorphic_oracle_config
        if use_pool:
            search_config = (f'pool_policy_tester(pool_file="{{pool_file}}", testing_method={oracle_config}, '
                             f'read_policy_cache=false, max_time={time_limit},'
                             f'abstain_if_first_state_not_known_solved=true)')
        else:
            max_pool_size = 50
            search_config = (f'pool_fuzzer(max_steps=100000, max_pool_size={max_pool_size}, eval=hmax(), '
                             f'max_walk_length=5, testing_method={oracle_config},max_time={time_limit},'
                             f'abstain_if_first_state_not_known_solved=true)')
        run.add_command("test_driver",
                        ["{test_driver}", "{policy_driver}",
                         "--model", policy_file, "--domain", "{domain_file}", "--problem", "{problem_file}",
                         "--downward", "{fd}", "--search", search_config, "--timeout", time_limit],
                        time_limit=time_limit + 3600, memory_limit=memory_limit,
                        soft_stdout_limit=20 * 1024, hard_stdout_limit=20 * 1024)
        run.set_property("domain", "domain")
        run.set_property("problem", problem_name)
        run.set_property("policy", policy_name)
        run.set_property("search_config", search_config)
        run.set_property("oracle", "combined")
        run.set_property("algorithm", "test-combined")
        run.set_property("time_limit", time_limit)
        run.set_property("memory_limit", memory_limit)
        run.set_property("id", [policy_name, problem_name])


exp = create_experiment(LocalEnvironment(processes=7))
add_runs(exp)
exp.add_step("build", exp.build)
exp.add_step("start", exp.start_runs)
exp.add_fetcher()
exp.add_step("write-results", write_results)


class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = ["time_limit", "memory_limit"]
    ERROR_ATTRIBUTES = [
        "domain",
        "problem",
        "algorithm",
        "error",
        "unexplained_errors",
        "node"
    ]


exp.add_report(BaseReport(attributes=["error", "exit_code"] + basic_int_attributes), outfile="test-report.html")
exp.run_steps()
