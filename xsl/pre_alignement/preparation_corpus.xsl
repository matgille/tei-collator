<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs tei" version="2.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:xf="http://www.w3.org/2002/xforms"
    xmlns:f="urn:stylesheet-func" xmlns:mgl="https://matthiasgillelevenson.fr">

    <xsl:strip-space elements="*"/>
    <xsl:param name="temoin_leader">Sal_J</xsl:param>
    <xsl:param name="type_division">chapitre</xsl:param>
    <xsl:param name="element_base"/>
    <xsl:param name="numero_div">23</xsl:param>
    <xsl:param name="compare_with_shifting">False</xsl:param>

    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="/">
        <!--On crée un fichier où les encodages sont juxtaposés, pour après le convertir en json
        selon ce que requiert CollateX-->
        <xsl:for-each
            select="collection('../../temoins_tokenises_regularises?select=*.xml')//tei:TEI[@xml:id = $temoin_leader]/descendant::tei:div[@type = $type_division][@n = $numero_div]/descendant::node()[name() = $element_base or name() = 'head']">
            <xsl:variable name="ident_paragraphe" select="@n"/>
            <xsl:variable name="ident"
                select="count((self::* | preceding::*)[name() = $element_base][ancestor::tei:div[@type = $type_division][@n = $numero_div]]) + 1"/>
            <xsl:result-document href="divs/div{$numero_div}/juxtaposition_{$ident}.xml">
                <xsl:element name="groupe" namespace="https://matthiasgillelevenson.fr">
                    <xsl:element name="temoin" namespace="https://matthiasgillelevenson.fr">
                        <xsl:attribute name="n">
                            <xsl:value-of select="ancestor::tei:TEI/@xml:id"/>
                        </xsl:attribute>
                        <xsl:apply-templates/>
                    </xsl:element>
                    <xsl:for-each
                        select="collection('../../temoins_tokenises_regularises?select=*.xml')//tei:TEI[not(@xml:id = $temoin_leader)]/descendant::tei:div[@type = $type_division]/descendant::node()[name() = $element_base or name() = 'head'][@n = $ident_paragraphe]">
                        <xsl:element name="temoin" namespace="https://matthiasgillelevenson.fr">
                            <xsl:attribute name="n">
                                <xsl:value-of select="ancestor::tei:TEI/@xml:id"/>
                            </xsl:attribute>
                            <xsl:choose>
                                <!--On gère les déplacements de texte ici, pour l'instant ça ne permet que la collation, pas la réinjection, trop complexe.-->
                                <xsl:when
                                    test="$compare_with_shifting = 'True' and ancestor::tei:TEI/descendant::tei:div[@type = $type_division]/descendant::node()[name() = $element_base or name() = 'head'][translate(@sameAs, '#', '') = $ident_paragraphe]">
                                    <xsl:apply-templates
                                        select="ancestor::tei:TEI/descendant::tei:div[@type = $type_division]/descendant::node()[name() = $element_base or name() = 'head'][translate(@sameAs, '#', '') = $ident_paragraphe]"/>
                                    <xsl:message>Dans ce chapitre, on a détecté un déplacement de
                                        paragraphe pour un ou plusieurs autres témoins. La lemmatisation
                                        de l'ensemble du corpus est donc nécessaire pour le bon
                                        fonctionnement de la collation.</xsl:message>
                                </xsl:when>
                                <!--On gère les déplacements de texte ici-->
                                <xsl:otherwise>
                                    <xsl:apply-templates/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:element>
                    </xsl:for-each>
                </xsl:element>
            </xsl:result-document>
        </xsl:for-each>


        <!--On a besoin d'avoir le corpus à la fois régularisé pour collatex (suppresion des choice, etc) mais on 
        veut conserver la structuration d'origine pour la réinjection: on va créer un fichier
        juxtaposition_orig qui va nous servir de fichier base pour réinjecter les informations contextuelles.-->
        <xsl:for-each
            select="collection('../../temoins_tokenises?select=*.xml')//tei:TEI[@xml:id = $temoin_leader]//tei:div[@type = $type_division][@n = $numero_div]">
            <xsl:result-document href="divs/div{$numero_div}/juxtaposition_orig.xml">
                <xsl:element name="groupe" namespace="https://matthiasgillelevenson.fr">
                    <xsl:element name="temoin" namespace="https://matthiasgillelevenson.fr">
                        <xsl:attribute name="n">
                            <xsl:value-of select="ancestor::tei:TEI/@xml:id"/>
                        </xsl:attribute>
                        <xsl:apply-templates/>
                    </xsl:element>
                    <xsl:for-each
                        select="collection('../../temoins_tokenises?select=*.xml')//tei:TEI[not(@xml:id = $temoin_leader)]//tei:div[@type = $type_division][@n = $numero_div]">
                        <xsl:element name="temoin" namespace="https://matthiasgillelevenson.fr">
                            <xsl:attribute name="n">
                                <xsl:value-of select="ancestor::tei:TEI/@xml:id"/>
                            </xsl:attribute>
                            <xsl:apply-templates/>
                        </xsl:element>
                    </xsl:for-each>
                </xsl:element>
            </xsl:result-document>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="tei:teiHeader | tei:facsimile"/>

</xsl:stylesheet>
