<?xml version="1.0" encoding="UTF-8"?>
<!--Cette feuille est la troisième phase d'injection: on ajoute la ponctuation en comparant le
fichier précédent avec la transcription tokenisée originelle. 
Résultat: un fichier final qui marche !-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="xml"/>
    <xsl:strip-space elements="*"/>

    <xsl:param name="chapitre" select="'21'"/>
    <xsl:param name="chemin_sortie">
        <xsl:text>../../chapitres/chapitre</xsl:text>
        <xsl:value-of select="$chapitre"/>
        <xsl:text>/</xsl:text>
    </xsl:param>
    <xsl:param name="chemin_sortie2" select="'../../'"/>
    <xsl:param name="sigle" select="'Mad_G'"/>


    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <xsl:result-document href="{$chemin_sortie}apparat_{$sigle}_{$chapitre}_out.xml">
            <xsl:apply-templates/>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="tei:pc"/>

    <xsl:template match="tei:w">
        <xsl:variable name="ms" select="ancestor::*:temoin/@n"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="temoin_tokenise"
            select="concat('../../temoins_tokenises/', $sigle, '.xml')"/>
        <xsl:choose>
            <xsl:when
                test="document($temoin_tokenise)//tei:w[contains($xml_id, @xml:id)]/following::*[1][self::tei:pc]">
<!--                <xsl:text>Oui</xsl:text>-->
                <xsl:copy-of select="."/>
                <xsl:copy-of
                    select="document($temoin_tokenise)//tei:w[contains($xml_id, @xml:id)]/following::*[1][self::tei:pc]"
                />
            </xsl:when>
            <xsl:otherwise>
<!--                <xsl:text>Non</xsl:text>-->
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
