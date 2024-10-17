import numpy as np
import pandas as pd

from question import Question, TestCase

examples = [
    question0 := Question(0),
    question1 := Question(1),
    question2 := Question(2),
    question3 := Question(3),
    question4 := Question(4),
    question5 := Question(5),
    question6 := Question(6),
    question7 := Question(7),
    question8 := Question(8),
    question9 := Question(9),
    question10 := Question(10),
    question11 := Question(11),
    question12 := Question(12),
    question13 := Question(13),
    question14 := Question(14),
]

_question0_test_cases = (
    TestCase(input_args=("Hello world",), expected_output="dlrow olleH"),
)

for test_case in _question0_test_cases:
    question0.add_test_case(test_case)

_question1_test_cases = (TestCase(input_args=("Password1234",), expected_output=True),)

for test_case in _question1_test_cases:
    question1.add_test_case(test_case)

_question2_test_cases = (TestCase(input_args=("Password1234",), expected_output=True),)

for test_case in _question2_test_cases:
    question2.add_test_case(test_case)

_question3_test_cases = (
    TestCase(
        input_args=(np.array([0, -32, 2.5, 5.6, -40, -1.25]),),
        expected_output=np.array([32, -25.6, 36.5, 42.08, -40, 29.75]),
    ),
)

for test_case in _question3_test_cases:
    question3.add_test_case(test_case)

_question4_test_cases = (
    TestCase(
        input_args=(
            pd.DataFrame(
                {
                    "id": [1, 2, 3, 4],
                    "fname": ["Demarcus", "Jeff", "Jacob", "Joe"],
                    "lname": ["Rabiot", "Chang", "Danlon", "Flagstaff"],
                }
            ),
            pd.DataFrame(
                {
                    "id": [1, 2, 3, 4],
                    "studentid": [4, 3, 2, 1],
                    "score": [75, 94, 13, 53],
                }
            ),
        ),
        expected_output=pd.DataFrame(
            {
                "first_name": ["Jacob", "Joe", "Demarcus"],
                "last_name": ["Danlon", "Flagstaff", "Rabiot"],
                "score": [94, 75, 53],
            }
        ),
    ),
)

for test_case in _question4_test_cases:
    question4.add_test_case(test_case)

_question5_test_cases = (TestCase(input_args=(24,), expected_output=4),)

for test_case in _question5_test_cases:
    question5.add_test_case(test_case)

_question6_test_cases = (
    TestCase(input_args=("3:00 AM", "9:00 AM"), expected_output=6),
    TestCase(input_args=("2:00 PM", "4:00 PM"), expected_output=2),
    TestCase(input_args=("1:00 AM", "3:00 PM"), expected_output=14),
)

for test_case in _question6_test_cases:
    question6.add_test_case(test_case)

_question7_test_cases = (
    TestCase(input_args=(1,), expected_output=True),
    TestCase(input_args=(13,), expected_output=False),
    TestCase(input_args=(720,), expected_output=True),
)

for test_case in _question7_test_cases:
    question7.add_test_case(test_case)

_question8_test_cases = (
    TestCase(
        input_args=([(0, 0), (1, 1), (0, 5), (15, 0)], 0, 0, 5), expected_output=3
    ),
)

for test_case in _question8_test_cases:
    question8.add_test_case(test_case)

_question9_test_cases = (
    TestCase(input_args=(123,), expected_output=321),
    TestCase(input_args=(-4629,), expected_output=-9264),
    TestCase(input_args=(1000,), expected_output=1),
    TestCase(input_args=(2**31,), expected_output=0),
)

for test_case in _question9_test_cases:
    question9.add_test_case(test_case)


_question10_test_cases = (
    TestCase(
        input_args=(
            [
                ["Bread", "Eggs", "Milk"],
                ["Cereal", "Milk"],
                ["Bread", "Milk"],
                ["Wine", "Eggs"],
            ],
        ),
        expected_output=("Bread", "Milk"),
    ),
)

for test_case in _question10_test_cases:
    question10.add_test_case(test_case)

_question11_test_cases = (
    TestCase(input_args=(3,), expected_output=2),
    TestCase(input_args=(17,), expected_output=1597),
    TestCase(input_args=(-5,), expected_output=-1),
)

for test_case in _question11_test_cases:
    question11.add_test_case(test_case)

_question12_test_cases = (
    TestCase(
        input_args=(
            [
                -1.315958,
                -7.563353,
                -5.269449,
                -2.689798,
                1.64862,
                -1.229754,
                1.30937,
                -4.340184,
                0.4519081,
                -0.8255139,
            ],
            [
                -2.788446,
                -11.68663,
                -2.574175,
                9.553144,
                10.28382,
                -4.568493,
                3.014083,
                1.387986,
                10.37869,
                7.203864,
            ],
        ),
        expected_output=0.6956863,
    ),
)

for test_case in _question12_test_cases:
    question12.add_test_case(test_case)

_question13_test_cases = (
    TestCase(
        input_args=((lambda x: 2 * x - 4), 5, 0.1, 100),
        expected_output=2.0000000006111107,
    ),
)

for test_case in _question13_test_cases:
    question13.add_test_case(test_case)

_question14_test_cases = (
    TestCase(
        input_args=(
            [[5.1, 3.5], [4.9, 3.0], [4.7, 3.2], [4.6, 3.1], [5.0, 3.6]],
            [40.6676, 38.3504, 37.8056, 37.0268, 40.3952],
        ),
        expected_output=[5.000, 5.256, 2.532],
    ),
)

for test_case in _question14_test_cases:
    question14.add_test_case(test_case)
