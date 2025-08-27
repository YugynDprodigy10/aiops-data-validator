from valmods.csv_validator import CSVValidator

def test_csv_validator_good_bad():
    v = CSVValidator("schemas/csv.schema.yaml")
    assert v.validate("examples/good.csv") == []
    assert len(v.validate("examples/bad.csv")) > 0
