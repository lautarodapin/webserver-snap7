from datetime import datetime
from django.utils.timezone import now
import pytest
from app.fields import MultiType

def test_bool_multi_type():
    field_1 = MultiType("bool", True)
    field_2 = MultiType("bool", False)
    field_3 = MultiType("bool", "False")
    field_4 = MultiType("bool", "false")
    field_5 = MultiType("bool", 0)
    field_6 = MultiType("bool", 1)

    
    assert field_1.type == "bool"
    assert field_2.type == "bool"
    assert field_3.type == "bool"
    assert field_4.type == "bool"
    assert field_5.type == "bool"
    assert field_6.type == "bool"

    assert field_1.value == True
    assert field_2.value == False
    assert field_3.value == False
    assert field_4.value == False
    assert field_5.value == False
    assert field_6.value == True


def test_int_multi_type():
    field_1 = MultiType("int", 10)
    field_2 = MultiType("int", 10.5)
    field_3 = MultiType("int", "10")

    assert field_1.type == "int"
    assert field_2.type == "int"
    assert field_3.type == "int"

    assert field_1.value == 10
    assert field_2.value == 10
    assert field_3.value == 10

def test_float_multi_type():
    field_1 = MultiType("float", 10)
    field_2 = MultiType("float", 10.5)
    field_3 = MultiType("float", "10")
    field_4 = MultiType("float", "10.5")

    assert field_1.type == "float"
    assert field_2.type == "float"
    assert field_3.type == "float"
    assert field_4.type == "float"

    assert field_1.value == 10.0
    assert field_2.value == 10.5
    assert field_3.value == 10.0
    assert field_4.value == 10.5


def test_datetime_multi_type():
    today = now()
    field = MultiType("datetime", today)
    assert field.type == "datetime"
    assert field.value == today

    field = MultiType("datetime", str(today))

    assert field.type == "datetime"
    assert field.value == today
