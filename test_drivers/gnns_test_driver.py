#!/usr/bin/env python3

import argparse
import driver_common

parser = argparse.ArgumentParser(description="Driver for debugging remote GNN policies",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("gnn", help="Path to the executable starting the GNN server")
parser.add_argument("fd", help="Path to the FD driver script (for invoking the translator)")
driver_common.add_common_args(parser)
args = parser.parse_args()

server_command = [args.gnn, "--url", "localhost:0", "--fd", args.fd, "--model", args.model, "--domain", args.domain,
                  "--problem", args.problem]
driver_common.run_driver(server_command, args)
