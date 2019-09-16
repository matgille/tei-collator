<?xml version="1.0" encoding="UTF-8"?>
<!--Feuille XSL qui permet d'ajouter des id à tous les mots après les avoir tokenisés, dans un fichier qui pour l'instant ne concerne que le premier paragraphe du premier chapitre.-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs tei xf" version="3.0" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:xf="http://www.w3.org/2002/xforms" xmlns:uuid="java:java.util.UUID">
    <xsl:strip-space elements="*"/>

    <xsl:output doctype-system="Sal_J.dtd"/>


    <xsl:template match="/">
        <xsl:element name="xml">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <!--    <!-\-Conserver les commentaires pour ne pas perdre d'information-\->
    <xsl:template match="comment()">
        <xsl:comment><xsl:value-of select="."/></xsl:comment>
    </xsl:template>-->
    <xsl:template match="tei:teiHeader"/>
    <xsl:template match="tei:fw"/>
    <xsl:template match="tei:note"/>
    <xsl:template match="tei:lb"/>
    <xsl:template match="tei:facsimile"/>
    <xsl:template match="tei:orig"/>
    <xsl:template match="tei:abbr"/>
    <xsl:template match="tei:p[@n != 'Jl6hyqYStB']"/>
    <xsl:template match="tei:head[parent::tei:div[@type = 'partie']]"/>
    <xsl:template match="tei:div[@type = 'chapitre'][@n != '1']"/>
    <xsl:template match="tei:div[@type = 'seuil']"/>

    <xsl:template match="tei:w">
        <xsl:element name="w">
            <xsl:attribute name="xml:id">
                <xsl:value-of select="@xml:id"/>
            </xsl:attribute>
            <xsl:apply-templates/>
            <xsl:text> </xsl:text>
        </xsl:element>
    </xsl:template>


    <!--<!-\-
    <xsl:template match="tei:div[@type = 'chapitre'][@n != '1']"/>
-\->
    <xsl:template match="tei:choice">
        <xsl:value-of select="tei:reg"/>
        <xsl:value-of select="tei:expan"/>
    </xsl:template>-->


</xsl:stylesheet>
