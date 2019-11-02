<?xml version="1.0" encoding="UTF-8"?>
<!--Première phase de l'injection: récupération des apparats et des noeuds textuels uniquement
plus suppression de la redondance-->

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
    <xsl:param name="chemin_sortie"/>
    <xsl:param name="chapitre" select="21"/>


    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
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


        <!--Suppression de la redondance: si le token a déjà été rencontré, ne rien faire.-->
        <!--Si c'est la première occurrence du token, copier le noeud trouvé dans le document
        apparat_collatex.xml-->
        <xsl:variable name="token_precedent">
            <xsl:choose>
                <xsl:when test="preceding::tei:w[1]">
                    <xsl:value-of select="preceding::tei:w[1]/@xml:id"/>
                </xsl:when>
                <xsl:otherwise>False</xsl:otherwise>
            </xsl:choose>
        </xsl:variable>


        <xsl:variable name="recuperation_apparat">
            <xsl:for-each select="document($apparat_chapitre)//tei:rdg[contains(@wit, $ms)]/tei:w">
                <xsl:choose>
                    <xsl:when test="contains(@xml:id, $xml_id)">
                        <xsl:choose>
                            <!--Si le token trouvé a été traité (il appartient à un rdg qui compte un autre
                            w traité auparavant), on ne fait rien-->
                            <xsl:when test="contains(parent::tei:rdg/@xml:id, $token_precedent)">
                                <xsl:text>Redondance</xsl:text>
                            </xsl:when>
                            <!--Si le token trouvé a été traité-->
                            
                            <!--Si le token trouvé n'a pas été traité: on copie l'apparat (donc
                                l'ensemble des noeuds tei:w fils, d'où la nécessité de
                                réduire la redondance)-->
                            <xsl:otherwise>
                                <xsl:copy-of select="ancestor::tei:app"/>
                            </xsl:otherwise>
                            <!--Si le token trouvé n'a pas été traité: on copie l'apparat-->
                        </xsl:choose>
                    </xsl:when>
                    <!--Si le token n'a pas été trouvé, c'est qu'il n'est pas dans un apparat-->
                    <xsl:otherwise/>
                    <!--On va donc copier le noeud tei:w uniquement-->
                </xsl:choose>
            </xsl:for-each>
        </xsl:variable>

        <xsl:choose>
            <xsl:when test="$recuperation_apparat = ''">
                <xsl:copy-of select="."/>
            </xsl:when>
            <xsl:when test="$recuperation_apparat = 'Redondance'"/>
            <xsl:otherwise>
                <xsl:copy-of select="$recuperation_apparat"/>
            </xsl:otherwise>
        </xsl:choose>
        <!--Suppression de la redondance: si le token a déjà été rencontré, ne rien faire.-->

        <!--Ajouter les ommissions-->
        <!--<xsl:if test="following-sibling::tei:w[1]"/>-->
        <!--Ajouter les ommissions-->
    </xsl:template>


    <!--Création des différents fichiers xml par témoin-->
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
    <!--Création des différents fichiers xml par témoin-->




</xsl:stylesheet>
