<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <!--Idée ici: regrouper les tokens alignés en un apparat grossier, qu'il reste à affiner. -->
    <!--Le fichier xml source est le résultat de la transformation du fichier de sortie de collatex (python) par dicttoxml.-->

    <xsl:output method="xml"/>
    <xsl:strip-space elements="*"/>
    <xsl:template match="/">
        <xsl:element name="texte">
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="//table/item[position() > 1]/item"/>
    <xsl:template match="//witnesses"/>

    <!--On fonctionne avec le premier témoin comme base-->
    <xsl:template match="//table/item[1]/item">
        <xsl:element name="app">
            <xsl:variable name="position"
                select="count(preceding::item[parent::item[not(parent::item)]]) + 1"/>
            <xsl:attribute name="position" select="$position"/>
            <xsl:choose>
                <xsl:when test="@type = 'null'">
                    <xsl:element name="rdg">
                        <xsl:variable name="temoin0"
                            select="ancestor::item[parent::table]/position()"/>
                        <xsl:variable name="temoin"
                            select="ancestor::root/descendant::witnesses/item[position() = $temoin0]"/>
                        <xsl:attribute name="wit">
                            <xsl:value-of select="$temoin"/>
                        </xsl:attribute>
                        <xsl:element name="om"/>
                    </xsl:element>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:element name="rdg">
                        <xsl:attribute name="wit">
                            <xsl:value-of select="descendant::_sigil[1]"/>
                        </xsl:attribute>
                        <xsl:for-each select="item">
                            <xsl:element name="w">
                                <xsl:attribute name="xml:id">
                                    <xsl:value-of select="descendant::xmlid"/>
                                </xsl:attribute>
                                <xsl:value-of select="descendant::t"/>
                            </xsl:element>
                        </xsl:for-each>
                    </xsl:element>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:for-each select="//table/item[position() > 1]/item[position() = $position]">
                <xsl:choose>
                    <xsl:when test="@type = 'null'">
                        <xsl:element name="rdg">
                            <!--Ceci marche mais je ne sais absolument pas pourquoi. Idée: chercher la position du témoin correspondant-->
                            <xsl:variable name="temoin0" select="position() + 1"/>
                            <!--Ceci marche mais je ne sais absolument pas pourquoi.-->
                            <!--Aller chercher le nom du témoin correspondant-->
                            <xsl:variable name="temoin"
                                select="ancestor::root/descendant::witnesses/item[position() = $temoin0]"/>
                            <!--Aller chercher le témoin correspondant-->
                            <xsl:attribute name="wit">
                                <xsl:value-of select="$temoin"/>
                            </xsl:attribute>
                            <xsl:element name="om"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element name="rdg">
                            <xsl:attribute name="wit">
                                <xsl:value-of select="descendant::_sigil[1]"/>
                            </xsl:attribute>
                            <xsl:for-each select="item">
                                <xsl:element name="w">
                                    <xsl:attribute name="xml:id">
                                        <xsl:value-of select="descendant::xmlid"/>
                                    </xsl:attribute>
                                    <xsl:value-of select="descendant::t"/>
                                </xsl:element>
                            </xsl:for-each>
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
        </xsl:element>
    </xsl:template>

</xsl:stylesheet>
