
from typing import Dict, Union


MATCH_TYPES : Dict[str, Union[bool, int, str]] = {
    "get_bool": "bool",
    "get_real": "float",
    "get_int": "int",
    "get_dword": "int",
    "get_string": "str",
}