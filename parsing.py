import pandas as pd


def is_float(s: str) -> bool:
    """Returns True if the string can be coerced to float."""
    try:
        float(s)
        return True
    except ValueError:
        return False


def validate_column_lengths(d) -> bool:
    """
    Verifies that all dict entries have the same length.  The most common
    parsing error when parsing columns independently is to create lists of
    different lengths.
    """
    lengths = [None] * len(d.keys())
    for idx, key in enumerate(d.keys()):
        lengths[idx] = len(d[key])

    validated = True
    for length in lengths:
        if length != lengths[0]:
            validated = False

    if not validated:
        len_dict = {_column: length for _column, length in zip(d.keys(), lengths)}
        msg = f"column lenths are not all the same: {len_dict} "
        raise RuntimeError(msg)
    return True


def process_tax_and_fees_col(_column) -> dict:
    """
    Taxes and fees columns are merged together and contain many NA's
    Tax and Fee entries always alternate due to this merging artifact
    Both entries have a currency associated with it.
    """
    new_data = {}
    _column = _column.copy()
    _column = _column.loc[3:]
    _column = _column[~pd.isna(_column)]

    taxes = []
    taxes_currency = []
    fees = []
    fees_currency = []
    is_tax = True
    for entry in _column:
        *value, currency = entry.split(" ")
        value = "".join(value)
        if is_tax:
            taxes.append(float(value))
            taxes_currency.append(currency)
            is_tax = not is_tax
        else:
            fees.append(float(value))
            fees_currency.append(currency)
            is_tax = not is_tax

    new_data["Taxes"] = taxes
    new_data["Taxes currency"] = taxes_currency
    new_data["Fees"] = fees
    new_data["Fees currency"] = fees_currency

    return new_data


def process_df_into_order_type_col(df: "pd.DataFrame") -> dict:
    """Only rows with transaction have an order type."""
    new_data = {}
    _id_column = df.iloc[3:, 0]
    _column = df.iloc[3:, 3]
    _column = _column[~pd.isna(_id_column)]
    new_data["Order type"] = _column.values.tolist()
    return new_data


def process_transaction_table(df: "pd.DataFrame") -> "pd.DataFrame":
    """
    Process a raw transaction table into something useful. The transactions
    table lists all of the actions like sales, purchases, dividends, and
    transfers.
    """
    cols = df.iloc[1, :]
    new_data = {}

    if cols[0] == "Transaction ID":
        _column = df.iloc[2:, 0]
        new_data["Transaction ID"] = _column[~pd.isna(_column)].values.tolist()
    else:
        raise ValueError(
            f"expected:  cols[0] == 'Transaction ID'.  Received: {cols[0]}"
        )

    if cols[1] == "Execution date":
        _column = df.iloc[2:, 1]
        _column = _column[~pd.isna(_column)]
        new_data["Execution date"] = _column
    else:
        msg = f"expected cols[1] == 'Execution date'.  received:  {cols[1]}"
        raise ValueError(msg)

    if cols[2] == "Transaction type Quantity":
        _column = df.iloc[:, 2].str.split(" ").copy()
        _column = _column.loc[2:]  # skip 'bad' header
        _column = _column[~pd.isna(_column)]
        new_data["Transaction type"] = [x[0] for x in _column]
        new_data["Quantity"] = [float(x[1]) for x in _column]
    else:
        msg = (
            f"expected:  cols[2] == 'Transaction type Quantity'.  received:  {cols[2]}"
        )
        raise ValueError(msg)

    if cols[3] == "Order type":
        order_dict = process_df_into_order_type_col(df)
        new_data = {**new_data, **order_dict}
    else:
        msg = "Check column 3:  expected 'Order type'"
        raise ValueError(msg)

    if cols[4] == "Exchange":
        # exchange is the market type, e.g. on the exchange or not
        pass
    else:
        msg = f"Check column idx 4:  should be Exchange, which can be ignored.  received:  {cols[4]}"
        raise ValueError(msg)

    if cols[5] == "Execution price Option execution":
        _column = df.iloc[:, 5].str.split(" ").copy()
        _column = _column.loc[3:]  # 'cost' is in row 2
        _column = _column[~pd.isna(_column)]
        new_data["Execution price"] = [float(x[0]) for x in _column]
        new_data["Execution price currency"] = [x[1] for x in _column]
        new_data["Option execution cost"] = [float(x[2]) for x in _column]
        new_data["Option execution cost currency"] = [x[3] for x in _column]
    else:
        msg = "Check Column 5:  expected 'Execution price Option execution'"
        raise ValueError(msg)

    if cols[6] == "Taxes /":
        tax_dict = process_tax_and_fees_col(df.iloc[:, 6])
        new_data = {**new_data, **tax_dict}
    else:
        msg = f"expected:  cols[6] == 'Taxes /'.  received:  {cols[6]}"
        raise ValueError(msg)

    if cols[7] == "Cash /":
        _column = df.iloc[3:, 7]
        _column = _column[~pd.isna(_column)]

        proceeds = []
        proceeds_currency = []
        units = []
        for entry in _column:
            if entry[-3:] == "CHF":
                value, currency = entry.split(" ")
                proceeds.append(float(value))
                proceeds_currency.append(currency)
            elif is_float(entry):
                units.append(float(entry))
            else:
                msg = f"something wrong with col 7:{entry}"
                raise ValueError(msg)

        new_data["Net proceeds"] = proceeds
        new_data["Net proceeds currency"] = proceeds_currency
        new_data["Net proceeds units"] = units
    else:
        msg = f"expected:  cols[7] == 'Cash /'.  received:  {cols[6]}"
        raise ValueError(msg)

    try:
        validate_column_lengths(new_data)
    except Exception as e:
        raise e

    return pd.DataFrame(new_data)
