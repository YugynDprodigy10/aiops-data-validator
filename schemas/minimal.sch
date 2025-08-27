<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron">
  <sch:pattern id="non-empty-title">
    <sch:rule context="/Product">
      <sch:assert test="normalize-space(Title) != ''">Title must not be empty.</sch:assert>
    </sch:rule>
  </sch:pattern>
</sch:schema>
