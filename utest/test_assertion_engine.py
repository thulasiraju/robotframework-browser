import pytest
from Browser.assertion_engine import verify_assertion, AssertionOperator
from robot.libraries.BuiltIn import EXECUTION_CONTEXTS  # type: ignore


def test_equals():
    _validate_operator(AssertionOperator["=="], "actual", "actual", "unexpected")


def _validate_operator(operator: AssertionOperator, actual, expected, invalid):
    verify_assertion(actual, operator, expected)
    with pytest.raises(AssertionError):
        verify_assertion(actual, operator, invalid)


def test_not_equals():
    _validate_operator(AssertionOperator["!="], "actual", "expected", "actual")


def test_contains():
    _validate_operator(AssertionOperator["contains"], "actual", "ctua", "nope")
    _validate_operator(AssertionOperator["*="], "actual", "tual", "nope")


def test_greater():
    _validate_operator(AssertionOperator["<"], 1, 2, 0)


def test_less():
    _validate_operator(AssertionOperator[">"], 2, 1, 3)


def test_greater_or_equal():
    _validate_operator(AssertionOperator["<="], 1, 2, 0)
    _validate_operator(AssertionOperator["<="], 1, 1, 0)


def test_less_or_equal():
    _validate_operator(AssertionOperator[">="], 2, 2, 3)
    _validate_operator(AssertionOperator[">="], 2, 1, 3)


def test_match():
    _validate_operator(AssertionOperator["matches"], "Actual", "(?i)actual", "/(\\d)+/")
    _validate_operator(AssertionOperator["matches"], "Actual", "^Act", "/(\\d)+/")
    _validate_operator(AssertionOperator["matches"], "Actual", "ual$", "/(\\d)+/")
    _validate_operator(
        AssertionOperator["matches"],
        "Actual\nmultiline",
        "(?m)Actual\nmultiline$",
        "/(\\d)+/",
    )


def test_validate():
    def ns(): pass
    ns.variables = lambda: 0
    ns.variables.current = lambda: 0
    ns.variables.current.store = lambda: 0
    EXECUTION_CONTEXTS.start_suite("suite", ns, lambda: 0)
    _validate_operator(
        AssertionOperator("validate"), 1, "0 < value < 2", "value == 'hello'"
    )


def test_then():
    def ns(): pass
    ns.variables = lambda: 0
    ns.variables.current = lambda: 0
    ns.variables.current.store = lambda: 0
    EXECUTION_CONTEXTS.start_suite("suite", ns, lambda: 0)
    thenOp = AssertionOperator["then"]
    assert verify_assertion(8, thenOp, "value + 3") == 11
    assert verify_assertion(2, thenOp, "value + 3") == 5
    assert verify_assertion("René", thenOp, "'Hello ' + value + '!'") == "Hello René!"


def test_start_with():
    _validate_operator(AssertionOperator["^="], "Hello Robots", "Hello", "Robots")
    _validate_operator(
        AssertionOperator["shouldstartwith"], "Hello Robots", "Hello", "Robots"
    )
    _validate_operator(
        AssertionOperator["^="], "Hel[4,5]?[1-9]+ Robots", "Hel[4,5]?[1-", ".*"
    )


def test_ends_with():
    _validate_operator(AssertionOperator["$="], "Hello Robots", "Robots", "Hello")
    _validate_operator(
        AssertionOperator["$="], "Hel[4,5]?[1-9]+ Robots", "[1-9]+ Robots", ".*"
    )
