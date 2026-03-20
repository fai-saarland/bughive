#!/usr/bin/env python3

import argparse
import driver_common


parser = argparse.ArgumentParser(description="Driver for debugging remote ASNet policies",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--asnet", required=True, help="Path to the executable starting the ASNet server")
parser.add_argument("--model", required=True, nargs='+', help="Paths to the policy model files")
parser.add_argument("--verbose", '-v', action='store_true', help="More verbose output.")
driver_common.add_common_args(parser)
args = parser.parse_args()

server_command = [args.asnet, "127.0.0.1:0", args.domain, args.problem] + args.model
if args.verbose:
    server_command.append('--verbose')
driver_common.run_driver(server_command, args)
