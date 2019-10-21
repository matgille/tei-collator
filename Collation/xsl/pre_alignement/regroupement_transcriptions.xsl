<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs tei" version="2.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:xf="http://www.w3.org/2002/xforms"
    xmlns:f="urn:stylesheet-func">

    <xsl:strip-space elements="*"/>

    <xsl:template match="/">
        <xsl:result-document href="../temoins_regroupes/groupe.xml">
            <xsl:element name="teiCorpus" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:for-each
                    select="collection('../../temoins_tokenises_regularises?select=*.xml')//tei:TEI">
                    <xsl:apply-templates/>
                </xsl:for-each>
            </xsl:element>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="tei:teiHeader | tei:facsimile | tei:pb | tei:cb | tei:note"/>
    <xsl:template match="tei:hi">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:text">
        <xsl:element name="text" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="xml:id" select="ancestor::tei:TEI/@xml:id"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>



    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
