import re
import sys


def command_color(s):
    return f"\033[36m{s}\033[0m"


def makefile_docs():
    with open("Makefile", "r") as f:
        for line in f:
            if line.startswith("##"):
                docstring = line.strip("## ").rstrip()
                # get the make command immediately after a docstring
                command = "make " + re.match(r"^([a-z_-]+):", f.readline()).group(1)
                yield command, docstring


def print_makefile_docs(title):
    header = f"Makefile commands for {title}"
    print()
    print(header)
    print("-" * len(header))

    # print make command and docstring in two columns
    for cmd, doc in makefile_docs():
        print(f'{command_color(cmd):<35}{":":4}{doc:<12}')


if __name__ == "__main__":
    print_makefile_docs(title=sys.argv[1])
