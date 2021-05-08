from typing import Any, Optional, Union
from django.db import models
from django.utils.functional import cached_property
from django.utils.timezone import datetime
from dateutil.parser import parse as date_parse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class MultiType:
    # TODO using pydantic or dataclass for automatic validation
    def __init__(self, type, value) -> None:
        self.type: str = str(type)
        self._value: str = str(value)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.type}:{self._value}"

    def __len__(self) -> int:
        return len(self.type) + len(self._value)

    @cached_property
    def value(self) -> Union[bool, str, int, float, datetime]:
        if self.type == "bool":
            if self._value in ["False", "false", "0", 0, False]:
                return False
            elif self._value in ["True", "true", "1", 1, True]:
                return True
        elif self.type == "str":
            return str(self._value)
        elif  self.type == "int":
            return int(float(self._value))
        elif self.type == "float":
            return float(self._value)
        elif self.type == "datetime":
            if isinstance(self._value, datetime):
                return self._value
            return date_parse(self._value)
        raise TypeError(_(f"{self.type} is not a valid type"))

def parse_multi_type(string: str) -> MultiType:
    args = string.split(":", 1)
    # TODO agregar validacion
    if args[0] not in ["bool", "str", "int", "float", "datetime"]:
        raise TypeError(_(f"{args[0]} is not a valid type"))
    if len(args) != 2:
        raise ValueError(_("Invalid input for MultiType instance"))
    return MultiType(*args)

class MultiTypeField(models.CharField):
    description = _("MultiType Field that can save Boolean, Int, Float, Strings")
    
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 500  # Fixed max length
        super().__init__(*args, **kwargs)
        
    def deconstruct(self) -> Any:
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def to_python(self, value: Optional[Union[MultiType, str]]) -> Optional[MultiType]:
        if isinstance(value, MultiType):
            return value
        if value is None:
            return value
        return parse_multi_type(value)

    def from_db_value(self, value: Optional[str], expression, connection) -> Optional[MultiType]:
        if value is None:
            return value
        return parse_multi_type(value)

    def get_prep_value(self, value: MultiType) -> str:
        return ":".join([value.type, (value._value)])
