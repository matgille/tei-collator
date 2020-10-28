<?xml version="1.0" encoding="UTF-8"?>
<!--Seconde phase bis: on s'occupe des apparats avec une seule variante, pour les transformer en suite de tei:w
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="xs"
    version="2.0">

    <xsl:strip-space elements="*"/>

    <xsl:param name="chapitre" select="'20'"/>
    <xsl:param name="chemin_sortie">
        <xsl:text>divs/div</xsl:text>
        <xsl:value-of select="$chapitre"/>
        <xsl:text>/</xsl:text>
    </xsl:param>
    <xsl:param name="chemin_sortie2" select="'../../'"/>
    <xsl:param name="sigle" select="'Sal_J'"/>
    <xsl:variable name="retour_au_texte"
        select="concat($chemin_sortie2, $chemin_sortie, 'apparat_', $sigle, '_', $chapitre, '.xml')"/>


    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <xsl:result-document
            href="{$chemin_sortie}apparat_{$sigle}_{$chapitre}_outc.xml">
            <xsl:apply-templates/>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="tei:rdg">
        <xsl:element name="rdg" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="wit">
                <xsl:value-of select="@wit"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="tei:app[@type = 'not_apparat']">
        <xsl:apply-templates select="descendant::tei:w"/>
    </xsl:template>

    <!--Ici on rétablit les identifiants des tei:w qu'on avait perdus précédemment, en reprenant le fichier apparat_X_X.xml.-->
    <xsl:template match="tei:w">
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:if test="@xml:id != 'none'">
                <xsl:attribute name="xml:id">
                    <xsl:variable name="xml_id_pre_processed">
                        <!--On va chercher dans le document avant réduction des redondances, il y a donc un risque d'avoir un xml:id double-->
                        <xsl:value-of
                            select="document($retour_au_texte)//tei:w[contains(@xml:id, $xml_id)]/@xml:id"
                        />
                    </xsl:variable>
                    <xsl:choose>
                        <xsl:when test="contains($xml_id_pre_processed, ' ')">
                            <xsl:value-of
                                select="tokenize($xml_id_pre_processed, ' ')[1]"
                            />
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="$xml_id_pre_processed"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
            </xsl:if>
            <xsl:value-of select="."/>
        </xsl:element>
    </xsl:template>




</xsl:stylesheet>
