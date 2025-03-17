"""
# -------------------------------------------------------------
# PYTHON File
# NOTE: 
#   - DO NOT EDIT sections marked as [DO NOT EDIT]
#   - Sections without this mark can be modified as needed.
# -------------------------------------------------------------
Beam transformers.
"""

# [CAN EDIT] - All

from typing import Iterator, Dict, Any, List


def convert_dict_to_list(inputs: dict, reference: List[str] = None) -> list:
    """
    Convert input(s) to a list of dictionaries for processing and reorder the keys
    based on the provided reference list.

    Parameters
    ----------
    inputs : Union[Dict, List[Dict]]
        Input dictionary or a list of dictionaries.
    reference : List[str], optional
        A list of keys defining the desired order of dictionary keys.

    Returns
    -------
    List[Dict]
        A list containing the input dictionary(s) with keys ordered according to the reference list.
    """

    if not reference:
        # If no reference is provided, return values as they appear in the input dictionary
        return list(inputs.values())

    # Return the values in the order defined by the reference list
    # And fill null by 0
    return [inputs[key] or 0 for key in reference if key in inputs]


def array_to_string(
    inputs,
    entity_size,
) -> Iterator[str]:
    """
    Converts numerical data, either a scalar or an array, to a CSV-formatted string.

    This function takes either a scalar value (float or int) or a list/array of numerical
    values, and converts the data into a comma-separated string. If the input is a scalar,
    it wraps it in a list before converting.

    Parameters
    ----------
    data : float, int, or list/array of float/int
        The input data to be converted.

    Returns
    -------
    str
        A string of comma-separated values representing the input data.
        If the input is a scalar, the returned string will contain a single value.

    Examples
    --------
    >>> array_to_string(5.0)
    '5.0'

    >>> array_to_string([1.0, 2.5, 3])
    '1.0,2.5,3'
    """
    for data in inputs:
        yield ",".join(map(str, data[entity_size:]))


def array_to_dicts(
    inputs,
    timestamp,
    output_type,
    output_desc,
) -> Iterator[Dict[str, Any]]:
    """
    Converts a list of tuples into a list of dictionaries with predefined keys.

    Parameters
    ----------
    inputs : list of tuple
        Each tuple contains values corresponding to ACCOUNT_ID, SERVICE_ID, 
        SERVICE_NUM, BRAND, FLEX_ATTR_NAME, FLEX_ATTR_VALUE, and FLEX_ATTR_DESC.
    timestamp : str
        A timestamp string to be added to each dictionary under the key SCORE_EXPIRY_DTM.

    Returns
    -------
    list of dict
        A list of dictionaries where each dictionary represents a row of data with the specified keys.
    """
    # Join the values as a dictionary
    for data in inputs:
        yield dict(
            ACCOUNT_ID=str(data[2]),
            SERVICE_ID=str(data[0]),
            SERVICE_NUM=str(data[1]),
            BRAND=data[4],
            FLEX_ATTR_NAME=output_type,
            FLEX_ATTR_VALUE=str(data[7]),
            FLEX_ATTR_DESC=output_desc,
            SCORE_EXPIRY_DTM=timestamp,
        )


def convert_to_bq_dicts(
    inputs,
    timestamp,
) -> Iterator[Dict[str, Any]]:
    """
    Converts a list of tuples into a list of dictionaries with predefined keys.
    
    Parameters
    ----------
    inputs : list of tuple
        Each tuple contains values for MODEL_ID, BRAND, KEY_TYPE, KEY_VALUE, 
        MODEL_OUTPUT, MODEL_OUTPUT_TYPE, and CREATE_DATE.
    
    Returns
    -------
    list of dict
        A list of dictionaries with keys: MODEL_ID, KEY_VALUE, MODEL_OUTPUT, CREATE_DATE.
    """
    for data in inputs:
        yield {
            "MODEL_ID": data[3],
            "KEY_VALUE": data[0],
            "MODEL_OUTPUT": float(data[7]),
            "CREATE_DATE": data[9],
        }
