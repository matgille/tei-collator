<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <!--Idée ici: aligner les item de même position. -->

    <xsl:template match="/">
        <xsl:element name="texte">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="//table/item[1]/item">
        <xsl:variable name="position"
            select="count(preceding::item[parent::item[not(parent::item)]]) + 1"/>
        <xsl:copy-of select="."/>
        <xsl:copy-of select="//table/item[position()>1]/item"></xsl:copy-of>
    </xsl:template>

</xsl:stylesheet>
