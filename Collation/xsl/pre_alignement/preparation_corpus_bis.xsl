<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs tei" version="2.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:xf="http://www.w3.org/2002/xforms"
    xmlns:f="urn:stylesheet-func">

    <xsl:strip-space elements="*"/>
    <xsl:param name="temoin_leader">''Sal_J''</xsl:param>
    <xsl:param name="element_scission">tei:div[@type='chapitre']</xsl:param>
    <xsl:param name="scinder_par">div</xsl:param>
    <xsl:param name="element_base">tei:p</xsl:param>

    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="/">
        <!--On crée un fichier où les encodages sont juxtaposés, pour après le convertir en json
        selon ce que requiert CollateX-->
        <xsl:result-document href="log.txt">
            <xsl:value-of
                select="concat('collection(../../temoins_tokenises_regularises?select=*.xml)//tei:TEI[@xml:id = ''Sal_J'']//', $element_scission, '//', $element_base)"/>
            <xsl:choose>
                <xsl:when
                    test="collection('../../temoins_tokenises_regularises?select=*.xml')//tei:TEI[@xml:id = 'Sal_J']//tei:div[@type = 'chapitre']//tei:p"
                    >Oui</xsl:when>
                <xsl:otherwise>Non</xsl:otherwise>
            </xsl:choose>
        </xsl:result-document>
        <xsl:for-each
            select="collection('../../temoins_tokenises_regularises?select=*.xml')//tei:TEI[@xml:id = 'Sal_J']//tei:div[@type = 'chapitre']//tei:p">
            <!--collection('../../../temoins_tokenises_regularises?select=*.xml')//tei:TEI[@xml:id = $temoin_leader]//$element_scission//$element_base-->
            <xsl:variable name="ident_paragraphe" select="@n"/>
            <xsl:variable name="chapitre_courant" select="ancestor::tei:div[@type = 'chapitre']/@n"/>
            <xsl:variable name="ident"
                select="count(preceding::tei:p[ancestor::tei:div[@type = 'chapitre'][@n = $chapitre_courant]]) + 1"/>
            <xsl:variable name="numero" select="ancestor::tei:div[@type = 'chapitre']/@n"/>
            <xsl:result-document
                href="{$scinder_par}s/{$scinder_par}{$numero}/juxtaposition_{$ident}.xml">
                <xsl:element name="groupe">
                    <xsl:element name="temoin">
                        <xsl:attribute name="n">
                            <xsl:value-of select="ancestor::tei:TEI/@xml:id"/>
                        </xsl:attribute>
                        <xsl:apply-templates/>
                    </xsl:element>
                    <xsl:for-each
                        select="collection('../../temoins_tokenises_regularises?select=*.xml')//tei:TEI[not(@xml:id = 'Sal_J')]//tei:div[@type = 'chapitre']//tei:p[@n = $ident_paragraphe]">
                        <!--collection('../../../temoins_tokenises_regularises?select=*.xml')//tei:TEI[not(@xml:id = $temoin_leader)]//$element_scission[@n = $ident]//$element_base[@n = $numero]-->
                        <xsl:element name="temoin">
                            <xsl:attribute name="n">
                                <xsl:value-of select="ancestor::tei:TEI/@xml:id"/>
                            </xsl:attribute>
                            <xsl:apply-templates/>
                        </xsl:element>
                    </xsl:for-each>
                </xsl:element>
            </xsl:result-document>
        </xsl:for-each>
        <!--On a besoin d'avoir le corpus à la fois régularisé pour collatex (suppresion des choice, etc) mais on 
        veut conserver la structuration d'origine pour la réinjection: on va créer un fichier
        juxtaposition_orig qui va nous servir de fichier base pour réinjecter les informations contextuelles.-->
        <xsl:for-each
            select="collection('../../temoins_tokenises?select=*.xml')//tei:TEI[@xml:id = 'Sal_J']//tei:div[@type = 'chapitre']">
            <xsl:variable name="numero_chapitre" select="@n"/>
            <xsl:result-document
                href="{$scinder_par}s/{$scinder_par}{$numero_chapitre}/juxtaposition_orig.xml">
                <xsl:element name="groupe">
                    <xsl:element name="temoin">
                        <xsl:attribute name="n">
                            <xsl:value-of select="ancestor::tei:TEI/@xml:id"/>
                        </xsl:attribute>
                        <xsl:apply-templates/>
                    </xsl:element>
                    <xsl:for-each
                        select="collection('../../temoins_tokenises?select=*.xml')//tei:TEI[not(@xml:id = 'Sal_J')]//tei:div[@type = 'chapitre'][@n = $numero_chapitre]">
                        <xsl:element name="temoin">
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
