#!/usr/bin/python3
import atheris
import logging
import sys

with atheris.instrument_imports():
    import nameparser

# No logging
logging.disable(logging.CRITICAL)


@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)

    human = nameparser.HumanName(fdp.ConsumeUnicode(atheris.ALL_REMAINING))
    human.capitalize()
    is_eq = human == human
    human.as_dict()
    human.initials_list()
    human.initials()


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
