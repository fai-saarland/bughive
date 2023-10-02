#!/usr/bin/env python3

import argparse
import os.path
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='policy server url', default="localhost:0")
    parser.add_argument('--fd', required=True, help='path to FD (for invoking translator)',)
    parser.add_argument('--domain', required=True, help='domain file')
    parser.add_argument('--model', required=True, help='model file')
    parser.add_argument('--problem', required=True, help='problem file')
    return parser.parse_args()


def get_task():
    with open("output.sas", "r") as f:
        return f.read()


def apply_policy(state):
    return policy.apply_policy_to_state(state)


if __name__ == "__main__":
    args = parse_arguments()
    from gnn.network import plan as policy
    from pheromone import pheromone
    subprocess.call(f"python3 {args.fd} --translate {args.domain} {args.problem}", shell=True, stdout=subprocess.DEVNULL)
    policy.setup(f"--domain {args.domain} --problem {args.problem} --model {args.model} --sas output.sas")
    pheromone.start_server(args.url, get_task, apply_policy)

