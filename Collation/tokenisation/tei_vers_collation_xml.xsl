<?xml version="1.0" encoding="UTF-8"?>
<!--Première feuille de style pour collatex. Sort un fichier texte par document tei.-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:tex="placeholder.uri" exclude-result-prefixes="tex" version="2.0"
    xmlns:uuid="java:java.util.UUID">
    <xsl:output method="xml" omit-xml-declaration="no" indent="no" encoding="UTF-8"/>
 <xsl:strip-space elements="*"/> 

    <!--Crée des dossiers par paragraphe et par chapitre qui comportent les textes d'un même paragraphe. Suppose une régularité dans la structuration des textes-->
    <xsl:template match="/">
        <xsl:for-each select="descendant::tei:TEI[4]//tei:div[@type = 'chapitre'][not(@subtype)][@n = '1']">
            <xsl:variable name="n_chapitre" select="@n"/>
            <xsl:for-each select="//tei:TEI/descendant::tei:div[@type = 'chapitre'][@n = $n_chapitre]/tei:div/tei:p">
                <xsl:variable name="id" select="ancestor::tei:TEI/@xml:id"/>
                <xsl:variable name="n_par" select="@n"/>
                <xsl:result-document href="chapitre{$n_chapitre}/par_{$n_par}/{$id}.txt">
                    <xml>
                        <xsl:apply-templates select="//ancestor::tei:TEI[@xml:id = $id]//tei:p[@n = $n_par]"/>
                    </xml>
                </xsl:result-document>
            </xsl:for-each>
        </xsl:for-each>
    </xsl:template>
    <!--Crée des dossiers par paragraphe et par chapitre qui comportent les textes d'un même paragraphe.-->


    <xsl:template match="tei:teiHeader"/>

    <xsl:template match="tei:abbr"/>


    <xsl:template match="tei:fw"/>


    <xsl:template match="tei:p[not(node())] | tei:p[not(text())] | tei:p[not(text())][child::tei:anchor]"> VIDE </xsl:template>



    <xsl:template match="tei:note"/>





    <xsl:template match="tei:orig"/>
    <xsl:template match="tei:corr"/>


    <xsl:template match="tei:lb"/>





    <xsl:template match="text()">
        <xsl:for-each select="tokenize(., '\s+')">
            <xsl:element name="w">
                <xsl:attribute name="xml:id"> <xsl:variable name="uuid" select="substring-before(uuid:randomUUID(), '-')"/>
                    a<xsl:value-of select="$uuid"/> </xsl:attribute>
                <xsl:value-of select="."/>
            </xsl:element>
        </xsl:for-each>
    </xsl:template>




</xsl:stylesheet>
