import subprocess
import re
import sys
import time
import resource


def add_common_args(parser):
    parser.add_argument("model", help="Path to the policy model file")
    parser.add_argument("domain", help="Path to the PDDL domain file")
    parser.add_argument("problem", help="Path to the PDDL problem file")
    parser.add_argument("downward", help="Path to the downward executable (not the FD driver script)")
    parser.add_argument("search", help="Search configuration of FD")
    parser.add_argument("-t", "--timeout", type=int, help="Time limit for the driver in seconds")
    parser.add_argument("-m", "--mem", type=int, help="Memory limit for the driver in MiB")


def run_driver(server_command, args):
    script_start = time.time()
    return_code = 3

    # get the available memory and leave margin for driver itself
    set_mem_limit = False
    if args.mem is not None:
        available_mem = args.mem * 1024 * 1024 - 10
        set_mem_limit = True
    else:
        current_rlimit = resource.getrlimit(resource.RLIMIT_AS)[0]
        if current_rlimit >= 0:
            available_mem = current_rlimit - 10
            set_mem_limit = True
    if set_mem_limit:
        if available_mem <= 2:
            print("Not enough memory provided. Server and FD not started.")
            sys.exit(5)
        internal_mem_limit = (available_mem // 2)  # memory limit for server and client each
        resource.setrlimit(resource.RLIMIT_AS, (internal_mem_limit, internal_mem_limit))

    with subprocess.Popen(server_command, stdout=subprocess.PIPE) as server_process:
        port = 0
        for line in server_process.stdout:
            if "Server listening on port " in line.decode():
                port = int(re.search(r'\d+', line.decode()).group())
                break
        connecting_end = time.time()
        if port == 0:
            print(server_process.stdout)
            print("Cannot setup policy server", flush=True)
            return_code = 2
        else:
            connection_time = round(connecting_end - script_start)
            print(f"Connection established in {connection_time}s", flush=True)
            try:
                fd_timeout = None if args.timeout is None else max(0, args.timeout - connection_time)
                if fd_timeout is not None and fd_timeout <= 0:
                    print("No time remaining. FD process not started.", flush=True)
                    server_process.terminate()
                    sys.exit(4)
                print("Starting FD process", flush=True)
                fd_process = subprocess.run([args.downward, "--remote-policy", f"localhost:{port}", "--search", args.search],
                                            timeout=args.timeout)
                return_code = fd_process.returncode
                print(f"FD process terminated with return code {return_code}", flush=True)
            except subprocess.TimeoutExpired:
                print("FD process timed out", flush=True)
                return_code = 4
            server_process.terminate()
            if return_code == 35:
                print("\nProblem with remote policy detected, printing policy server log", flush=True)
                print(server_process.stdout, flush=True)
    sys.exit(return_code)
