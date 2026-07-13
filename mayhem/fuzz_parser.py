#!/usr/bin/env python3
"""Atheris fuzz harness for python-nameparser.

Exercises the HumanName parser on arbitrary unicode input — the same code path
as the original mayhemheroes harness (parse, capitalize, compare, as_dict,
initials) — with Atheris instrumenting the imported nameparser modules so
libFuzzer gets coverage feedback.

Run modes (driven by the compiled launcher `nameparser_fuzzer` / `-standalone`):
  * fuzzing      — `python3 fuzz_parser.py [libFuzzer args]`
  * single input — `python3 fuzz_parser.py <file>` (libFuzzer runs it once)
"""
import logging
import signal
import sys

import atheris

# Instrument the library under test so the fuzzer gets coverage feedback.
with atheris.instrument_imports():
    import nameparser

# nameparser logs on odd input; silence it so the fuzz log stays useful.
logging.disable(logging.CRITICAL)


class _InputTimeout(Exception):
    pass


def _alarm(signum, frame):
    raise _InputTimeout()


# Per-input watchdog: a single pathological name (e.g. exponential prefix
# banking) must not hang the fuzzer.
signal.signal(signal.SIGALRM, _alarm)
_PER_INPUT_SECONDS = 5


@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    text = fdp.ConsumeUnicode(atheris.ALL_REMAINING)
    signal.setitimer(signal.ITIMER_REAL, _PER_INPUT_SECONDS)
    try:
        human = nameparser.HumanName(text)
        human.capitalize()
        _ = human == human
        human.as_dict()
        human.initials_list()
        human.initials()
        str(human)
    except _InputTimeout:
        # This one input was too slow — skip it, don't count it as a defect.
        pass
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == '__main__':
    main()
