from __future__ import annotations

import ast
import contextlib
import importlib
import inspect
import sys
import timeit
from dataclasses import KW_ONLY, dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from func_timeout import func_timeout

if TYPE_CHECKING:
    import os
    from collections.abc import Callable, Generator

    from question import BonusConditions, Question, TestCase

FUNCTION_RUNTIME_LIMIT = 30
FLOAT_DIFF_TOLERANCE = 1e-5


class Result(Enum):
    """
    Enum for the result of a test case.

    Attributes:
        PASSED: Test case passed.
        FAILED: Test case failed.
    """

    PASSED: str = "Pass"
    FAILED: str = "Fail"


class BonusResult(Enum):
    """
    Enum for the result of a bonus check.

    Attributes:
        PASSED: Bonus conditions met.
        FAILED: Bonus conditions not met.
        NA: Bonus conditions not checked (either no bonus conditions or test
        cases failed so bonus conditions not checked).
    """

    PASSED: str = "Pass"
    FAILED: str = "Fail"
    NA: str = ""


@dataclass
class TestCaseOutput:
    """
    Dataclass representing the output of a test case.

    Attributes:
        result: The result of the test case.
        output: The received output from the solution function.
        message: Output message.
        runtime: The runtime of the test case.
        exception: Boolean flag for if an exception was raised.
    """

    result: Result
    _: KW_ONLY
    output: Any = ""
    message: Any = ""
    runtime: float | str = ""
    exception: bool = False


@dataclass
class Results:
    """
    Dataclass representing the results of marking a submission.

    Attributes:
        test_case_results: The results of all test cases.
        bonus_results: Whether any bonus conditions were met.
        points: The number of points scored.
        runtime: The total runtime if all test cases passed and zero otherwise.
    """

    test_case_results: list[TestCaseOutput]
    bonus_result: BonusResult
    points: float
    runtime: float


class Marker:
    def __init__(self) -> None:
        pass

    @staticmethod
    def _values_match(expected: Any, actual: Any) -> bool:  # noqa: ANN401, C901, PLR0911
        """
        Check if two values match.

        :param expected: The expected value.
        :param actual: The actual value obtained.
        :return: If the two values match.
        """
        if isinstance(expected, float) and isinstance(actual, float):
            return abs(expected - actual) < FLOAT_DIFF_TOLERANCE

        if isinstance(expected, list | tuple) and isinstance(actual, list | tuple):
            if len(expected) != len(actual):
                return False
            for e, a in zip(expected, actual, strict=True):
                if not Marker._values_match(e, a):
                    return False
            return True

        if isinstance(expected, np.ndarray) and isinstance(actual, np.ndarray):
            if expected.shape != actual.shape or expected.dtype != actual.dtype:
                return False
            if expected.dtype == float:  # If the arrays are float arrays use allclose
                return np.allclose(expected, actual)
            return np.array_equal(expected, actual)

        if isinstance(expected, pd.DataFrame) and isinstance(actual, pd.DataFrame):
            expected = expected.reset_index(drop=True)
            actual = actual.reset_index(drop=True)
            return (
                expected.equals(actual)  # Equal values element-wise
                and expected.shape == actual.shape  # Equal shapes
                and expected.columns.equals(actual.columns)  # Equal columns
            )

        if (
            isinstance(expected, float | int)
            and isinstance(actual, float | int)
            or type(expected) is type(actual)
        ):
            return expected == actual

        return False

    @staticmethod
    def _parse_syntax_tree(filename: str | os.PathLike, code: str) -> ast.AST:
        """
        Parse the abstract syntax tree from some code.

        :param filename: Filename that the code is from.
        :param code: The code string.
        :return: The abstract syntax tree.
        :raises SyntaxError: If there is a syntax error in the code string.
        """
        try:
            ast_tree = ast.parse(code, filename)
        except SyntaxError as e:
            msg, (file, line_no, column, line, *_) = e.args
            raise SyntaxError(msg, (file, line_no, column, line)) from None
        else:
            return ast_tree

    @staticmethod
    def _is_disallowed_function_used(
        ast_node: ast.Call, disallowed_functions: set[str] | list[str] | tuple[str]
    ) -> bool:
        """
        Check if a disallowed function is called in a function call AST node.

        :param ast_node: The function call node.
        :param disallowed_functions: A collection of disallowed functions.
        :return: True if a disallowed function is used.
        :raises ValueError: If `ast_node` is not an ast.Call object.
        """
        if not disallowed_functions:
            return False

        match ast_node:
            # Check if a disallowed function in the form bar() was used
            case ast.Call(
                func=ast.Name(
                    id=function_name
                    )
            ) if function_name in disallowed_functions:  # fmt: skip
                return True

            # Check if a disallowed function in the form foo.bar() was used
            case ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=module_name),
                    attr=function_name)
            ) if f"{module_name}.{function_name}" in disallowed_functions:  # fmt: skip
                return True

            case _:
                return False

    def _is_disallowed_import_used(
        self,
        ast_node: ast.Call | ast.Import | ast.ImportFrom,
        disallowed_imports: set[str] | list[str] | tuple[str],
    ) -> bool:
        """
        Check if a disallowed import is used based on an AST node.

        :param ast_node: A function call or import node.
        :param disallowed_imports: A collection of disallowed imports.
        :return: True if a disallowed import is used.
        :raises ValueError: If `ast_node` is not any of the following:
            ast.Call, ast.Import, or ast.ImportFrom
        """

        if not disallowed_imports:
            return False

        if isinstance(ast_node, ast.Call):
            # Check if disallowed imports are used via __import__
            if (
                self._is_disallowed_function_used(ast_node, {"__import__"})
                and ast_node.args[0].value in disallowed_imports
            ):
                return True

            # Check if disallowed imports are used via importlib
            return (
                self._is_disallowed_function_used(
                    ast_node, {"importlib.import_module", "import_module"}
                )
                and ast_node.args[0].value in disallowed_imports
            )

        # Check if disallowed imports are used
        if isinstance(ast_node, ast.Import) and set(disallowed_imports) & {
            package.name.split(".")[0] for package in ast_node.names
        }:
            return True

        # Check if a function isn't import using `from ... import ...`
        return (
            isinstance(ast_node, ast.ImportFrom)
            and ast_node.module.split(".")[0] in disallowed_imports
        )

    def _obeys_bonus_conditions(
        self, ast_tree: ast.AST, conditions: BonusConditions
    ) -> bool:
        """
        Check if an abstract syntax tree follows bonus conditions.

        :param ast_tree: A abstract syntax tree.
        :param conditions: The conditions needed to get bonus points.
        :return: If all the bonus conditions were met.
        """
        # Get the ast node objects of the keywords
        disallowed_keywords = tuple(
            getattr(ast, node) for node in conditions.blacklisted_keywords
        )
        for node in ast.walk(ast_tree):
            # Check if a disallowed python keyword is used
            if disallowed_keywords and isinstance(node, disallowed_keywords):
                return False

            # Check if a disallowed keyword is used
            # Also do not allow exec or eval statements
            if isinstance(node, ast.Call):
                is_disallowed_function_used = self._is_disallowed_function_used(
                    node, [*conditions.blacklisted_functions, "exec", "eval"]
                )
                if is_disallowed_function_used:
                    return False

            # Check if a disallowed import is used
            if isinstance(node, ast.Call | ast.Import | ast.ImportFrom):
                is_disallowed_import_used = self._is_disallowed_import_used(
                    node, conditions.blacklisted_packages
                )
                if is_disallowed_import_used:
                    return False

        return True

    @staticmethod
    def _import_module_from_file(name: str, filepath: str | os.PathLike) -> None:
        """
        Import a file as a module.

        :param name: Name of the module to import as.
        :param filepath: Path to the file.
        """
        spec = importlib.util.spec_from_file_location(name, filepath)
        spec.loader = importlib.util.LazyLoader(spec.loader)
        module = importlib.util.module_from_spec(spec)
        # NOTE: the use of LazyLoader means any syntax error will not be raised until
        # module elements are accessed
        spec.loader.exec_module(module)
        return module

    def _mark_test_case(
        self,
        function: Callable,
        test_case: TestCase,
        *,
        time_limit: float = FUNCTION_RUNTIME_LIMIT,
    ) -> TestCaseOutput:
        """
        Mark a function on a test case.

        :param function: The function to test.
        :param test_case: The test case to test the function on.
        :param time_limit: The time limit in seconds for the function
            to finish running (default: 30)
        :return: The output of the test case.
        """
        args = test_case.input_args
        kwargs = test_case.input_kwargs

        try:
            output = func_timeout(time_limit, function, args=args, kwargs=kwargs)
        except Exception as exc:  # noqa: BLE001
            return TestCaseOutput(Result.FAILED, message=exc, exception=True)

        if self._values_match(test_case.expected_output, output):
            # record time only if passed
            iterations, timing = timeit.Timer(
                lambda: func_timeout(time_limit, function, args=args, kwargs=kwargs)
            ).autorange()

            runtime = timing / iterations
            return TestCaseOutput(Result.PASSED, output=output, runtime=runtime)

        # Test case failed
        return TestCaseOutput(Result.FAILED, output=output, message="Test case failed")

    def mark(
        self,
        question: Question,
        filepath: str | os.PathLike,
        *,
        time_limit: float = FUNCTION_RUNTIME_LIMIT,
    ) -> Results:
        """
        Mark a question and the code file that solves it.

        The number of points return is based on the correctness of the solution and
        if there are any potential bonus points available. Zero points means at least
        one test case failed, one point means all test cases passed but no bonus was
        obtained.

        :param question: The question to mark.
        :param filepath: The code file to that contains the solution to the question.
        :param time_limit: The time limit in seconds for the function
            to finish running (default: 30)
        :return: A 4-tuple of a list of test case outputs, the bonus conditions
            output, the number of points, and the runtime (if all tests pass).
        """
        with self.set_recursion_depth(100):
            solution = self._import_module_from_file("solution", filepath)

            try:
                func = solution.Solution
            except Exception as exc:  # noqa: BLE001
                test_case_results = [
                    TestCaseOutput(Result.FAILED, message=exc, exception=True)
                    for test_case in question.test_cases
                ]
            else:
                test_case_results = [
                    self._mark_test_case(func, test_case, time_limit=time_limit)
                    for test_case in question.test_cases
                ]

            runtime = sum(
                result.runtime
                for result in test_case_results
                if result.result != Result.FAILED
            )

            # Award zero points if any test case failed
            if any(
                test_result.result == Result.FAILED for test_result in test_case_results
            ):
                return Results(test_case_results, BonusResult.NA, 0, 0)
            # Award one point if no additional bonus conditions
            if question.bonus is None:
                return Results(test_case_results, BonusResult.NA, 1, runtime)
            # Award one point plus bonus if bonus conditions met
            syntax_tree = self._parse_syntax_tree(
                filepath, Path(filepath).read_text(encoding="utf-8")
            )
            if self._obeys_bonus_conditions(syntax_tree, question.bonus.conditions):
                return Results(
                    test_case_results,
                    BonusResult.PASSED,
                    1 + question.bonus.bonus_points,
                    runtime,
                )
            # Award one point if bonus conditions not met
            return Results(test_case_results, BonusResult.FAILED, 1, runtime)

    @staticmethod
    @contextlib.contextmanager
    def set_recursion_depth(depth: int) -> Generator[None, None, None]:
        """
        Set the recursion depth limit for a function.

        :param depth: The recursion depth limit.
        """
        old_depth = sys.getrecursionlimit()
        sys.setrecursionlimit(depth + len(inspect.stack(0)))
        yield
        sys.setrecursionlimit(old_depth)
