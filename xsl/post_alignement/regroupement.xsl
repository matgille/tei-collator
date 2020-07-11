<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <!--Idée ici: regrouper les tokens alignés en un apparat grossier, qu'il reste à affiner. -->

    <!--Le fichier xml source est le résultat de la transformation du fichier de sortie de collatex (python) par dicttoxml.
    Voir le dépot de thèse.-->

    <!--Fichier de sortie: du xml qui ressemble vaguement à de la TEI avec des app et des rdg dedans. Tout est lieu variant: 
        il reste la grosse partie, à comparer les chaines de caractère pour décider si il y a variation ou pas.-->

    <xsl:output method="xml"/>
    <xsl:strip-space elements="*"/>




    <xsl:template match="/">
        <xsl:element name="texte">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="//table/item[position() > 1]/item"/>
    <xsl:template match="//witnesses"/>

    <!--A. On prend le premier témoin comme base.-->
    <xsl:template match="//table/item[1]/item">
        <xsl:element name="app" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:variable name="position"
                select="count(preceding::item[parent::item[not(parent::item)]]) + 1"/>
            <xsl:attribute name="position" select="$position"/>
            <xsl:choose>
                <!--Si l'item est vide, créer un element rdg parent d'une balise vide om-->
                <xsl:when test="@type = 'null'">
                    <xsl:element name="rdg" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:variable name="temoin0"
                            select="ancestor::item[parent::table]/position()"/>
                        <xsl:variable name="temoin"
                            select="ancestor::root/descendant::witnesses/item[position() = $temoin0]"/>
                        <xsl:attribute name="wit">
                            <xsl:value-of select="concat('#', $temoin)"/>
                        </xsl:attribute>
                        <xsl:element name="om"/>
                    </xsl:element>
                </xsl:when>
                <!--Si l'item est vide, créer un element rdg parent d'une balise vide om-->

                <!--Sinon, créer une balise rdg et y mettre les token, un par element w, et injecter
                l'identifiant unique dans un @xml:id-->
                <xsl:otherwise>
                    <xsl:element name="rdg" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:attribute name="wit">
                            <xsl:value-of select="concat('#', descendant::_sigil[1])"/>
                        </xsl:attribute>
                        <xsl:for-each select="item">
                            <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
                                <xsl:attribute name="xml:id">
                                    <xsl:value-of select="descendant::xml:id"/>
                                </xsl:attribute>
                                <xsl:if test="descendant::n">
                                    <xsl:attribute name="lemma">
                                        <xsl:value-of select="descendant::n"/>
                                    </xsl:attribute>
                                </xsl:if>
                                <xsl:if test="descendant::pos">
                                    <xsl:attribute name="pos">
                                        <xsl:value-of select="descendant::pos"/>
                                    </xsl:attribute>
                                </xsl:if>
                                <xsl:value-of select="descendant::t"/>
                            </xsl:element>
                        </xsl:for-each>
                    </xsl:element>
                </xsl:otherwise>
                <!--Sinon, créer une balise rdg et y mettre les token-->
            </xsl:choose>

            <!--B. Pour chaque item de meme position, répéter les memes règles-->
            <xsl:for-each select="//table/item[position() > 1]/item[position() = $position]">
                <xsl:choose>
                    <!--Si l'item est vide...-->
                    <xsl:when test="@type = 'null'">
                        <xsl:element name="rdg" namespace="http://www.tei-c.org/ns/1.0">
                            <!--Ceci marche mais je ne sais absolument pas pourquoi. Idée: chercher la position du témoin correspondant-->
                            <xsl:variable name="temoin0" select="position() + 1"/>
                            <!--Ceci marche mais je ne sais absolument pas pourquoi.-->
                            <!--Aller chercher le nom du témoin correspondant-->
                            <xsl:variable name="temoin"
                                select="ancestor::root/descendant::witnesses/item[position() = $temoin0]"/>
                            <!--Aller chercher le témoin correspondant-->
                            <xsl:attribute name="wit">
                                <xsl:value-of select="concat('#', $temoin)"/>
                            </xsl:attribute>
                            <xsl:element name="om"/>
                        </xsl:element>
                    </xsl:when>
                    <!--Si l'item est vide...-->

                    <!--Sinon, créer les rdg par témoin et y mettre les w-->
                    <xsl:otherwise>
                        <xsl:element name="rdg" namespace="http://www.tei-c.org/ns/1.0">
                            <xsl:attribute name="wit">
                                <xsl:value-of select="concat('#', descendant::_sigil[1])"/>
                            </xsl:attribute>
                            <xsl:for-each select="item">
                                <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
                                    <xsl:attribute name="xml:id">
                                        <xsl:value-of select="descendant::xml:id"/>
                                    </xsl:attribute>
                                    <xsl:if test="descendant::n">
                                        <xsl:attribute name="lemma">
                                            <xsl:value-of select="descendant::n"/>
                                        </xsl:attribute>
                                    </xsl:if>
                                    <xsl:if test="descendant::pos">
                                        <xsl:attribute name="pos">
                                            <xsl:value-of select="descendant::pos"/>
                                        </xsl:attribute>
                                    </xsl:if>
                                    <xsl:value-of select="descendant::t"/>
                                </xsl:element>
                            </xsl:for-each>
                        </xsl:element>
                    </xsl:otherwise>
                    <!--Sinon, créer les rdg par témoin et y mettre les w-->
                </xsl:choose>
            </xsl:for-each>
            <!--B. Pour chaque item de meme position, répéter les memes règles-->
        </xsl:element>
    </xsl:template>



</xsl:stylesheet>
