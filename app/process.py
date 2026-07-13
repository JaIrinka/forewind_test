import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import base64

import numpy as np
import pandas as pd

from app.processor import Processor
from src.request import request


def load_b64_dataframe(path):
    with open(path, "r") as text_file:
        encoded = text_file.read()
    return pd.DataFrame(eval(base64.b64decode(encoded)))


def build_result(data_path, application_path):
    data = load_b64_dataframe(data_path)
    applications = load_b64_dataframe(application_path)
    return Processor().get_data(data, applications, request)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run Processor.get_data over .b64-encoded data files")
    parser.add_argument("data", help="Path to a .b64 file encoding the data DataFrame (see src/data.b64)")
    parser.add_argument("application", help="Path to a .b64 file encoding the applications DataFrame (see src/applications.b64)")
    args = parser.parse_args(argv)
    result = build_result(args.data, args.application)
    print(result)


if __name__ == "__main__":
    main()