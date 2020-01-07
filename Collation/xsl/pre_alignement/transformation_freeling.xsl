<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">

    <xsl:param name="sortie"/>
    <xsl:output method="text"/>
    <xsl:strip-space elements="*"/>


    <xsl:template match="tei:TEI">
        <xsl:result-document href="{$sortie}">
            <xsl:apply-templates select="descendant::tei:text"/>
        </xsl:result-document>
    </xsl:template>
    
    <!--

    <xsl:template match="tei:TEI">
        <xsl:result-document href="../temoins_tokenises_regularises/txt/{@xml:id}.txt">
            <xsl:apply-templates select="descendant::tei:text"/>
        </xsl:result-document>
    </xsl:template>-->

    <xsl:template match="tei:teiHeader | tei:fw | tei:note | tei:del"/>

    <xsl:template match="tei:w">
        <xsl:value-of select="."/>
        <xsl:text>&#xA;</xsl:text>
    </xsl:template>

    <xsl:template match="tei:pc[text() != '.']">
        <xsl:value-of select="."/>
        <xsl:text>&#xA;</xsl:text>
    </xsl:template>

    <xsl:template match="tei:pc[text() = '.']">
        <xsl:value-of select="."/>
        <xsl:text>&#xA;&#xA;</xsl:text>
    </xsl:template>
</xsl:stylesheet>
