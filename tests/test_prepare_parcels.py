from src.data.prepare_parcels import normalize_parcel_number


def test_normalize_parcel_number_accepts_ten_digits() -> None:
    assert normalize_parcel_number("1234567890") == "1234567890"
    assert normalize_parcel_number("123-456-7890") == "1234567890"


def test_normalize_parcel_number_rejects_nonstandard_values() -> None:
    assert normalize_parcel_number(None) is None
    assert normalize_parcel_number("") is None
    assert normalize_parcel_number("12345") is None
    assert normalize_parcel_number("1234567890,0987654321") is None
