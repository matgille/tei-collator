<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
    <sch:ns uri="http://www.tei-c.org/ns/1.0" prefix="tei"/>
    <sch:pattern>
        <sch:title>tei w header</sch:title>
        <sch:rule context="tei:w">
            <sch:assert role="fatal"
                test="not(ancestor::tei:teiHeader)">Pas de
                balise tei:w dans le tei:header
                !</sch:assert>
            <sch:assert test="not(descendant::tei:w)"
                role="fatal">Interdit d'enchâsser deux tei:w
                !</sch:assert>
            <!--<sch:assert role="warning"
                test="not(contains(string-join(text()), ' '))"
                >Pas d'espace dans un tei:w !</sch:assert>-->
        </sch:rule>
    </sch:pattern>
</sch:schema>