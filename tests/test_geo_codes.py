import pytest

from app.domain.campaign import GeoCodes
from app.domain.errors import InvalidGeoCodes


def test_parses_a_list_of_codes() -> None:
    assert GeoCodes.parse("MX,AU,RO").codes == ("MX", "AU", "RO")


def test_accepts_a_single_code() -> None:
    assert GeoCodes.parse("mx").codes == ("MX",)


def test_normalises_case_whitespace_and_duplicates() -> None:
    assert GeoCodes.parse(" mx , AU,mx ").codes == ("MX", "AU")


def test_ignores_empty_parts() -> None:
    assert GeoCodes.parse("MX,,AU,").codes == ("MX", "AU")


@pytest.mark.parametrize("raw", ["", " ", ",", " , "])
def test_rejects_input_without_codes(raw: str) -> None:
    with pytest.raises(InvalidGeoCodes, match="At least one"):
        GeoCodes.parse(raw)


@pytest.mark.parametrize("bad_code", ["MEX", "M", "M1", "12", "\u041c\u0425"])
def test_rejects_codes_that_are_not_two_ascii_letters(bad_code: str) -> None:
    with pytest.raises(InvalidGeoCodes, match=bad_code):
        GeoCodes.parse(f"AU,{bad_code}")


def test_lists_every_invalid_code_in_the_message() -> None:
    with pytest.raises(InvalidGeoCodes, match="MEX, 12"):
        GeoCodes.parse("AU,MEX,12")
