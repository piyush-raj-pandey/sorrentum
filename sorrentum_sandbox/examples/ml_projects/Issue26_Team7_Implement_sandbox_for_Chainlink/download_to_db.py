#!/usr/bin/env python
"""
Download chainlink data from Binance and save it into the DB.

Use as:
> download_to_db.py --pair ETH/USD --num_of_data 10 --target_table 'chainlink_history'

> download_to_db.py --pair ETH/USD --roundid 55340232221128670494 --target_table 'chainlink_real_time'
"""
import argparse
import logging

import helpers.hdbg as hdbg
import helpers.hparser as hparser
import sorrentum_sandbox.projects.Issue26_Team7_Implement_sandbox_for_Chainlink.db as sisebidb
import sorrentum_sandbox.projects.Issue26_Team7_Implement_sandbox_for_Chainlink.download as sisebido


_LOG = logging.getLogger(__name__)


def _add_download_args(
    parser: argparse.ArgumentParser,
) -> argparse.ArgumentParser:
    """
    Add the command line options for exchange download.
    """
    parser.add_argument(
        "--pair",
        action="store",
        required=True,
        type=str,
        help="Currency pair to download",
    )
    parser.add_argument(
        "--num_of_data",
        action="store",
        required=False,
        type=int,
        help="Number of data to download",
    )
    parser.add_argument(
        "--roundid",
        action="store",
        required=False,
        type=str,
        help="Roundid for the last stored transaction data",
    )
    parser.add_argument(
        "--target_table",
        action="store",
        required=True,
        type=str,
        help="Name of the db table to save data into"
    )
    return parser


def _parse() -> argparse.ArgumentParser:
    hdbg.init_logger(use_exec_path=True)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser = _add_download_args(parser)
    parser = hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    # Load data.
    if(args.roundid is None):
        raw_data = sisebido.downloader(pair = args.pair, num_of_data = args.num_of_data)
    elif(args.num_of_data is None):
        raw_data = sisebido.downloader(pair = args.pair, roundid = args.roundid)
    # Save data to DB.
    db_conn = sisebidb.get_db_connection()
    saver = sisebidb.PostgresDataFrameSaver(db_conn)
    saver.save(raw_data, args.target_table)


if __name__ == "__main__":
    _main(_parse())
