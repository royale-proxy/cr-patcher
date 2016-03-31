# coc-patcher

Run with:

    python3.5 patcher.py

## Installation

1. Install dependencies.
2. Fill in the `config.json` file.

    Note: The `keypass` and `dname` fields are only required to create a new keystore.  See [here](http://docs.oracle.com/javase/7/docs/technotes/tools/solaris/keytool.html#DName) for how to fill out the `dname` fields.

## Dependencies

Install `requests-cache` with:

    python3.5 -m pip install requests-cache