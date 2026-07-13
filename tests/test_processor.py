import pandas as pd

from src.data import applications, data, output
from app.processor import Processor
from src.request import request


def test_get_data_matches_output():
    proc = Processor()
    result = proc.get_data(data.head(), applications.head(), request)
    pd.testing.assert_frame_equal(result, output)