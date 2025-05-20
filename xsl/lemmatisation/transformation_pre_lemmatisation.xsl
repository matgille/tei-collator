<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">

    <!--Il vaudrait mieux le transformer en fonction python, ce serait plus simple-->

    <xsl:param name="sortie"/>
    <xsl:param name="division"/>
    <xsl:output method="text"/>
    <xsl:strip-space elements="*"/>
    <xsl:param name="div1_n" select="1"/>
    <xsl:param name="div2_n" select="2"/>
    <xsl:param name="div3_n" select="2"/>

    <xsl:param name="div1_type" select="livre"/>
    <xsl:param name="div2_type" select="partie"/>
    <xsl:param name="div3_type" select="chapitre"/>



    <xsl:template match="tei:TEI">
        <xsl:result-document href="{$sortie}">
            <xsl:apply-templates select="descendant::tei:div[@type = $div1_type][@n = $div1_n]/descendant::tei:div[@type = $div2_type][@n = $div2_n]/descendant::tei:div[@type = $div3_type][@n = $div3_n]"/>

        <!--    <xsl:choose>
                <xsl:when test="$division = '*'">
                    <xsl:apply-templates
                        select="descendant::tei:text"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates
                        select="descendant::tei:text//tei:div[@n = $division]"
                    />
                </xsl:otherwise>
            </xsl:choose>-->
        </xsl:result-document>
    </xsl:template>

    <!--

    <xsl:template match="tei:TEI">
        <xsl:result-document href="fichier_tokenise_regularises/txt/{@xml:id}.txt">
            <xsl:apply-templates select="descendant::tei:text"/>
        </xsl:result-document>
    </xsl:template>-->

    <xsl:template
        match="tei:teiHeader | tei:fw | tei:note | tei:del | tei:hi[@rend = 'initiale']"/>

    <xsl:template match="tei:w">
        <xsl:variable name="replaced"
            select="translate(lower-case(.), 'áéíóúý', 'aeiouy')"/>
        <xsl:variable name="replaced_2"
            select="replace($replaced, 'ça', 'za')"/>
        <xsl:variable name="replaced_3"
            select="replace($replaced_2, 'çe', 'ce')"/>
        <xsl:variable name="replaced_4"
            select="replace($replaced_3, 'ço', 'zo')"/>
        <xsl:variable name="replaced_5"
            select="replace($replaced_4, 'çi', 'ci')"/>
        <xsl:variable name="replaced_6"
            select="replace($replaced_5, 'j', 'i')"/>
        <xsl:value-of
            select="replace($replaced_6, 'v', 'u')"/>
        <!--On supprime les accents pour avoir une meilleur lemmatisation. Ils ne seront pas supprimés dans le document de sortie,
        on ne réinjectera que les analyses dans le xml.-->
        <xsl:text>&#xA;</xsl:text>
    </xsl:template>

    <xsl:template match="tei:pc[text() != '.']">
        <xsl:value-of select="."/>
        <xsl:text>&#xA;</xsl:text>
    </xsl:template>

    <xsl:template match="tei:pc[text() = '.']">
        <xsl:value-of select="."/>
        <xsl:text>&#xA;&#xA;</xsl:text>
    </xsl:template>
</xsl:stylesheet>
