<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">

    <xsl:strip-space elements="*"/>

    <xsl:param name="chemin_sortie" select="'../../chapitres/chapitre4/xml/'"/>
    <xsl:param name="chemin_sortie2" select="'../../'"/>
    <xsl:param name="chapitre" select="'4'"/>
    <xsl:param name="sigle" select="'Sal_J'"/>


    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <xsl:result-document href="{$chemin_sortie}apparat_{$sigle}_{$chapitre}_out.xml">
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

    <xsl:template match="tei:rdg[translate(@wit, '#', '') != $sigle]">
        <xsl:variable name="sigle_ms" select="ancestor::tei:TEI/@xml:id"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="nombre_temoins"
            select="string-length(@xml:id) - string-length(translate(@xml:id, '_', '')) + 1"/>
        <xsl:variable name="premiere_chaine" select="string-length(@xml:id) div $nombre_temoins"/>
        <xsl:variable name="retour_au_texte"
            select="concat($chemin_sortie2, 'temoins_tokenises?=*.xml')"/>
        <xsl:element name="rdg" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="wit" select="@wit"/>
            <xsl:value-of select="."/>
            <!--<xsl:for-each select="tokenize(@xml:id, '_')">
                <xsl:copy-of
                    select="substring(collection($retour_au_texte)//tei:w[contains($xml_id, @xml:id)]/text(), 1, $premiere_chaine)"
                />
            </xsl:for-each>-->
        </xsl:element>
    </xsl:template>

    <xsl:template match="tei:rdg[translate(@wit, '#', '') = $sigle]">
        <xsl:variable name="sigle_ms" select="ancestor::tei:TEI/@xml:id"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="retour_au_texte"
            select="concat($chemin_sortie2, 'temoins_tokenises/', $sigle, '.xml')"/>
        <xsl:element name="rdg" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="wit" select="@wit"/>
            <xsl:for-each select="tokenize(@xml:id, '_')">
                <xsl:copy-of
                    select="document($retour_au_texte)//tei:w[contains($xml_id, @xml:id)]/node()"/>
            </xsl:for-each>
        </xsl:element>
    </xsl:template>

    <!--On peut imaginer de créer une nouvelle strate de comparaison, en prenant les noeuds enfants des rdg et en les comparant, 
    Même si la chaîne de caractère est identique, pour vérifier que je n'ai pas ajouté de balise pour décrire un phénomène donné
    Si le noeud est différent, on va créer un nouveau rdg avec le noeud qui varie.-->

</xsl:stylesheet>
