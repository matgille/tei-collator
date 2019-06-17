<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math" exclude-result-prefixes="xs math"
    version="3.0">
    <xsl:output method="text"/>

    <xsl:template match="/">
        <xsl:text>{
        "witnesses" : [</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]
            }</xsl:text>
    </xsl:template>

    <xsl:template match="temoin">
        <xsl:text>{
    "id":"</xsl:text>
        <xsl:value-of select="@n"/>
        <xsl:text>",
        "tokens" : [</xsl:text>
        <xsl:for-each select="descendant::w[text()]">
            <xsl:text>{"t": "</xsl:text>
            <xsl:value-of select="."/>
            <xsl:text> " ,</xsl:text>
            <xsl:text>"xmlid" : "</xsl:text>
            <xsl:value-of select="@xml:id"/>
            <xsl:text>"}</xsl:text>
            <xsl:variable name="nom_temoin" select="ancestor::temoin/@n"/>
            <xsl:if test="following::w[ancestor::temoin/@n = $nom_temoin]">
                <xsl:text>,</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>]}</xsl:text>
        <xsl:if test="following::temoin">
            <xsl:text>,</xsl:text>
        </xsl:if>
    </xsl:template>

</xsl:stylesheet>
