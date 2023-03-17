<?xml version="1.0" encoding="UTF-8"?>



<!--Troisième partie: transformer en json les sources xml pour pouvoir utiliser au mieux collatex -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    exclude-result-prefixes="xs math" xmlns:tei="http://www.tei-c.org/ns/1.0" version="3.0"
    xmlns:mgl="https://matthiasgillelevenson.fr">
    <xsl:output method="text"/>
    <xsl:param name="align_on"/>

    <xsl:strip-space elements="*"/>


    <xsl:template match="/">
        <xsl:text>{
        "witnesses" : [</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]
            }</xsl:text>
    </xsl:template>

    <xsl:template match="mgl:temoin[child::tei:*]">
        <!--Any empty div won't be processed: there -->
        <xsl:text>{
    "id":"</xsl:text>
        <xsl:value-of select="@n"/>
        <xsl:text>",
        "tokens" : [</xsl:text>
        <!--<xsl:for-each select="descendant::tei:w[text()]|descendant::tei:pc">-->
        <xsl:for-each select="descendant::tei:w[text()] | tei:milestone[@type = 'ancre_alignement']">
            <xsl:text>{"t": "</xsl:text>
            <xsl:choose>
                <xsl:when test="node()">
                    <xsl:value-of select="normalize-space(.)"/>
                </xsl:when>
                <!--
                <xsl:otherwise>
                    <xsl:text>ø</xsl:text>
                </xsl:otherwise>-->
            </xsl:choose>
            <!--pour éviter des sauts de ligne qui ne sont vraiment pas appréciés par le validateur JSON-->
            <xsl:text> "</xsl:text>
            <xsl:choose>
                <xsl:when test="@synch">
                    <xsl:text>,</xsl:text>
                    <xsl:text>"n": "</xsl:text>
                    <xsl:value-of select="@synch"/>
                    <xsl:text>" </xsl:text>
                    <xsl:if test="@lemma">
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
                </xsl:when>
                <xsl:otherwise>
                    <xsl:if test="@lemma">
                        <xsl:text>,</xsl:text>
                        <xsl:text>"n": "</xsl:text>
                        <xsl:choose>
                            <!--On commence par normaliser les entités nommées sur les parties du discours uniquement.-->
                            <xsl:when test="starts-with(@pos, 'NP')">
                                <xsl:value-of select="@pos"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:choose>
                                    <!--On va comparer sur les lemmes et les pos en concaténant les deux valeurs-->
                                    <xsl:when test="$align_on = '1'">
                                        <xsl:value-of select="concat(@lemma, '|', @pos)"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:value-of select="@lemma"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:otherwise>
                        </xsl:choose>
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
                </xsl:otherwise>
            </xsl:choose>
            <xsl:text>,</xsl:text>
            <xsl:text>"xml:id" : "</xsl:text>
            <xsl:value-of select="@xml:id"/>
            <xsl:text>"}</xsl:text>
            <xsl:variable name="nom_temoin" select="ancestor::mgl:temoin/@n"/>
            <!--<xsl:if test="following::tei:w[text()][ancestor::mgl:temoin/@n = $nom_mgl:temoin]|following::tei:pc[ancestor::mgl:temoin/@n = $nom_mgl:temoin]">-->
            <xsl:if
                test="following::tei:w[text()][ancestor::mgl:temoin/@n = $nom_temoin] | following::tei:milestone[@type = 'ancre_alignement'][ancestor::mgl:temoin/@n = $nom_temoin]">
                <xsl:text>,</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>]}</xsl:text>
        <xsl:if test="following::mgl:temoin">
            <xsl:text>,</xsl:text>
        </xsl:if>
    </xsl:template>

    <xsl:template match="mgl:temoin[not(child::tei:*)]">
        <!--Any empty div won't be processed: there -->
        <xsl:text>{
    "id":"</xsl:text>
        <xsl:value-of select="@n"/>
        <xsl:text>",
        "tokens" : [</xsl:text>
        <xsl:text>{"t": ""</xsl:text>
        <xsl:if test="@lemma">
            <xsl:text>,</xsl:text>
            <xsl:text>"n": "" </xsl:text>
        </xsl:if>
        <xsl:text>,</xsl:text>
        <xsl:text>"xml:id" : "none</xsl:text>
        <xsl:text>"}</xsl:text>
        <xsl:text>]}</xsl:text>
        <xsl:if test="following::mgl:temoin">
            <xsl:text>,</xsl:text>
        </xsl:if>
    </xsl:template>

</xsl:stylesheet>
