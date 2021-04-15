<?xml version="1.0" encoding="UTF-8"?>



<!--Troisième partie: transformer en json les sources xml pour pouvoir utiliser au mieux collatex -->
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    exclude-result-prefixes="xs math"
    xmlns:tei="http://www.tei-c.org/ns/1.0" version="3.0">
    <xsl:output method="text"/>

    <xsl:strip-space elements="*"/>


    <xsl:template match="/">
        <xsl:text>{
        "witnesses" : [</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]
            }</xsl:text>
    </xsl:template>

    <xsl:template match="temoin[child::tei:*]">
        <!--Any empty div won't be processed: there -->
        <xsl:text>{
    "id":"</xsl:text>
        <xsl:value-of select="@n"/>
        <xsl:text>",
        "tokens" : [</xsl:text>
        <!--<xsl:for-each select="descendant::tei:w[text()]|descendant::tei:pc">-->
        <xsl:for-each select="descendant::tei:w[text()]">
            <xsl:text>{"t": "</xsl:text>
            <xsl:value-of select="normalize-space(.)"/>
            <!--pour éviter des sauts de ligne qui sont vraiment pas appréciés par le validateur JSON-->
            <xsl:text> "</xsl:text>
            <xsl:if test="@lemma">
                <xsl:text>,</xsl:text>
                <xsl:text>"n": "</xsl:text>
                <!--On va comparer sur les lemmes et les pos en concaténant les deux valeurs-->
                <xsl:value-of
                    select="concat(@lemma, '|', @pos, '|')"/>
                <xsl:text>" </xsl:text>
                <xsl:text>,</xsl:text>
                <xsl:text>"lemma": "</xsl:text>
                <xsl:value-of select="@lemma"/>
                <xsl:text>" </xsl:text>
            </xsl:if>
            <xsl:if test="@pos">
                <xsl:text>,</xsl:text>
                <xsl:text>"pos": "</xsl:text>
                <xsl:value-of select="@pos"/>
                <xsl:text>" </xsl:text>
            </xsl:if>
            <xsl:text>,</xsl:text>
            <xsl:text>"xml:id" : "</xsl:text>
            <xsl:value-of select="@xml:id"/>
            <xsl:text>"}</xsl:text>
            <xsl:variable name="nom_temoin"
                select="ancestor::temoin/@n"/>
            <!--<xsl:if test="following::tei:w[text()][ancestor::temoin/@n = $nom_temoin]|following::tei:pc[ancestor::temoin/@n = $nom_temoin]">-->
            <xsl:if
                test="following::tei:w[text()][ancestor::temoin/@n = $nom_temoin]">
                <xsl:text>,</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>]}</xsl:text>
        <xsl:if test="following::temoin">
            <xsl:text>,</xsl:text>
        </xsl:if>
    </xsl:template>

    <xsl:template match="temoin[not(child::tei:*)]">
        <!--Any empty div won't be processed: there -->
        <xsl:text>{
    "id":"</xsl:text>
        <xsl:value-of select="@n"/>
        <xsl:text>",
        "tokens" : [</xsl:text>
        <xsl:text>{"t": "empty"</xsl:text>
        <xsl:if test="@lemma">
            <xsl:text>,</xsl:text>
            <xsl:text>"n": "ø" </xsl:text>
        </xsl:if>
        <xsl:text>,</xsl:text>
        <xsl:text>"xml:id" : "none</xsl:text>
        <xsl:text>"}</xsl:text>
        <xsl:text>]}</xsl:text>
        <xsl:if test="following::temoin">
            <xsl:text>,</xsl:text>
        </xsl:if>
    </xsl:template>

</xsl:stylesheet>
