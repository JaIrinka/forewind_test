import pandas as pd

from data import applications, data, output
from processor import Processor
from request import request


def test_get_data_matches_output():
    proc = Processor()
    result = proc.get_data(data.head(), applications.head(), request)
    pd.testing.assert_frame_equal(result, output)