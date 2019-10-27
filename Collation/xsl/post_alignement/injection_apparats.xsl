<?xml version="1.0" encoding="UTF-8"?>
<!--Première phase de l'injection: récupération des apparats et des noeuds textuels-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="xml"/>
    <xsl:strip-space elements="*"/>
    <!--Feuille qui réinjecte à l'aide des identifiants de token l'apparat dans chaque transcription individuelle, 
    de manière à pouvoir créer des éditions ayant pour base chacun des manuscrits-->
    <!--FAIT: s'occuper du namespace pour revenir à de la tei. C'est pas très beau mais ça fait le travail, 
    géré au niveau du script python. -->
    <!--ÀF: trouver une façon de gérer les omissions du témoin base-->
    <!--Question importante sur l'injection: pour un sic par exemple dans un lieu variant, 
    vaut-il mieux créer un apparat enfant du <sic> ou re-créer des <sic> dans les <rdg> ? La seconde
    option est meilleure du point de vue de la représentation du texte, mais elle est la plus risquée. Á voir-->
    <!--La ponctuation dans les app n'est pas rétablie (ce n'est pas un bug, elle n'est pas conservée). Gérer cela.-->
    <xsl:param name="chemin_sortie"/>
    <xsl:param name="chapitre" select="3"/>
    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="*:temoin">
        <xsl:variable name="sigle" select="translate(@n, '#', '')"/>
        <xsl:result-document href="{$chemin_sortie}apparat_{$sigle}_{$chapitre}.xml">
            <xsl:element name="div" namespace="http://www.tei-c.org/ns/1.0">
                <xsl:attribute name="type">chapitre</xsl:attribute>
                <xsl:attribute name="n" select="$chapitre"/>
                <xsl:attribute name="xml:id" select="concat($sigle, '_3_3_', $chapitre)"/>
                <xsl:apply-templates/>
            </xsl:element>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="tei:w">
        <!--Fonctionnement pour l'instant: on va comparer deux fichiers xml. Pour chaque token dans la transcription originale (xml 1), 
        regarder si l'identifiant apparaît dans un apparat du fichier de collation produit (xml 2). Si tel est le cas, remplacer le 
        token par l'apparat.-->
        <!--Limite de ce procédé: on est moins précis quand on marque un token en particulier: le <add>, par exemple, 
            va se retrouver 
        parent d'un app et donc d'un rdg d'un autre manuscrit, ce qui n'a aucun sens.-->
        <!--Solution: Créer une feuilles de tokénisation intermédiaire-->
        <!--Solution 2: faire de cette feuille un truc un peu plus complexe en copiant de la feuille d'apparat tout sauf 
            le rdg courant, 
        et en réintégrant les information de l'xml 1 concernant ce rdg dans l'xml de sortie -->
        <!--Cela permettra d'éviter un truc du genre: del > app > rdg rdg rdg, pour avoir app > rdg rdg rdg > del -->
        <xsl:variable name="ms" select="ancestor::*:temoin/@n"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="apparat_chapitre"
            select="concat('../../chapitres/chapitre', $chapitre, '/apparat_collatex.xml')"/>
        <xsl:if
            test="document($apparat_chapitre)//tei:rdg[contains(@wit, $ms) and contains(@xml:id, $xml_id)]">
            <!--Tester si le token est pas déjà dans un apparat qui touche le token précédent: suppression des doublons-->
            <xsl:variable name="token_precedent" select="preceding::tei:w[1]/@xml:id"/>
            <xsl:if
                test="not(contains(document($apparat_chapitre)//tei:rdg[contains(@wit, $ms)][contains(@xml:id, $xml_id)]/@xml:id, $token_precedent))">
                <xsl:copy-of
                    select="document($apparat_chapitre)//tei:app[child::tei:rdg[contains(@wit, $ms) and contains(@xml:id, $xml_id)]]"
                />
            </xsl:if>
            <!--Tester si le token est pas déjà dans un apparat qui touche le token précédent-->
        </xsl:if>
        <xsl:if
            test="not(document($apparat_chapitre)//tei:rdg[contains(@wit, $ms)][contains(@xml:id, $xml_id)])">
            <xsl:copy-of select="."/>
        </xsl:if>

        <!--Ajouter les ommissions-->
        <!--<xsl:if test="following-sibling::tei:w[1]"/>-->
        <!--Ajouter les ommissions-->
    </xsl:template>

    <xsl:template match="tei:pc">
        <xsl:apply-templates/>
    </xsl:template>

</xsl:stylesheet>
