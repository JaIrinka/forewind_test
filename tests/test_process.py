import pandas as pd

from app.process import build_result, load_b64_dataframe


def test_build_result_matches_output():
    result = build_result("src/data.b64", "src/applications.b64")
    output = load_b64_dataframe("src/output.b64")
    pd.testing.assert_frame_equal(result.head(), output)
