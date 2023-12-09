"""
app.py - The qcc-gateway-hl7-listener test harness application.
"""
import argparse
from argparse import ArgumentParser

import hl7
from hl7.client import MLLPClient


CLI_DESCRIPTION = """
The qcc-gateway-hl7-listener test harness is used to manually test and verify the qcc-gateway-hl7-listener service.
"""


def _create_arg_parser() -> ArgumentParser:
    """Creates the Argument Parser for the CLI utility."""
    parser = argparse.ArgumentParser(
        prog="qcc-gateway-hl7-listener test-harness",
        description=CLI_DESCRIPTION,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument("path", type=str, help="The path to the hl7 file")
    parser.add_argument(
        "--host",
        type=str,
        help="The MLLP host name",
        default="localhost",
        required=False,
    )
    parser.add_argument(
        "--port",
        type=int,
        help="The MLLP port",
        default=2575,
        required=False
    )
    return parser


def run_app(hl7_path: str, mllp_host: str="localhost", mllp_port: int=2575):
    """run_app runs the qcc-gateway-hl7-listener test harness application."""
    print("=" * 25)
    print("starting test harness app with parameters:")
    print(f"hl7_path = {hl7_path}")
    print(f"mllp_host = {mllp_host}")
    print(f"mllp_port = {mllp_port}")

    with open(hl7_path) as f:
        hl7_data = f.read()
        hl7_message = hl7.parse_hl7(hl7_data)

    print("sending hl7 message ....")
    mllp_client = MLLPClient(mllp_host, mllp_port)
    ack = mllp_client.send_message(hl7_message)

    print(f"received HL7 acknowledgement:\n{ack}")
    print("="*25)


if __name__ == "__main__":
    arg_parser = _create_arg_parser()
    parsed_args = arg_parser.parse_args()
    run_app(parsed_args.path, parsed_args.host, parsed_args.port)
