<?xml version="1.0" encoding="UTF-8"?>
<!--Cette feuille régularise les éléments une fois tokénisés et xmlidsés-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">


    <xsl:strip-space elements="*"/>
    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>



    <xsl:template match="/">
        <xsl:for-each select="collection('../../temoins_tokenises?select=*.xml')//tei:TEI">
            <xsl:variable name="nom_fichier" select="@xml:id"/>
            <xsl:result-document href="../temoins_tokenises_regularises/{$nom_fichier}.xml">
                <xsl:element name="TEI" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="xml:id" select="$nom_fichier"/>
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:result-document>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="tei:hi">
        <xsl:value-of select="."/>
    </xsl:template>

    <xsl:template match="tei:choice">
        <xsl:apply-templates select="tei:reg"/>
        <xsl:apply-templates select="tei:expan"/>
        <xsl:apply-templates select="tei:corr"/>
    </xsl:template>


</xsl:stylesheet>