<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" xmlns:tei="http://www.tei-c.org/ns/1.0">
    <sch:ns uri="http://www.tei-c.org/ns/1.0" prefix="tei"/>
    <sch:pattern>
        <sch:title>Notes</sch:title>
        <sch:rule context="tei:note[ancestor::tei:body][ancestor::tei:TEI[@type = 'transcription']]">
            <sch:assert role="fatal" test="@type">Les notes doivent être typée</sch:assert>
        </sch:rule>
    </sch:pattern>
    <!--<sch:pattern>
        <sch:title>Head</sch:title>
        <sch:rule context="tei:head">
            <sch:assert role="fatal" test="@n">Les tei:head doivent être identifiés avec un
                @n</sch:assert>
        </sch:rule>
    </sch:pattern>-->
    <sch:pattern>
        <sch:title>tei w header</sch:title>
        <sch:rule context="tei:w">
            <sch:assert role="fatal" test="not(ancestor::tei:teiHeader)">Pas de balise tei:w dans le
                tei:header !</sch:assert>
            <sch:assert test="not(descendant::tei:w)" role="fatal">Interdit d'enchâsser deux tei:w
                !</sch:assert>
             <sch:assert role="fatal" test="not(ancestor::tei:add[@type='commentaire'])"
                          >Pas de tei:w dans une transcription de glose ou de commentaire!</sch:assert>
        </sch:rule>
    </sch:pattern>
</sch:schema>
