from valmods.xml_validator import XMLValidator

def test_xml_schematron_violation():
    v = XMLValidator("schemas/minimal.xsd", schematron_path="schemas/minimal.sch")
    issues = v.validate("examples/bad_schematron.xml")
    assert any(i.issue_type == "SCHEMATRON" for i in issues)
