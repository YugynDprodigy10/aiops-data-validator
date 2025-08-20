
from validators.json_validator import JSONValidator
from validators.xml_validator import XMLValidator

def test_json_validator():
    schema = "schemas/sample.schema.json"
    file = "examples/bad_sample.json"
    v = JSONValidator(schema)
    issues = v.validate(file)
    assert len(issues) >= 2

def test_xml_validator():
    xsd = "schemas/minimal.xsd"
    file = "examples/bad_label.xml"
    v = XMLValidator(xsd_path=xsd)
    issues = v.validate(file)
    assert len(issues) >= 1
