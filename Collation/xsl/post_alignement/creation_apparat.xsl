<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="text"/>


    <xsl:template match="/">
        <xsl:text>[</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]</xsl:text>
    </xsl:template>


    <!--Un dictionnaire par app-->
    <xsl:template match="app">
        <xsl:text>{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
        <xsl:if test="following-sibling::app">
            <xsl:text>,</xsl:text>
        </xsl:if>
    </xsl:template>
    <!--Un dictionnaire par app-->

    <!--Une liste par leçon-->
    <xsl:template match="rdg">
        <xsl:text>"</xsl:text>
        <xsl:value-of select="count(preceding-sibling::rdg)"/>
        <xsl:text>" : ["</xsl:text>
        <xsl:for-each select="w">
            <xsl:value-of select="@xml:id"/>
            <xsl:if test="following-sibling::w">
                <xsl:text>_</xsl:text>
            </xsl:if>
        </xsl:for-each>
        <xsl:text>","</xsl:text>
        <xsl:value-of select="w"/>
        <xsl:text>","</xsl:text>
        <!--Il y a un dièse de trop à un moment et je n'ai pas réussi à déterminer où.-->
        <xsl:value-of select="replace(@wit, '##', '#')"/>
        <xsl:text>"]</xsl:text>
        <xsl:if test="following-sibling::rdg">
            <xsl:text>,</xsl:text>
        </xsl:if>
    </xsl:template>
    <!--Une liste par leçon-->

    <xsl:template match="w"/>
</xsl:stylesheet>
