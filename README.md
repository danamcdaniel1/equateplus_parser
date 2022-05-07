# EquatePlus PDF Parser

ComputerShare/Equateplus can sometimes give a list of transactions as part of
their 1099 tax form, instead of a summary of activities.  This document can easily
become dozens of pages long, and present a serious challenge for tax reporting to
the IRS.

This project parses a ComputerShare/Equateplus Tax Summary PDF into a tidy pandas 
dataframe, then saves it as a csv, which can be further summarized for easier tax 
reporting.

Because the ComputerShare/Equateplus developers present a "pretty" table of
transactions for human consumption, PDF parsing is not trivial. The transactions
tables are a merge of several different kinds of transactions (e.g. sales,
dividends, vesting withhold-to-cover activities, transers, etc).  The simplest
way to clean the parsed table is to parse it column-wise.

