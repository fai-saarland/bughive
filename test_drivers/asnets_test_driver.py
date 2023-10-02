#!/usr/bin/env python3

import argparse
import driver_common


parser = argparse.ArgumentParser(description="Driver for debugging remote ASNet policies",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("asnet", help="Path to the executable starting the ASNet server")
driver_common.add_common_args(parser)
args = parser.parse_args()

server_command = [args.asnet, "localhost:0", args.model, args.domain, args.problem]
driver_common.run_driver(server_command, args)
