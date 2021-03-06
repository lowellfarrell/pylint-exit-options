# pylint-exit-options

`pylint-exit-options` is a small command-line tool that can be used to re-process `pylint` exit codes or add quality thresholds.  
The tool can parse the bit-encoded exit code and allow you to customize which issue types will equate to a non-zero exit 
code.  Then a new exit code will be return that is a sum of the customized exit settings.  Additionally the tool can be used to trigger 
a non-zero exit code if the quality of the drops below a minimum value.  The goal is to add more exit code tuning capabilities to existing `pylint` feature set.

# Installation

You can manually install by downloading `pylint_exit_options.py`, and make it executable.

```bash
curl -o pylint-exit-options https://raw.githubusercontent.com/lowellfarrell/pylint-exit-options/master/pylint_exit_options.py && chmod +x pylint_exit_options.py
```

You should also consider creating a symbolic link so that the calls in the remainder of this
README work as described.  Update `<path-to>` with where you downloaded the script.

```bash
ln -s <path-to>/pylint_exit_options.py /usr/local/bin/pylint-exit-options
```

*Note: If you perform a `--user` install with `pip` then you will need to ensure `~/.local/bin` appears in your `PATH`
environment variable, otherwise the command line `pylint-exit-options` will not work.* 

# Usage
Replace calls to `pylint` with calls to `pylint-exit-options` and all pylint arguments and option will be passed to `pylint`
by `pylint-exit-options`.

```bash
pylint-exit-options mymodule.py
if [ $? -ne 0 ]; then
  echo "An error occurred while running pylint." >&2
  exit 1
fi
```
# Options
--exit-report <F,E,W,R,C,U>
    You can choose which issue codes are part of the exit code with this option using a comma delimited 
string. Acceptable values are : F[Fatal], E[Error], W[Warning], R[Re-factor], C[Convention], U[Usage]. 

usage: "-r=R" will report only Re-factor type error codes, "-r=R,C" will report only Re-factor and Convention 
type error codes. By default Fatal, Error, Warning and Usage type error codes are reported

--quality-gate <0.00 - 10.00>
If the final score is less than the threshold which defaults to 0, 64 will be added to the resulting exitcode.  `pylint` 
quality scores are between 0.00 to 10.00, 10.00 being the best.

# Examples
In this example pylint detects convention issue(s), and exits with a exit code of 16.  `pylint-exit-options` 
decodes this, lists the `pylint` issue message type, and exits with a new exit code. In this case the new exit code is 0.

```bash
> pylint-exit-options pylint-exit-options.py
pylint-exit-options.py:1:0: C0103: Module name "pylint-exit-options" doesn't conform to snake_case naming style (invalid-name)
pylint-exit-options.py:240: [R0914(too-many-locals), QualityCheck.check_quality] Too many local variables (16/15)

------------------------------------------------------------------
Your code has been rated at 9.89/10 (previous run: 9.89/10, +0.00)

The following types of issues were found:

  - re-factor message issued
  - convention message issued

Exiting gracefully...

> echo $?
0
```

In this example pylint detects re-factor an convention issue(s), and exits with a exit code of 24.  `pylint-exit-options` 
decodes this, lists the `pylint` issue message types, lists the message types that have non-zero issue cods for 
`pylint-exit-options` and exits with a new exit code. In this case the new exit code is 16.

```bash
> pylint-exit-options --exit-report=C pylint-exit-options.py
************* Module pylint-exit-options
pylint-exit-options.py:1:0: C0103: Module name "pylint-exit-options" doesn't conform to snake_case naming style (invalid-name)
pylint-exit-options.py:240: [R0914(too-many-locals), QualityCheck.check_quality] Too many local variables (16/15)

------------------------------------------------------------------
Your code has been rated at 9.89/10 (previous run: 9.89/10, +0.00)

The following types of issues were found:

  - re-factor message issued
  - convention message issued

The following types of issues are blocking:

  - convention message issued

Exiting due to issues...

> echo $?
16
```

In this example `pylint` rates the quality of the code as 9.89 out of 10.  Since we have set the minimum acceptable quality to 9.9, 
the `pylint-exit-options` will exit with a code of 64.

```bash
> pylint-exit-options --quality-gate=9.9 pylint-exit-options.py
************* Module pylint-exit-options
pylint-exit-options.py:1:0: C0103: Module name "pylint-exit-options" doesn't conform to snake_case naming style (invalid-name)

------------------------------------------------------------------
Your code has been rated at 9.89/10 (previous run: 9.89/10, +0.00)

The following types of issues were found:

  - convention message issued

The code quality is below the minimum accepable level

Exiting due to issues...

> echo $?
64
```

# Default pylint issue code conventions
`pylint` can return combinations of the following codes.  `pylint-exit-options` will identify each
issued message, and return the bit wise sum of the issue codes as a final exit code.

| Pylint code | Message | Final return code |
| ----------- | ------- | ----------------- |
| 1  | Fatal message issued | 1 |
| 2  | Error message issued | 2 |
| 4  | Warning message issued | 4 |
| 8  | Re-factor message issued | 0 |
| 16 | Convention message issued | 0 |
| 32 | Usage error | 32 |

# Exit Codes
The final exit code from `pylint-exit-options` will be a sumation of one or more of the following base codes.

| Exit code | Type |
| --------- | ---- |
| 0  | Good |
| 1  | Fatal |
| 2  | Error |
| 4  | Warning |
| 8  | Re-factor |
| 16 | Convention Violation |
| 32 | Usage error |
| 64 | Quality Violation |


# Credit
Forked from: https://github.com/jongracecox/pylint-exit and https://github.com/theunkn0wn1/pylint-exit
Inspiration from: https://github.com/marrink-lab/vermouth-martinize/blob/master/run_pylint.py

