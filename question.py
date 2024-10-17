from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, field
from typing import Any


@dataclass
class BonusConditions:
    """
    Dataclass representing the conditions needed to get bonus points.

    Passing in "for" into `blacklisted_keywords` will not blacklist generator
    expressions. To disallow generator expressions use "gen" instead.

    Attributes:
        blacklisted_packages: Blacklisted external packages.
        blacklisted_keywords: Blacklisted Python built-in keywords.
        blacklisted_functions: Blacklisted Python built-in functions.
    """

    _: KW_ONLY  # The following are keyword-only arguments
    blacklisted_packages: set[str] | list[str] | tuple[str, ...] = field(
        default_factory=set
    )
    blacklisted_keywords: set[str] | list[str] | tuple[str, ...] = field(
        default_factory=set
    )
    blacklisted_functions: set[str] | list[str] | tuple[str, ...] = field(
        default_factory=set
    )

    def __post_init__(self) -> None:
        # Make sure all arguments are sets if they are not None
        if isinstance(self.blacklisted_packages, list | tuple):
            self.blacklisted_packages = set(self.blacklisted_packages)
        if isinstance(self.blacklisted_keywords, list | tuple):
            self.blacklisted_keywords = set(self.blacklisted_keywords)
        if isinstance(self.blacklisted_functions, list | tuple):
            self.blacklisted_functions = set(self.blacklisted_functions)

        # There must be at least one condition
        if not (
            self.blacklisted_packages
            or self.blacklisted_keywords
            or self.blacklisted_functions
        ):
            msg = "The bonus conditions must have at least one condition"
            raise ValueError(msg)


@dataclass
class Bonus:
    """
    Dataclass representing bonus points and the conditions needed.

    `bonus_points` must be a positive number.

    Attributes:
        bonus_points: The number of bonus points available.
        conditions: The conditions needed to award the bonus points.
    """

    bonus_points: float
    conditions: BonusConditions

    def __post_init__(self) -> None:
        # Ensure bonus_points is positive
        if self.bonus_points <= 0:
            msg = "Bonus points must be positive"
            raise ValueError(msg)


@dataclass
class TestCase:
    """
    Dataclass representing a test case for a question.

    Attributes:
        input_args: The arguments to pass into the solution function.
        input_kwargs: The keyword arguments to pass in.
        expected_output: The expected output.
    """

    _: KW_ONLY  # The following are keyword-only arguments
    input_args: tuple = ()
    input_kwargs: dict = field(default_factory=dict)
    expected_output: Any

    # prevent pytest treating class as a test case
    __test__ = False

    def __post_init__(self) -> None:
        # Ensure input_args is a tuple
        if not isinstance(self.input_args, tuple):
            msg = "Input args must be a tuple"
            raise ValueError(msg)


@dataclass
class Question:
    """
    Dataclass representing a question.

    A question includes the test cases for the question, and possibly any whitelisted
    external packages and bonus points.

    Attributes:
        question_number: The question number.
        whitelisted_packages: The whitelisted external packages that can be used.
        bonus: Bonus points and the conditions needed to earn them if they're available.
        test_cases: The test cases for the question.
    """

    question_number: int

    _: KW_ONLY  # The following are keyword-only arguments

    bonus: Bonus | None = None
    test_cases: list[TestCase] = field(default_factory=list)

    def add_test_case(self, test_case: TestCase) -> None:
        """
        Add a test case to the question.

        :param test_case: The test case to add.
        """
        self.test_cases.append(test_case)
