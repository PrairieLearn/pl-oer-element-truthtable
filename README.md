# PrairieLearn OER Element: Truth Table

This element was developed by Pai Zheng and Yujie Miao. Please carefully test the element and understand its features and limitations before deploying it in a course. It is provided as-is and not officially maintained by PrairieLearn, so we can only provide limited support for any issues you encounter!

If you like this element, you can use it in your own PrairieLearn course by copying the contents of the `elements` folder into your own course repository. After syncing, the element can be used as illustrated by the example question that is also contained in this repository.


## `pl-truth-table` element

This element creates a truth table and can be used for both instructional materials and questions. Input columns are auto-generated to enumerate all boolean combinations. Output columns are supplied as an attribute (either to be displayed or to be used for grading student inputs). The table supports both partial and all-or-nothing grading, different input alphabets (e.g., 0/1 or T/F), and custom bit widths (e.g., "011" as a single output column).

### Example

<img src="example.png" width="300">

```html
<pl-truth-table
    answers-name="q1"
    input-name="[X, Y, Z]"
    output-name="X AND Y AND Z"
    correct-answer="[0,0,0,0,0,0,0,1]">
</pl-truth-table>
```

### Element Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `answers-name` | string (required) | Unique name for the element. |
| `input-name` | string (required) | Names of the input variables, displayed in the table header. For multiple input columns, wrap names in the style of an array (in square brakets and comma-seperated, e.g., `"[X, Y, Z]"`). Formatting via HTML is possible; commas in names can be escaped via `\,`. |
| `output-name` | string (required) | Names of the input variables, displayed in the table header. For multiple input columns, wrap names in the style of an array (in square brakets and comma-seperated, `"[X OR Y, X AND Y]"`). Formatting via HTML is possible; commas in names can be escaped via `\,`. |
| `bit-width` | string (default: `"1"`) | The number of bits for each input variable. Provide a single number to set a consistent bit width for all inputs. For different bit widths per column, wrap lengths in the style of an array (in square brakets and comma-seperated, `"[1,2]"`). |
| `correct-answer` | string (required, unless set via `data["correct_answers"]` in `server.py`) | Correct output values for the table. Wrap values in the style of an array (in square brakets and comma-seperated, e.g., `"[0, 1, 1, 1]"`). For multiple output columns, separate each column's values by a comma (e.g., `"[0, 1, 1, 1], [0, 0, 0, 1]"`). Outputs can have multiple bits as well (e.g., `"[00, 11]"`). The number of output columns must match the number of names provided in `output-name`, and the number of values per column must be 2^N for N input bits. |
| `is-material` | boolean (default: `false`) | If set to `true`, outputs are immediately displayed and the table is static, to be used as instructor-provided material. All of the remaining attributes only apply if `is-material` is set to `false`. |
| `partial-credit` | boolean (default: `true`) | If set to `true`, students receive partial credit based on the percentage of correctly filled cells. Otherwise, all-or-nothing grading is used. |
| `alphabet` | string (default: `"10"`) | The characters used in the truth table. Enter the character corresponding to true first, and then the one corresponding to false. Other legal output characters can be appended afterwards. For example, set `alphabet="TF"` to use T and F, or `alphabet="TFX"` to allow `X` to mark unknown outputs. Note that all `correct-answer` must use the alphabet defined here. |
| `placeholder` | string (default: `"?"`) | The placeholder shown for empty input boxes. |
| `prefill` | string (default: `""`) | A value prefilled for all input boxes (useful for large but sparsely filled tables). |
| `constant-size` | string (default: `"0"`) | If set to `"0"`, the size of text boxes automatically scales with the bit-width of the values set in `output-values`. To reveal less information about the expected size of the solutions, this attribute allows a constant size (number of expected characters) to be set for all outputs. |
| `show-cell-score` | boolean (default: `true`) | If set to `true`, students are shown a badge for each individual cell that tells them if their answer is correct. Otherwise, no cell-level feedback is provided. |
| `show-column-score` | boolean (default: `false`) | If set to `true`, students are shown a badge for each column that tells them the percentage of their answers in that column that is correct. Otherwise, no column-level feedback is provided. |
