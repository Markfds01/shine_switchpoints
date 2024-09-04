import argparse
import sys


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-r",
        "--region",
        type=str,
        required=True,
        help="A valid region abbreviation"
    )

    parser.add_argument(
        "-ns",
        "--n-switchpoints",
        type=int,
        required=True,
        help="Maximum number of switchpoints to test"
    )

    parser.add_argument(
        "-w",
        "--weekly-model",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Flag to use the weekly model or the daily model"
    )

    parser.add_argument(
        "-d",
        "--deaths",
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Flag to indicate if estimate deaths instead of hospitalizations"
    )
    parser.add_argument(
        "-ag",
        "--ages",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Flag to indicate if you want to predict by age groups"
    )
    parser.add_argument(
        "-sw",
        "--switchpoints",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Flag to indicate if you want to predict switchpoints"
    )
    parser.add_argument(
        "-aw",
        "--weekly",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Flag to indicate if you want to do rolling average weekly"
    )
    
    

    return parser.parse_args(args)
