﻿<?xml version="1.0" encoding="UTF-8"?>

<!--étape 2: scission en chapitres.-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs tei" version="2.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:xf="http://www.w3.org/2002/xforms"
    xmlns:uuid="java:java.util.UUID" xmlns:f="urn:stylesheet-func">
    <xsl:strip-space elements="*"/>
    <xsl:output method="xml"/>

    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <xsl:for-each select="//tei:TEI[1]//tei:div[@type = 'chapitre'][not(@subtype)]">
            <xsl:variable name="numero_chapitre" select="@n"/>
            <xsl:result-document
                href="file:/Users/squatteur/Desktop/hyperregimiento-de-los-principes/Collation/chapitres/chapitre{$numero_chapitre}/juxtaposition.xml">
                <xsl:element name="groupe">
                    <xsl:element name="temoin">
                        <xsl:attribute name="n">
                            <xsl:value-of select="ancestor::text/@xml:id"/>
                        </xsl:attribute>
                        <xsl:apply-templates/>
                    </xsl:element>
                    <xsl:for-each
                        select="following::tei:div[@type = 'chapitre'][not(@subtype)][@n = $numero_chapitre]">
                        <xsl:element name="temoin">
                            <xsl:attribute name="n">
                                <xsl:value-of select="ancestor::text/@xml:id"/>
                            </xsl:attribute>
                            <xsl:apply-templates/>
                        </xsl:element>
                    </xsl:for-each>
                </xsl:element>
            </xsl:result-document>
        </xsl:for-each>
    </xsl:template>

</xsl:stylesheet>