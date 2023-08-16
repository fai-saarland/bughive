#!/usr/bin/env python3

import subprocess
import argparse
import re
import sys
import time

# example call formatter_class=argparse.ArgumentDefaultsHelpFormatter

script_start = time.time()
parser = argparse.ArgumentParser(description="Driver for debugging remote ASNet policies",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("asnet", help="Path to the script starting the ASNet server")
parser.add_argument("model", help="Path to the ASNet policy file")
parser.add_argument("domain", help="Path to the PDDL domain file")
parser.add_argument("problem", help="Path to the PDDL problem file")
parser.add_argument("fd", help="Path to the FD executable (not the driver script)")
parser.add_argument("search", help="Search configuration of FD")
parser.add_argument("-t", "--timeout", type=int, help="Time limit for the driver in seconds")
args = parser.parse_args()

command = [args.asnet, "localhost:0", args.model, args.domain, args.problem]
return_code = 3

with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as server_process:
    port = 0
    for line in server_process.stdout:
        if "Server listening on port " in line.decode():
            port = int(re.search(r'\d+', line.decode()).group())
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
            fd_process = subprocess.run([args.fd, "--remote-policy", f"localhost:{port}", "--search", args.search], timeout=args.timeout)
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
