#### Update 06/18/2016: New Documentation and Tutorial Coming Soon!

# Mosaic

Mosaic is a cross-platform, timing-accurate record and replay tool for
Android-based mobile devices. Mosaic enables cross-platform record and replay
through a novel virtual screen abstraction. User interactions are translated from
a physical device into a platform-agnostic intermediate representation before
translation to a target system. The intermediate representation is human-readable,
which allows Mosaic users to modify previously recorded traces or even synthesize
their own user interactive sessions from scratch.

# Requirements

1. Python 2.7
    1. argparse (`pip install argparse`)
    2. enum34 (`pip install enum34`)
2. Android Debugger (ADB)

# Convenience Scripts

Although Mosaic is a Python-based command line tool, we provide the following
bash wrappers for conveince operations:

1. Calibrate sourcea nd target devices:
    `./calibrate.sh <SOURCE-NAME>`
    `./calibrate.sh <TARGET-NAME>`
2. Record applicaton use case:
    `./calibrate.sh <APP-NAME> <SOURCE-NAME>`
3. Virtualize application use case:
    `./virtualize.sh <APP-NAME> <SOURCE-NAME>`
4. Translation application use case:
    `./translate.sh <APP-NAME> <SOURCE-NAME> <TARGET-NAME>`
4. Replay application use case:
    `./run.sh <APP-NAME> <SOURCE-NAME> <TARGET-NAME>`
