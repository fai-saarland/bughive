#!/usr/bin/env python3

import argparse
import os.path
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True, help='model file')
    parser.add_argument('--url', help='policy server url', default="localhost:0")
    parser.add_argument('--sas', required=False, help='FDR task as sas file')
    parser.add_argument('--fd', required=False, help='path to FD (for invoking translator if no sas file is provided)')
    parser.add_argument('--domain', required=True, help='domain file, required if no sas file is provided')
    parser.add_argument('--problem', required=True, help='problem file, required if no sas file is provided')
    parser.add_argument('--cpu', action='store_true', help='use CPU only')
    return parser.parse_args()


def get_task():
    with open(sas_file, "r") as f:
        return f.read()


def apply_policy(state):
    return policy.apply_policy_to_state(state)


if __name__ == "__main__":
    args = parse_arguments()
    assert args.fd or args.sas
    from gnn.network import plan as policy
    from pheromone import pheromone
    if not args.sas:
        subprocess.call(f"python3 {args.fd} --translate {args.domain} {args.problem}", shell=True, stdout=subprocess.DEVNULL)
    sas_file = args.sas if args.sas else "output.sas"
    setup_args = f"--domain {args.domain} --problem {args.problem} --model {args.model} --sas {sas_file}"
    if args.cpu:
        setup_args += " --cpu"
    policy.setup(setup_args)
    pheromone.start_server(args.url, get_task, apply_policy)

