<?xml version="1.0" encoding="UTF-8"?>
<!--Feuille XSL qui permet d'ajouter des id à tous les mots après les avoir tokenisés.-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs tei xf" version="3.0" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:xf="http://www.w3.org/2002/xforms" xmlns:uuid="java:java.util.UUID">
    <xsl:strip-space elements="*"/>
    <xsl:output doctype-system="Sal_J.dtd"/>


    <xsl:template match="/">
        <xsl:apply-templates _xpath-default-namespace="tei"/>
    </xsl:template>

    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>


    <!--    <!-\-Conserver les commentaires pour ne pas perdre d'information-\->
    <xsl:template match="comment()">
        <xsl:comment><xsl:value-of select="."/></xsl:comment>
    </xsl:template>-->
<!--problème de tokénisation: les virgules-->
    <xsl:template match="tei:text//text()[not(parent::tei:note)][ancestor::tei:div[@type = 'chapitre']]">
        <xsl:for-each select="tokenize(., '\s+')">
            <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:attribute name="xml:id"> <xsl:variable name="uuid" select="substring-before(uuid:randomUUID(), '-')"/>
                    a<xsl:value-of select="$uuid"/> </xsl:attribute>
                <xsl:value-of select="."/>
            </xsl:element>
        </xsl:for-each>
    </xsl:template>


</xsl:stylesheet>
