<?xml version="1.0" encoding="UTF-8"?>

<!--Tokénisation spéciale pour le témoin incunable.-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs tei" version="2.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:xf="http://www.w3.org/2002/xforms"
    xmlns:f="urn:stylesheet-func">
    <xsl:strip-space elements="*"/>
    <!--    <xsl:output doctype-system="Sal_J.dtd"/>-->




    <xsl:template match="/">
        <xsl:apply-templates xpath-default-namespace="tei"/>
    </xsl:template>

    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

  
    
    
    <xsl:template match="tei:choice">
        <xsl:value-of select="tei:reg"/>
        <xsl:value-of select="tei:expan"/>
        <xsl:value-of select="tei:corr"/>
    </xsl:template>


</xsl:stylesheet>
