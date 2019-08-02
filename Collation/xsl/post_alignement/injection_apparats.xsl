<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="xml"/>
    <!--Feuille qui réinjecte à l'aide des identifiants de token l'apparat dans chaque transcription individuelle, 
    de manière à pouvoir créer des éditions ayant pour base chacun des manuscrits-->
    <!--ÀF: s'occuper du namespace (feuilles de transformation précédentes)-->
    <!--ÀF: trouver une façon de gérer les omissions du témoin base-->
    <!--Question importate sur l'injection: pour un sic par exemple dans un lieu variant, 
    vaut-il mieux créer un apparat enfant du <sic> ou re-créer des <sic> dans les <rdg> ? La seconde
    option est meilleure du point de vue de la représentation du texte, mais elle est la plus risquée. Á voir-->
   
    <xsl:param name="chapitre"/>
    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="*:temoin">
        <xsl:variable name="sigle" select="translate(@n, '#', '')"/>
        <xsl:result-document href="apparat_{$sigle}.xml">
            <div>
                <xsl:attribute name="type">chapitre</xsl:attribute>
                <xsl:attribute name="n" select="$chapitre"/>
                <xsl:attribute name="xml:id" select="concat($sigle, '_3_3_', $chapitre)"/>
                <xsl:apply-templates/>
            </div>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="*:w">
        <xsl:variable name="ms" select="ancestor::*:temoin/@n"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="apparat_chapitre"
            select="concat('../../chapitres/chapitre',$chapitre, '/apparat_collatex.xml')"/>
        <xsl:if
            test="document($apparat_chapitre)//*:rdg[contains(@wit, $ms) and contains(@xml:id, $xml_id)]">
            <!--Tester si le token est pas déjà dans un apparat qui touche le token précédent: suppression des doublons-->
            <xsl:variable name="token_precedent" select="preceding::*:w[1]/@xml:id"/>
            <xsl:if
                test="not(contains(document($apparat_chapitre)//*:rdg[contains(@wit, $ms)][contains(@xml:id, $xml_id)]/@xml:id, $token_precedent))">
                <xsl:copy-of
                    select="document($apparat_chapitre)//*:app[child::*:rdg[contains(@wit, $ms) and contains(@xml:id, $xml_id)]]"
                />
            </xsl:if>
            <!--Tester si le token est pas déjà dans un apparat qui touche le token précédent-->
        </xsl:if>
        <xsl:if
            test="not(document($apparat_chapitre)//*:rdg[contains(@wit, $ms)][contains(@xml:id, $xml_id)])">
            <xsl:copy-of select="."/>
        </xsl:if>
    </xsl:template>


</xsl:stylesheet>
