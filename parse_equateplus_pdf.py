#!/usr/bin/env python
#
# Parse EquatePlus Tables
# Developed with Python 3.8.13
#
# ComputerShare/Equateplus can sometimes give a list of transactions as part of
# their 1099 tax form, instead of a summary of activities.  .
#
# Because the ComputerShare/Equateplus developers present a "pretty" table of
# transactions, PDF parsing auto-generates a messy object. The transactions
# tables are a merge of several different kinds of transactions (e.g. sales,
# dividends, vesting withhold-to-cover activities, transers, etc).  The simplest
# way to clean the parsed table is to parse it column-wise.
#
# This script will parse the hellscape PDF into a tidy dataframe, saved as a csv,
# which can be further processed for easier tax reporting.

import argparse
import sys
import time

import pandas as pd
import tabula

import parsing


def get_args() -> "argparse.Namespace":
    """Defines the command line arguments to parse_equateplus_pdf."""

    parser = argparse.ArgumentParser(description="EquatePlus/ComputerShare PDF Parser")
    parser.add_argument("--pdf", type=str, help="Path to input PDF")
    parser.add_argument("--output", type=str, help="Path to output CSV")
    return parser.parse_args()


def parse_file_to_csv(pdf: "str", output: "str") -> None:
    """Parses the provided .PDF and creates a .CSV of transactions"""

    tables = tabula.read_pdf(pdf, pages="all")
    ct_transaction_tables = 0

    print("\nCounting the parsed tables...")
    for idx in range(len(tables)):
        df = tables[idx]
        if df.columns[2] == "Grant details":
            print(f"#:{idx} positions table")
        if df.columns[2] == "Transaction details":
            ct_transaction_tables += 1
            print(f"#:{idx} transactions table")

    print("\nParsing transactions tables...")
    transaction_df_list = [None] * ct_transaction_tables
    df_idx = 0
    for table in tables:
        if table.columns[2] == "Transaction details":
            transaction_df_list[df_idx] = parsing.process_transaction_table(table)
            df_idx += 1

    transactions = pd.concat(transaction_df_list)

    print(f"Saving {transactions.shape[0]} transactions to {args.output}...")
    transactions.to_csv(args.output, index=False)


if __name__ == "__main__":
    print(f"Start: {time.asctime()}")
    print(f"Python path: {sys.executable}")
    print(f"Python info: \n{sys.version}\n")

    args = get_args()
    print(args)

    parse_file_to_csv(pdf=args.pdf, output=args.output)

    print(f"End:  {time.asctime()}")
