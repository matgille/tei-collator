<?xml version="1.0" encoding="UTF-8"?>
<!--Deuxième phase de l'injection: restauration des noeuds non textuels dans les apparats-->
<!--À nouveau on a un travail de comparaison ici, mais cette fois avec les fichiers de transcription
tokénisée (on va rétablir les éléments à l'intérieur des tei:w)-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">

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
        <xsl:result-document href="{$chemin_sortie}apparat_{$sigle}_{$chapitre}_outb.xml">
            <xsl:apply-templates/>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="tei:w">
        <xsl:variable name="sigle_ms" select="ancestor::tei:TEI/@xml:id"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="retour_au_texte"
            select="concat($chemin_sortie2, 'temoins_tokenises/', $sigle, '.xml')"/>
        <xsl:for-each select="tokenize(@xml:id, '_')">
            <xsl:copy-of select="document($retour_au_texte)//tei:w[@xml:id = $xml_id]"/>
        </xsl:for-each>
    </xsl:template>

    <!--Pour les leçons autre que le manuscrit base-->
    <xsl:template match="tei:rdg[not(contains(@wit, $sigle))]">
        <xsl:variable name="sigle_ms" select="ancestor::tei:TEI/@xml:id"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="nombre_temoins"
            select="string-length(@xml:id) - string-length(translate(@xml:id, '_', '')) + 1"/>
        <xsl:variable name="premiere_chaine" select="string-length(@xml:id) div $nombre_temoins"/>
        <xsl:variable name="retour_au_texte"
            select="concat($chemin_sortie2, 'temoins_tokenises?=*.xml')"/>
        <xsl:element name="rdg" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="wit" select="@wit"/>
            <!--On ne récupère rien (à changer p.e.)-->
            <xsl:for-each select="tei:w">
                <xsl:copy-of select="."/>
            </xsl:for-each>
            <!--On ne récupère rien-->
        </xsl:element>
    </xsl:template>
    <!--Pour les leçons autre que le manuscrit base-->


    <!--Pour les leçons qui touchent au manuscrit base-->
    <xsl:template match="tei:rdg[contains(@wit, $sigle)]">
        <xsl:variable name="sigle_ms" select="ancestor::tei:TEI/@xml:id"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="retour_au_texte"
            select="concat($chemin_sortie2, 'temoins_tokenises/', $sigle, '.xml')"/>
        <xsl:element name="rdg" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="wit" select="@wit"/>
            <!--On récupère les tei:w des transcriptions tokenisées et éventuellement les noeuds à l'intérieur-->
            <xsl:for-each select="tokenize(@xml:id, '_')">
                <xsl:variable name="xml_id" select="."/>
                <xsl:copy-of select="document($retour_au_texte)//tei:w[@xml:id = $xml_id]"/>
            </xsl:for-each>
            <!--On récupère les tei:w des transcriptions tokenisées-->
        </xsl:element>
    </xsl:template>
    <!--Pour les leçons qui touchent au manuscrit base-->



</xsl:stylesheet>
