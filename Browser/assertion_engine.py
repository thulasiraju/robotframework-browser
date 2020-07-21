from enum import Enum
from typing import (
    Any,
    Dict,
    Tuple,
    Callable,
    TypeVar,
    cast,
    Optional,
    List,
    Union,
)
import re

from robot.libraries.BuiltIn import BuiltIn  # type: ignore

from .utils.robot_booleans import is_truthy

NumericalOperator = Enum(
    "NumericalEnum",
    {
        "equal": "==",
        "==": "==",
        "shouldbe": "==",
        "inequal": "!=",
        "!=": "!=",
        "shouldnotbe": "!=",
        "lessthan": "<",
        "<": "<",
        "greaterthan": ">",
        ">": ">",
        "<=": "<=",
        ">=": ">=",
    },
)
SequenceOperator = Enum(
    "SequenceOperators",
    {
        "contains": "*=",
        "*=": "*=",
        "validate": "validate",
        "equal": "==",
        "==": "==",
        "shouldbe": "==",
        "inequal": "!=",
        "!=": "!=",
        "shouldnotbe": "!=",
    },
)

StringOperator = Enum(
    "StringOperator",
    {
        "contains": "*=",
        "*=": "*=",
        "starts": "^=",
        "^=": "^=",
        "shouldstartwith": "^=",
        "ends": "$=",
        "$=": "$=",
        "matches": "matches",
    },
)

EvalOperator = Enum(
    "EvalOperator", {"validate": "validate", "then": "then", "evaluate": "then"}
)

AssertionOperator = Enum(  # type: ignore
    "AssertionOperator",
    {
        **{i.value: i.name for i in NumericalOperator},
        **{i.value: i.name for i in SequenceOperator},
        **{i.value: i.name for i in StringOperator},
        **{i.value: i.name for i in EvalOperator},
    },
)
AnyOperator = Union[
    NumericalOperator,
    SequenceOperator,
    StringOperator,
    EvalOperator,
    AssertionOperator,
]

handlers: Dict[str, Tuple[Callable, str]] = {
    "==": (lambda a, b: a == b, "should be"),
    "!=": (lambda a, b: a != b, "should not be"),
    "<": (lambda a, b: a < b, "should be less than"),
    ">": (lambda a, b: a > b, "should be greater than"),
    "<=": (lambda a, b: a <= b, "should be less than or equal"),
    ">=": (lambda a, b: a >= b, "should be greater than or equal"),
    "*=": (lambda a, b: b in a, "should contain"),
    "matches": (lambda a, b: re.search(b, a), "should match"),
    "^=": (lambda a, b: re.search(f"^{re.escape(b)}", a), "should start with",),
    "$=": (lambda a, b: re.search(f"{re.escape(b)}$", a), "should end with",),
    "validate": (
        lambda a, b: BuiltIn().evaluate(b, namespace={"value": a}),
        "should validate to true with",
    ),
}


T = TypeVar("T")


def verify_assertion(
    value: T, operator: Optional[AnyOperator], expected: Any, message=""
) -> Any:
    if operator is None:
        return value
    if operator is AssertionOperator["then"]:
        return cast(T, BuiltIn().evaluate(expected, namespace={"value": value}))
    handler = handlers.get(operator.name)
    if handler is None:
        raise RuntimeError(f"{message} `{operator}` is not a valid assertion operator")
    validator, text = handler
    if not validator(value, expected):
        raise AssertionError(f"{message} `{value}` {text} `{expected}`")
    return value


def int_str_verify_assertion(
    value: T, operator: Optional[AssertionOperator], expected: Any, message=""
):
    if operator is None:
        return value
    elif operator in NumericalOperator:
        expected = int(expected)
    elif operator in EvalOperator:
        expected = str(expected)
    else:
        raise ValueError(f"Operator '{operator.name}' is not allowed.")
    return verify_assertion(value, operator, expected, message)


def bool_verify_assertion(
    value: T, operator: Optional[AssertionOperator], expected: Any, message=""
):
    if operator is None:
        return value
    elif operator not in [
        AssertionOperator["=="],
        AssertionOperator["!="],
    ]:
        raise ValueError(f"Operators '==' and '!=' are allowed, not '{operator.name}'.")

    expected_bool = is_truthy(expected)
    return verify_assertion(value, operator, expected_bool, message)


def map_list(selected: List):
    if not selected or len(selected) == 0:
        return None
    elif len(selected) == 1:
        return selected[0]
    else:
        return selected


def sequence_verify_assertion(
    value: Union[List, Dict],
    operator: Optional[SequenceOperator],
    expected: Union[List, Dict],
    message="",
):
    if isinstance(value, list) and isinstance(expected, list):

        expected.sort()
        value.sort()
        return verify_assertion(map_list(value), operator, map_list(expected), message)
    elif isinstance(value, dict) and isinstance(expected, dict):
        return verify_assertion(value, operator, expected, message)
    else:
        raise TypeError(
            "Both value and expected need to be lists or dicts to use sequence assertion."
            f"Their types were: {type(value)}, expected: {type(expected)}"
        )


def int_dict_verify_assertion(
    value: Dict[str, int],
    operator: Optional[AssertionOperator],
    expected: Optional[Dict[str, int]],
    message="",
):
    if not operator:
        return value
    elif expected and operator in NumericalOperator:
        for k, v in value.items():
            exp = expected[k]
            verify_assertion(v, operator, exp, message)
        return True
    elif operator in SequenceOperator:
        return verify_assertion(value, operator, expected, message)
    else:
        raise AttributeError(
            f"Operator '{operator.name}' is not allowed in this Keyword. "
            f"Allowed operators are: {NumericalOperator} and {SequenceOperator}"
        )
