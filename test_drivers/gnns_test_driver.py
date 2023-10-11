#!/usr/bin/env python3

import argparse
import driver_common

parser = argparse.ArgumentParser(description="Driver for debugging remote GNN policies",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--gnn", required=True, help="Path to the executable starting the GNN server")
parser.add_argument("--fd", required=False, help="Path to the FD driver script (for invoking the translator)")
parser.add_argument("--sas", required=False, help="Path to the task sas file")
parser.add_argument('--cpu', action='store_true', help='use CPU only in GNN server')
driver_common.add_common_args(parser)
args = parser.parse_args()
assert args.sas or args.fd

server_command = [args.gnn, "--model", args.model, "--domain", args.domain, "--problem", args.problem]

if args.sas:
    server_command += ["--sas", args.sas]
else:
    server_command += ["--fd", args.fd]
if args.cpu:
    server_command += ["--cpu"]
driver_common.run_driver(server_command, args)
