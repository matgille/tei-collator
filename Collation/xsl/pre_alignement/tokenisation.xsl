<?xml version="1.0" encoding="UTF-8"?>

<!--étape 1: tokeniser. Manque juste à extraire la ponctuation et à la conserver.-->
<!--Feuille XSL qui permet d'ajouter des id à tous les mots après les avoir tokenisés.-->
<!--à faire, URGENT: 1) nettoyer la feuille et 2) créer une sécurité pour ne pas perdre tout le travail en re-tokenisant
avec de nouveaux xml:id-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs tei" version="2.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:xf="http://www.w3.org/2002/xforms"
    xmlns:uuid="java:java.util.UUID" xmlns:math="http://exslt.org/math"
    xmlns:f="urn:stylesheet-func" xmlns:propre="http://perso.ens-lyon.fr"
    extension-element-prefixes="math">
    <xsl:strip-space elements="*"/>
    <!--    <xsl:output doctype-system="Sal_J.dtd"/>-->


    <xsl:function name="propre:randomisation">
        <xsl:variable name="random_alpha"
            select="concat(string(floor(math:random() * 3)), string(floor(math:random() * 5)))"/>
        <xsl:variable name="random00" select="replace($random_alpha, '00', 'a')"/>
        <xsl:variable name="random0" select="replace($random00, '01', 'a')"/>
        <xsl:variable name="random1" select="replace($random0, '02', 'b')"/>
        <xsl:variable name="random2" select="replace($random1, '03', 'c')"/>
        <xsl:variable name="random3" select="replace($random2, '04', 'd')"/>
        <xsl:variable name="random4" select="replace($random3, '05', 'e')"/>
        <xsl:variable name="random5" select="replace($random4, '06', 'f')"/>
        <xsl:variable name="random6" select="replace($random5, '07', 'g')"/>
        <xsl:variable name="random7" select="replace($random6, '08', 'h')"/>
        <xsl:variable name="random8" select="replace($random7, '09', 'i')"/>
        <xsl:variable name="random9" select="replace($random8, '10', 'j')"/>
        <xsl:variable name="random10" select="replace($random9, '11', 'k')"/>
        <xsl:variable name="random11" select="replace($random10, '12', 'l')"/>
        <xsl:variable name="random12" select="replace($random11, '13', 'm')"/>
        <xsl:variable name="random13" select="replace($random12, '14', 'n')"/>
        <xsl:variable name="random14" select="replace($random13, '15', 'o')"/>
        <xsl:variable name="random15" select="replace($random14, '16', 'p')"/>
        <xsl:variable name="random16" select="replace($random15, '17', 'q')"/>
        <xsl:variable name="random17" select="replace($random16, '18', 'r')"/>
        <xsl:variable name="random18" select="replace($random17, '19', 's')"/>
        <xsl:variable name="random19" select="replace($random18, '20', 't')"/>
        <xsl:variable name="random20" select="replace($random19, '21', 'u')"/>
        <xsl:variable name="random21" select="replace($random20, '22', 'v')"/>
        <xsl:variable name="random22" select="replace($random21, '23', 'w')"/>
        <xsl:variable name="random23" select="replace($random22, '24', 'x')"/>
        <xsl:variable name="random24" select="replace($random23, '25', 'y')"/>
        <xsl:variable name="random25" select="replace($random24, '26', 'z')"/>
        <xsl:value-of select="$random25"/>
    </xsl:function>

    <xsl:template match="/">
        <xsl:result-document href="../temoins/groupe.xml">
            <xsl:element name="group">
                <xsl:apply-templates xpath-default-namespace="tei"/>
            </xsl:element>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="tei:choice">
        <xsl:apply-templates select="tei:reg"/>
        <xsl:apply-templates select="tei:expan"/>
        <xsl:apply-templates select="tei:corr"/>
    </xsl:template>

    <xsl:template match="tei:text">
        <text xml:id="{ancestor::tei:TEI/@xml:id}">
            <xsl:apply-templates/>
        </text>
    </xsl:template>

    <!--    <!-\-Conserver les commentaires pour ne pas perdre d'information-\->
    <xsl:template match="comment()">
        <xsl:comment><xsl:value-of select="."/></xsl:comment>
    </xsl:template>-->
    <!--problème de tokénisation: les virgules-->
    <xsl:template match="tei:TEI[@type = 'bibliographie'] | tei:TEI[@type = 'these']"/>

    <xsl:template match="tei:TEI[@type = 'transcription']">
        <xsl:element name="TEI" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:apply-templates/>
        </xsl:element>


        <!-- <xsl:analyze-string select="." regex="([.,:;!?])">
            <xsl:matching-substring>
                <xsl:element name="pct">
                    <xsl:attribute name="xml:id">a<xsl:value-of
                        select="substring-before(uuid:randomUUID(), '-')"/></xsl:attribute>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:element>
                <xsl:element name="w">
                    <xsl:attribute name="xml:id">a<xsl:value-of
                        select="substring-before(uuid:randomUUID(), '-')"/></xsl:attribute>
                    <xsl:value-of select="regex-group(2)"/>
                </xsl:element>
            </xsl:matching-substring>
        </xsl:analyze-string>-->
    </xsl:template>

    <xsl:template match="text()[not(ancestor::tei:note)][not(ancestor::tei:teiHeader)]">
        <xsl:for-each select="tokenize(., '([.,!?;:]*)?\s+')">
            <xsl:variable name="random_alpha"
                select="concat(string(floor(math:random() * 3)), string(floor(math:random() * 5)))"/>
            <xsl:variable name="random00" select="replace($random_alpha, '00', 'a')"/>
            <xsl:variable name="random0" select="replace($random00, '01', 'a')"/>
            <xsl:variable name="random1" select="replace($random0, '02', 'b')"/>
            <xsl:variable name="random2" select="replace($random1, '03', 'c')"/>
            <xsl:variable name="random3" select="replace($random2, '04', 'd')"/>
            <xsl:variable name="random4" select="replace($random3, '05', 'e')"/>
            <xsl:variable name="random5" select="replace($random4, '06', 'f')"/>
            <xsl:variable name="random6" select="replace($random5, '07', 'g')"/>
            <xsl:variable name="random7" select="replace($random6, '08', 'h')"/>
            <xsl:variable name="random8" select="replace($random7, '09', 'i')"/>
            <xsl:variable name="random9" select="replace($random8, '10', 'j')"/>
            <xsl:variable name="random10" select="replace($random9, '11', 'k')"/>
            <xsl:variable name="random11" select="replace($random10, '12', 'l')"/>
            <xsl:variable name="random12" select="replace($random11, '13', 'm')"/>
            <xsl:variable name="random13" select="replace($random12, '14', 'n')"/>
            <xsl:variable name="random14" select="replace($random13, '15', 'o')"/>
            <xsl:variable name="random15" select="replace($random14, '16', 'p')"/>
            <xsl:variable name="random16" select="replace($random15, '17', 'q')"/>
            <xsl:variable name="random17" select="replace($random16, '18', 'r')"/>
            <xsl:variable name="random18" select="replace($random17, '19', 's')"/>
            <xsl:variable name="random19" select="replace($random18, '20', 't')"/>
            <xsl:variable name="random20" select="replace($random19, '21', 'u')"/>
            <xsl:variable name="random21" select="replace($random20, '22', 'v')"/>
            <xsl:variable name="random22" select="replace($random21, '23', 'w')"/>
            <xsl:variable name="random23" select="replace($random22, '24', 'x')"/>
            <xsl:variable name="random24" select="replace($random23, '25', 'y')"/>
            <xsl:variable name="random25" select="replace($random24, '26', 'z')"/>
            <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:attribute name="xml:id">
                    <xsl:variable name="random0" select="propre:randomisation()"/>
                    <xsl:variable name="random"
                        select="concat(floor(math:random() * 9), floor(math:random() * 9), floor(math:random() * 9), floor(math:random() * 9), floor(math:random() * 9))"/>
                    <xsl:value-of select="concat($random25, $random, $random25)"/>
                </xsl:attribute>
                <xsl:value-of select="."/>
            </xsl:element>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="tei:teiHeader"/>

</xsl:stylesheet>
