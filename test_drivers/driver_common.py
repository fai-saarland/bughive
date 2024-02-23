import subprocess
import re
import sys
import time
import resource


def add_common_args(parser):
    parser.add_argument("--model", required=True, help="Path to the policy model file")
    parser.add_argument("--domain", required=True, help="Path to the PDDL domain file, required if no sas file is provided")
    parser.add_argument("--problem", required=True, help="Path to the PDDL problem file, required if no sas file is provided")
    parser.add_argument("--downward", required=True, help="Path to the downward executable (not the FD driver script)")
    parser.add_argument("--search", required=True, help="Search configuration of FD")
    parser.add_argument("-t", "--timeout", type=int, help="Time limit for the driver in seconds")
    parser.add_argument("-m", "--mem", type=int, help="Memory limit for the driver in MiB")
    parser.add_argument("--fdmem", type=int, help="Set maximal memory limit for FD process in MiB")


def run_driver(server_command, args):
    script_start = time.time()
    return_code = 3
    soft_mem_limit, hard_mem_limit = resource.getrlimit(resource.RLIMIT_AS)
    print(f"read memory resource limits of driver process (in bytes): " 
          f"soft={soft_mem_limit if soft_mem_limit >= 0 else 'unlimited'}, " 
          f"hard={hard_mem_limit if hard_mem_limit >= 0 else 'unlimited'}")
    policy_mem_limit = None
    fd_mem_limit = None
    set_mem_limit = False
    if args.mem is not None:
        available_mem = args.mem * 1024 * 1024 - 1024 * 1024
        set_mem_limit = True
    else:
        if soft_mem_limit >= 0:
            available_mem = soft_mem_limit - 1024 * 1024
            set_mem_limit = True
    if set_mem_limit:
        if available_mem <= 1024 * 1024:
            print("Not enough memory provided. Server and FD not started.")
            sys.exit(5)
        if args.fdmem:
            fd_mem_limit = min(available_mem, args.fdmem * 1024 * 1024)
            policy_mem_limit = available_mem - fd_mem_limit
            if fd_mem_limit <= 1024*1024 or policy_mem_limit <= 1024*1024:
                print(f"FD or policy mem limit not high enough.")
                sys.exit(5)
        else:
            policy_mem_limit = (available_mem // 2)
            fd_mem_limit = policy_mem_limit

    def set_policy_mem_limit():
        if policy_mem_limit:
            print(f"limiting policy server process to {policy_mem_limit} bytes", flush=True)
            resource.setrlimit(resource.RLIMIT_AS, (policy_mem_limit, hard_mem_limit))

    def set_fd_mem_limit():
        if fd_mem_limit:
            print(f"limiting fd process to {fd_mem_limit} bytes", flush=True)
            resource.setrlimit(resource.RLIMIT_AS, (fd_mem_limit, hard_mem_limit))
    
    print("Starting policy server")
    with subprocess.Popen(server_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=set_policy_mem_limit) as server_process:    
        port = 0
        for line in server_process.stdout:
            decoded_line = line.decode()
            print(decoded_line, end="")
            if "Server listening on port " in decoded_line:
                port = int(re.search(r'\d+', decoded_line).group())
                break
        connecting_end = time.time()
        if port == 0:
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
                                            timeout=args.timeout, preexec_fn=set_fd_mem_limit)
                return_code = fd_process.returncode
                print(f"FD process terminated with return code {return_code}", flush=True)
            except subprocess.TimeoutExpired:
                print("FD process timed out", flush=True)
                return_code = 4
            server_process.terminate()
            if return_code == 35:
                print("\nProblem with remote policy detected, return code 35", flush=True)
            server_log = server_process.stdout.read().decode()
            if server_log:
                print(f"Policy server log:\n{server_log}", flush=True)
    sys.exit(return_code)
