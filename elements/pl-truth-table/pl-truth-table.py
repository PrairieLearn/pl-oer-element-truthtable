import random
import re
from enum import Enum
from typing import Any

import chevron
import lxml.html
import prairielearn as pl
from typing_extensions import assert_never

BIT_WIDTH_DEFAULT = "1"
CORRECT_ANSWER_DEFAULT = None
ALPHABET_DEFAULT = "10"
IS_MATERIAL_DEFAULT = False
LABEL_DEFAULT = None
PLACEHOLDER_DEFAULT = "?"
PREFILL_DEFAULT = ""
SHOW_HELP_TEXT_DEFAULT = True
SHOW_CELL_SCORE_DEFAULT = True
PARTIAL_CREDIT_DEFAULT = True
SHOW_COLUMN_SCORE_DEFAULT = False
CONSTANT_SIZE_DEFAULT = 0

TRUTH_TABLE_MUSTACHE_TEMPLATE_NAME = "pl-truth-table.mustache"


def prepare(element_html: str, data: pl.QuestionData) -> None:
    element = lxml.html.fragment_fromstring(element_html)
    required_attribs = ["answers-name", "input-name", "output-name"]
    optional_attribs = [
        "correct-answer",
        "label",
        "display",
        "prefill",
        "placeholder",
        "partial-credit",
        "is-material",
        "show-cell-score",
        "show-column-score",
        "bit-width",
        "alphabet",
        "constant-size"
    ]
    pl.check_attribs(element, required_attribs, optional_attribs)

    name = pl.get_string_attrib(element, "answers-name")
    pl.check_answers_names(data, name)

    output_name = pl.get_string_attrib(element, "output-name")  # [X or Y, X and Y]
    output_name = output_name.lstrip("[").rstrip("]").split(",")

    # prepare the input variables e.g. ['X', 'Y']
    variable_string = pl.get_string_attrib(element, "input-name")
    variables = variable_string.strip("[").strip("]").split(",")
    # check if different bitwidth is provided for each variable
    bit_width = pl.get_string_attrib(element, "bit-width", BIT_WIDTH_DEFAULT)
    num_rows = 1
    if "," in bit_width:
        bit_width = bit_width.lstrip("[").rstrip("]").split(",")
        for x in bit_width:
            num_rows *= 2 ** int(x)
    else:
        num_rows = 2 ** (
            int(bit_width) * len(variables)
        )  # Total rows in the truth table based on the number of variables and bit width

    # Just to test that the number is an integer > 0
    constant_size = int(pl.get_string_attrib(element, "constant-size", CONSTANT_SIZE_DEFAULT))
    if constant_size < 0:
        raise ValueError(
            f"The constant size for inputs must 0 or greater."
        )

    # Get the single correct-answer string from the HTML and split it for each row
    output_string = None
    if ("correct_answers" in data and name in data["correct_answers"]):
        output_string = data["correct_answers"][name]
    else:
        output_string = pl.get_string_attrib(
        element, "correct-answer", CORRECT_ANSWER_DEFAULT
    )
    if output_string is None:
        raise ValueError(
                f"data[\"correct_answers\"][{name}] not declared in server.py. Alternatively, fill out element attribute \"correct-answer\""
            )

    output_list = (
        re.split(r"\],\s+\[", output_string) if output_string is not None else None
    )
    # check if the number of output lists is equal to the number of output names
    if output_list is not None:
        if len(output_list) != len(output_name):
            raise ValueError(
                f"The number of output lists ({len(output_list)}) must match the number of output names ({len(output_name)})."
            )
    for k, output in enumerate(output_list):
        output = output.lstrip("[").rstrip("]").replace(" ", "").split(",")
        if output is not None:
            if len(output) != num_rows:
                raise ValueError(
                    f"The length of the correct answer ({len(output)}) must match the number of rows ({num_rows})."
                )
            # check if the value is in the alphabet
            alphabet = pl.get_string_attrib(
                element, "alphabet", ALPHABET_DEFAULT
            )
            char_level_set = {char for item in set(output) for char in item}
            if not char_level_set.issubset(set(alphabet)):
                raise ValueError(
                    f"Invalid format. Provided output {char_level_set} not in alphabet {set(alphabet)}."
                )
            width = len(output[0])
            # Split the correct_answer into individual answers for each row
            for row_index in range(num_rows):
                if len(output[row_index]) != width:
                    raise ValueError(
                        f"The bit-width inside correct answer list {k} is not consistent. Please check."
                    )
                data["correct_answers"][f"{name}_{row_index}_{k}"] = output[row_index]

def render(element_html: str, data: pl.QuestionData) -> str:
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, "answers-name")
    label = pl.get_string_attrib(element, "label", LABEL_DEFAULT)
    # Get the output name
    output_name = pl.get_string_attrib(element, "output-name")  # [X or Y, X and Y]
    output_name = output_name.lstrip("[").rstrip("]").split(",")
    for o_name in output_name:
        o_name = o_name.lstrip("").rstrip("")
    num_output = len(output_name)

    # Determine if the question is material (informational) or requires input
    is_material = pl.get_boolean_attrib(
        element, "is-material", False
    )  # Default to False if not specified
    placeholder = pl.get_string_attrib(element, "placeholder", PLACEHOLDER_DEFAULT)
    placeholder_l = []
    for k in range(num_output):
        placeholder_l.append(placeholder * len(data["correct_answers"][f"{name}_0_{k}"]))
    prefill = pl.get_string_attrib(element, "prefill", PREFILL_DEFAULT)
    show_cell_score = pl.get_boolean_attrib(element, "show-cell-score", SHOW_CELL_SCORE_DEFAULT)
    partial_credit = pl.get_boolean_attrib(
        element, "partial-credit", PARTIAL_CREDIT_DEFAULT
    )
    show_column_score = pl.get_boolean_attrib(element, "show-column-score", SHOW_COLUMN_SCORE_DEFAULT)
    constant_size = int(pl.get_string_attrib(element, "constant-size", CONSTANT_SIZE_DEFAULT))

    score = data["partial_scores"].get(name, {"score": None}).get("score", None)
    if score is not None:
        score = float(score) * 100
    ac = score == 100
    aw = score == 0

    # prepare the input variables e.g. ['X', 'Y']
    variable_string = pl.get_string_attrib(element, "input-name")
    variables = variable_string.strip("[").strip("]").split(",")

    # Generate table data
    var_lenth = len(variables)
    # check if different bitwidth is provided for each variable
    bit_width = pl.get_string_attrib(element, "bit-width", BIT_WIDTH_DEFAULT)
    num_rows = 1
    if "," in bit_width:
        bit_width_list = bit_width.lstrip("[").rstrip("]").split(",")
        for x in bit_width_list:
            num_rows *= 2 ** int(x)
    else:
        num_rows = 2 ** (
            int(bit_width) * var_lenth
        )  # Total rows in the truth table based on the number of variables and bit width
    columns = [{"name": c} for c in variables]
    rows = []
    for i in range(num_rows):
        row = {
            "input": [],
            "row_index": i,
            "name": name,
            "is_first_row": i == 0,
            "output": [],
        }
        if "," in bit_width:
            max_values = [2 ** int(w) for w in bit_width_list]
            counts = []
            rem = i
            # Convert the count into counts for each bitwidth
            for mv in reversed(max_values):
                counts.append(rem % mv)
                rem //= mv
            counts.reverse()
            # Generate the binary strings for the current counts
            row["input"] = [format(counts[i], f'0{int(bit_width_list[i])}b') for i in range(len(bit_width_list))]
        else:
            for j in range(var_lenth):
                # Calculate the bit position for the j-th variable
                bit_position = (var_lenth - j - 1) * int(bit_width)
                # Extract bit_width bits for the j-th variable from the row index
                # Shift right to bring the desired bits to the least significant position
                # Then apply a mask to extract exactly k bits
                bits = (i >> bit_position) & ((1 << int(bit_width)) - 1)
                # Format the bits as a binary string with leading zeros to ensure k bits
                bit_str = format(bits, f"0{bit_width}b")
                row["input"].append(bit_str)
        alphabet = pl.get_string_attrib(
                        element, "alphabet", ALPHABET_DEFAULT
                    )
        row["input"] = [i.replace("1", alphabet[0]) for i in row["input"]]
        row["input"] = [i.replace("0", alphabet[1]) for i in row["input"]]
        for k in range(num_output):
            size = constant_size or len(placeholder_l[k])
            output = {
                "cell_name": f"{name}_{i}_{k}",
                "output_index": k,
                "sub": data["submitted_answers"].get(f"{name}_{i}_{k}", prefill * len(data["correct_answers"][f"{name}_{i}_{k}"])),
                "correct": False,
                "incorrect": False,
                "input_error": data["format_errors"].get(f"{name}_{i}_{k}", None),
                "output_value": data["correct_answers"].get(
                    f"{name}_{i}_{k}", CORRECT_ANSWER_DEFAULT
                ),
                "placeholder": placeholder_l[k],
                "width": 16 + 8 * size
            }
            row["output"].append(output)
        rows.append(row)

    col_percentage_updated = False
    # stores column accuracies
    column_data = []
    raw_column_scores = [0.0] * num_output

    for index in range(num_rows):
        for k in range(num_output):
            answer_name = f"{name}_{index}_{k}"
            partial_score = (
                data["partial_scores"]
                .get(answer_name, {"score": None})
                .get("score", None)
            )
            if partial_score is not None:
                try:
                    col_percentage_updated = True
                    partial_score = float(partial_score)
                    if partial_score >= 1:
                        rows[index]["output"][k]["correct"] = True
                        raw_column_scores[k] += 1
                    else:
                        rows[index]["output"][k]["incorrect"] = True
                except Exception as e:
                    raise ValueError("invalid score" + partial_score) from e
                
    try: 
        for i in range(len(raw_column_scores)):
            col = {
                "name" : output_name[i],
                "percentage" : (raw_column_scores[i] / num_rows) * 100,
            }
            column_data.append(col)
    except Exception as e:
        raise ValueError("invalid column scores - " + raw_column_scores) from e

    # Get template
    with open(TRUTH_TABLE_MUSTACHE_TEMPLATE_NAME, "r", encoding="utf-8") as f:
        template = f.read()
    if data["panel"] == "question":
        grading_text = ""
        if partial_credit:
            if show_cell_score:
                grading_text = "You will receive partial credit per correct cell, and feedback which cells are filled out correctly"  
            elif show_column_score:
                grading_text = "You will receive partial credit per correct cell, and feedback to which degree each column is filled out correctly" 
            else:
                grading_text = "You will receive partial credit per correct cell, but no feedback which cells are filled out correctly" 
        else:
            if show_cell_score:
                grading_text = "You will not receive partial credit unless the entire table is filled correctly, but feedback on which cells are correct."  
            elif show_column_score:
                grading_text = "You will not receive partial credit unless the entire table is filled correctly, but feedback to which degree each column is filled out correctly." 
            else:
                grading_text = "You will not receive partial credit or feedback unless the entire table is filled correctly."

        info_params = {
            "format": True,
            "bitwidth": bit_width,
            "grading_text": grading_text,
            "alphabet": ', '.join(
                set(
                    pl.get_string_attrib(
                        element, "alphabet", ALPHABET_DEFAULT
                    )
                )
            ),
        }
        info = chevron.render(template, info_params).strip()
        html_params = {
            "question": True,
            "name": name,
            "output_name": output_name,
            "label": label,
            "info": info,
            "uuid": pl.get_uuid(),
            "columns": columns,
            "rows": rows,
            "num_rows": num_rows,
            "is_material": is_material,
            "show_cell_score": show_cell_score,
            "show_column_score": show_column_score,
            "column_data":column_data,
            "col_percentage_updated": col_percentage_updated,
            "score": score,
            "all_correct": ac,
            "all_incorrect": aw,
        }
        return chevron.render(template, html_params).strip()
    elif data["panel"] == "submission":
        html_params = {
            "submission": True,
            "name": name,
            "output_name": output_name,
            "label": label,
            "uuid": pl.get_uuid(),
            "columns": columns,
            "rows": rows,
            "num_rows": num_rows,
            "is_material": is_material,
            "show_cell_score": show_cell_score,
            "show_column_score": show_column_score,
            "column_data":column_data,
            "col_percentage_updated": col_percentage_updated,
            "score": score,
            "all_correct": ac,
            "all_incorrect": aw,
        }
        for index in range(num_rows):
            for k in range(num_output):
                # Construct the indexed name (e.g., answers-name_0, answers-name_1, ...)
                answer_name = f"{name}_{index}_{k}"
                parse_error = data["format_errors"].get(answer_name, None)
                if parse_error is None and answer_name in data["submitted_answers"]:
                    # Get submitted answer, raising an exception if it does not exist
                    a_sub = data["submitted_answers"].get(answer_name, None)
                    if a_sub is None:
                        raise Exception("submitted answer is None")
                    # If answer is in a format generated by pl.to_json, convert it
                    # back to a standard type (otherwise, do nothing)
                    a_sub = pl.from_json(a_sub)
                    a_sub = pl.escape_unicode_string(a_sub)
                    html_params["a_sub"] = a_sub
                elif answer_name not in data["submitted_answers"]:
                    data["format_errors"][answer_name] = "No submitted answer."
                    html_params["parse_error"] = None
        if partial_credit and score is not None:
            score_type, score_value = pl.determine_score_params(score)
            html_params[score_type] = score_value
        return chevron.render(template, html_params).strip()
    elif data["panel"] == "answer":
        html_params = {
            "answer": True,
            "name": name,
            "output_name": output_name,
            "label": label,
            "columns": columns,
            "rows": rows,
        }
        return chevron.render(template, html_params).strip()

def parse(element_html: str, data: pl.QuestionData) -> None:
    element = lxml.html.fragment_fromstring(element_html)
    name = pl.get_string_attrib(element, "answers-name")
    # Get the output name
    output_name = pl.get_string_attrib(element, "output-name")  # [X or Y, X and Y]
    output_name = output_name.lstrip("[").rstrip("]").split(",")
    for o_name in output_name:
        o_name = o_name.lstrip("").rstrip("")
    num_output = len(output_name)

    # Check if the question is marked as material (informational)
    is_material = pl.get_boolean_attrib(element, "is-material", False)
    # If it's material, skip grading
    if is_material:
        return
    
    # prepare the input variables e.g. ['X', 'Y']
    variable_string = pl.get_string_attrib(element, "input-name")
    variables = variable_string.strip("[").strip("]").split(",")

    # check if different bitwidth is provided for each variable
    bit_width = pl.get_string_attrib(element, "bit-width", BIT_WIDTH_DEFAULT)
    num_rows = 1
    if "," in bit_width:
        bit_width_l = bit_width.lstrip("[").rstrip("]").split(",")
        for x in bit_width_l:
            num_rows *= 2 ** int(x)
    else:
        num_rows = 2 ** (
            int(bit_width) * len(variables)
        )  # Total rows in the truth table based on the number of variables and bit width
        
    alphabet = pl.get_string_attrib(
        element, "alphabet", ALPHABET_DEFAULT
    )

    # Loop through each row to capture submitted answers
    for row_index in range(num_rows):
        for k in range(num_output):
            answer_name = f"{name}_{row_index}_{k}"
            a_sub = data["submitted_answers"].get(answer_name, None)
            expected_len = len(data["correct_answers"][answer_name])
            if a_sub is None:
                data["format_errors"][answer_name] = "No submitted answer."
                data["submitted_answers"][answer_name] = None
                continue
            if not a_sub:
                data["format_errors"][
                    answer_name
                ] = "Invalid format. The submitted answer was left blank."
                data["submitted_answers"][answer_name] = None
            elif len(a_sub) != expected_len:
                data["format_errors"][
                    answer_name
                ] = f"Invalid format. The submitted answer must be {expected_len} bit(s) long."
                data["submitted_answers"][answer_name] = pl.to_json(a_sub)
            elif not set(a_sub.lower()).issubset(set(alphabet.lower())):
                alphabet_print = ",".join(set(alphabet))
                data["format_errors"][
                    answer_name
                ] = f"Invalid format. Input not in alphabet ({alphabet_print})."
                data["submitted_answers"][answer_name] = pl.to_json(a_sub)
            else:
                # Store the submitted answer for this row
                data["submitted_answers"][answer_name] = pl.to_json(a_sub)

def grade(element_html: str, data: pl.QuestionData) -> None:
    element = lxml.html.fragment_fromstring(element_html)

    # Check if the question is marked as material (informational)
    is_material = pl.get_boolean_attrib(element, "is-material", False)
    # If it's material, skip grading
    if is_material:
        return

    name = pl.get_string_attrib(element, "answers-name")
    # prepare the input variables e.g. ['X', 'Y']
    variable_string = pl.get_string_attrib(element, "input-name")
    variables = variable_string.strip("[").strip("]").split(",")
    # check if different bitwidth is provided for each variable
    bit_width = pl.get_string_attrib(element, "bit-width", BIT_WIDTH_DEFAULT)
    num_rows = 1
    if "," in bit_width:
        bit_width = bit_width.lstrip("[").rstrip("]").split(",")
        for x in bit_width:
            num_rows *= 2 ** int(x)
    else:
        num_rows = 2 ** (
            int(bit_width) * len(variables)
        )  # Total rows in the truth table based on the number of variables and bit width
    # Get the output name
    output_name = pl.get_string_attrib(element, "output-name")  # [X or Y, X and Y]
    output_name = output_name.lstrip("[").rstrip("]").split(",")
    for o_name in output_name:
        o_name = o_name.lstrip("").rstrip("")
    num_output = len(output_name)

    partial_credit = pl.get_boolean_attrib(
        element, "partial-credit", PARTIAL_CREDIT_DEFAULT
    )

    is_incorrect = False
    score_sum = 0
    for index in range(num_rows):
        for k in range(num_output):
            answer_name = f"{name}_{index}_{k}"
            # Get the correct answer for each row
            a_tru = pl.from_json(data["correct_answers"].get(answer_name, None))
            if a_tru is None:
                break
            if answer_name in data["submitted_answers"]:
                if data["submitted_answers"][answer_name].lower() == a_tru.lower():
                    data["partial_scores"][answer_name] = {
                        "score": 1,
                        "feedback": "Correct.",
                    }
                    score_sum += 1
                else:
                    data["partial_scores"][answer_name] = {
                        "score": 0,
                        "feedback": "Incorrect.",
                    }
                    if not partial_credit:
                        is_incorrect = True
            else:
                data["partial_scores"][answer_name] = {
                    "score": 0,
                    "feedback": "Missing input.",
                }
                if not partial_credit:
                    is_incorrect = True

    if not partial_credit and is_incorrect:
        # assign the score to all the answers
        score_sum = 0
        for index in range(num_rows):
            for k in range(num_output):
                answer_name = f"{name}_{index}_{k}"
                a_tru = pl.from_json(data["correct_answers"].get(answer_name, None))
                if a_tru is None:
                    break
                data["partial_scores"][answer_name]["weight"] = 0.0

    data["partial_scores"][name] = {"score": score_sum / (num_rows * num_output)}


def test(element_html: str, data: pl.ElementTestData) -> None:
    return
