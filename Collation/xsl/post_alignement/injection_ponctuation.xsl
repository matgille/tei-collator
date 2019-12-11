<?xml version="1.0" encoding="UTF-8"?>
<!--Cette feuille est la troisième phase d'injection: on ajoute la ponctuation en comparant le
fichier précédent avec la transcription tokenisée originelle. 
Résultat: un fichier final qui marche !-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="xml"/>
    <xsl:strip-space elements="*"/>

    <xsl:param name="chapitre" select="'9'"/>
    <xsl:param name="chemin_sortie">
        <xsl:text>../../chapitres/chapitre</xsl:text>
        <xsl:value-of select="$chapitre"/>
        <xsl:text>/</xsl:text>
    </xsl:param>
    <xsl:param name="chemin_sortie2" select="'../../'"/>
    <xsl:param name="sigle" select="'Sal_J'"/>


    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <xsl:result-document href="{$chemin_sortie}apparat_{$sigle}_{$chapitre}_out.xml">
            <xsl:apply-templates/>
        </xsl:result-document>
    </xsl:template>

    <!--Redondance de la ponctuation-->
    <xsl:template
        match="tei:pc[preceding::*[1][self::tei:w]] | tei:pc[preceding-sibling::*[1][self::tei:app]]"/>
    <!--Redondance de la ponctuation-->


    <!--On prend chaque token, et si un élément de ponctuation suit, on copie le token et la ponctuation-->
    <xsl:template match="tei:w">
        <xsl:variable name="ms" select="ancestor::*:temoin/@n"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="temoin_tokenise"
            select="concat('../../temoins_tokenises/', $sigle, '.xml')"/>
        <xsl:choose>
            <xsl:when
                test="document($temoin_tokenise)//tei:w[contains($xml_id, @xml:id)]/following::*[1][self::tei:pc]">
                <xsl:copy-of select="."/>
                <xsl:copy-of
                    select="document($temoin_tokenise)//tei:w[contains($xml_id, @xml:id)]/following::*[1][self::tei:pb]"/>
                <xsl:copy-of
                    select="document($temoin_tokenise)//tei:w[contains($xml_id, @xml:id)]/following::*[1][self::tei:pc]"
                />
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    <!--On prend chaque token, et si un élément de ponctuation suit, on copie le token et la ponctuation-->



    <!--<!-\-Gestion des lacunes, création des lacunaStart et lacunaEnd. Attention, ça peut faire n'importe quoi.-\->
    <!-\-Suppose de déconstruire des apparats s'il n'y a que deux leçons dont une vide-\->
    <xsl:template match="tei:app[tei:rdg[not(node())]]">
        <xsl:variable name="position" select="count(preceding::tei:app)"/>
        <xsl:text>Position omission:</xsl:text>
        <xsl:value-of select="$position"/>
        <xsl:variable name="temoin" select="tei:rdg[not(node())]/@wit"/>
        <!-\-Ne marchera pas si il y a plusieurs témoins vides-\->
        <xsl:choose>
            <xsl:when
                test="following::tei:app[1]/tei:rdg[@wit = $temoin][not(node())] and not(preceding::tei:app[last()]/tei:rdg[@wit = $temoin][not(node())])">
                <xsl:element name="lacunaStart" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="wit" select="tei:rdg[@wit = $temoin][not(node())]/@wit"/>
                </xsl:element>
                <xsl:choose>
                    <!-\-S'il n'y a que deux leçons, dont une correspond à une omission, on n'a pas d'apparat, puisque l'omission
                    est indiquée avec les éléments lacunaStart et lacunaEnd-\->
                    <xsl:when test="count(tei:rdg) = 2">
                        <!-\-<xsl:copy-of select="tei:rdg[node()]/node()"/>-\->
                        <xsl:element name="app" namespace="http://www.tei-c.org/ns/1.0">
                            <!-\-<xsl:copy-of select="* except tei:rdg[not(node())]"/>-\->
                            <xsl:copy-of select="*"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="app" namespace="http://www.tei-c.org/ns/1.0">
                            <!-\-<xsl:copy-of select="* except tei:rdg[not(node())]"/>-\->
                            <xsl:copy-of select="*"/>
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:when
                test="following::tei:app[1]/tei:rdg[@wit = $temoin][not(node())] and preceding::tei:app[last()]/tei:rdg[@wit = $temoin][not(node())]">
                <xsl:choose>
                    <!-\-S'il n'y a que deux leçons, dont une correspond à une omission, on n'a pas d'apparat, puisque l'omission
                    est indiquée avec les éléments lacunaStart et lacunaEnd-\->
                    <xsl:when test="count(tei:rdg) = 2">
                        <!-\-                        <xsl:copy-of select="tei:rdg[node()]/node()"/>-\->
                        <xsl:element name="app" namespace="http://www.tei-c.org/ns/1.0">
                            <!-\-<xsl:copy-of select="* except tei:rdg[not(node())]"/>-\->
                            <xsl:copy-of select="*"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="app" namespace="http://www.tei-c.org/ns/1.0">
                            <!-\-<xsl:copy-of select="* except tei:rdg[not(node())]"/>-\->
                            <xsl:copy-of select="*"/>
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
                <xsl:element name="app" namespace="http://www.tei-c.org/ns/1.0">
                    <!-\-<xsl:copy-of select="* except tei:rdg[not(node())]"/>-\->
                    <xsl:copy-of select="*"/>
                    <xsl:text>Prout</xsl:text>
                </xsl:element>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <!-\-Fin de lacune-\->
    <!-\-Ça ne marche pas, mais alors pas du tout-\->
    <xsl:template match="tei:app[not(tei:rdg[not(descendant::tei:w)])]">
        <xsl:variable name="position" select="count(preceding::tei:app)"/>
        <xsl:text>Position pas omission:</xsl:text>
        <xsl:value-of select="$position"/>
        <xsl:choose>
            <xsl:when
                test="//tei:app[count(preceding::tei:app) = number($position - 1) and tei:rdg[not(node())]]">
                <xsl:variable name="temoin" select="tei:rdg[not(node())]/@wit"/>
                <xsl:element name="lacunaEnd" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="wit"
                        select="//tei:app[position() = $position - 1]/tei:rdg[not(node())]/@wit"/>
                </xsl:element>
            </xsl:when>
        </xsl:choose>
        <xsl:copy-of select="."/>
    </xsl:template>
    <!-\-Fin de lacune-\->

    <!-\-Gestion des lacunes. Attention, ça peut faire n'importe quoi.-\->-->

</xsl:stylesheet>
