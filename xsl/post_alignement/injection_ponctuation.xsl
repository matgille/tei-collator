<?xml version="1.0" encoding="UTF-8"?>
<!--Cette feuille est la troisième phase d'injection: on ajoute la ponctuation en comparant le
fichier précédent avec la transcription tokenisée originelle. 
Résultat: un fichier final qui marche !-->

<!--TODO: ajouter une règle pour choper les notes de type général !-->
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="xml"/>
    <xsl:strip-space elements="*"/>

    <xsl:param name="chapitre" select="'20'"/>
    <xsl:param name="chemin_sortie">
        <xsl:text>divs/div</xsl:text>
        <xsl:value-of select="$chapitre"/>
        <xsl:text>/</xsl:text>
    </xsl:param>
    <xsl:param name="chemin_sortie2" select="''"/>
    <xsl:param name="sigle" select="'Sal_J'"/>


    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <xsl:result-document
            href="{$chemin_sortie}apparat_{$sigle}_{$chapitre}_out.xml">
            <xsl:apply-templates/>
        </xsl:result-document>
    </xsl:template>


    <!--Redondance de la ponctuation-->
    <xsl:template
        match="tei:pc[preceding::*[1][self::tei:w]] | tei:pc[preceding-sibling::*[1][self::tei:app]]"/>
    <!--Redondance de la ponctuation-->



    <!--On prend chaque token, et si un élément de ponctuation suit, on copie le token et la ponctuation-->
    <xsl:template match="tei:w[not(@xml:id = 'none')]">
        <xsl:variable name="ms"
            select="ancestor::*:temoin/@n"/>
        <xsl:variable name="xml_id" select="@xml:id"/>
        <!--Attention ici, on romp l'universalisation du code-->
        <xsl:variable name="paragraphe"
            select="ancestor::tei:p/@n"/>
        <!--Attention ici, on romp l'universalisation du code-->
        <xsl:variable name="temoins"
            >../../temoins_tokenises?select=*.xml</xsl:variable>
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
                <xsl:copy-of
                    select="document($temoin_tokenise)//tei:w[contains($xml_id, @xml:id)]/following::*[1][self::tei:pb]"
                />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    <!--On prend chaque token, et si un élément de ponctuation suit, on copie le token et la ponctuation-->






    <!--On concentre les balises qui se retrouvent à entourer un lieu variant, comme un tei:sic alors qu'elles devraient
        porter sur le témoin base. 
        Vérifier que ça ne casse rien  + mettre à part ? -->
    <xsl:template
        match="tei:*[not(self::tei:p)][count(child::node()) = 1][child::tei:app]">
        <xsl:element name="app"
            namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="type">
                <xsl:value-of select="tei:app/@type"/>
            </xsl:attribute>
            <xsl:element name="rdg"
                namespace="http://www.tei-c.org/ns/1.0">
                <xsl:attribute name="id">
                    <xsl:value-of
                        select="descendant::tei:rdg[contains(@wit, concat('#', $sigle))]/@id"
                    />
                </xsl:attribute>
                <xsl:attribute name="wit">
                    <xsl:value-of
                        select="descendant::tei:rdg[contains(@wit, concat('#', $sigle))]/@wit"
                    />
                </xsl:attribute>
                <xsl:attribute name="lemma">
                    <xsl:value-of
                        select="descendant::tei:rdg[contains(@wit, concat('#', $sigle))]/@lemma"
                    />
                </xsl:attribute>
                <xsl:attribute name="pos">
                    <xsl:value-of
                        select="descendant::tei:rdg[contains(@wit, concat('#', $sigle))]/@pos"
                    />
                </xsl:attribute>
                <xsl:element name="{name(.)}"
                    namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:copy-of
                        select="descendant::tei:rdg[contains(@wit, concat('#', $sigle))]/child::*"
                    />
                </xsl:element>
            </xsl:element>
            <xsl:for-each
                select="descendant::tei:rdg[not(contains(@wit, concat('#', $sigle)))]">
                <xsl:copy-of select="."/>
            </xsl:for-each>
        </xsl:element>
    </xsl:template>
    <!--On concentre les balises qui entourent un lieu variant comme un sic pour les faire porter sur le témoin base-->
    <!--L'idéal serait de pouvoir appliquer cela à tous les lieux variants pour avoir une vrai apparat enrichi. Pour l'instant, 
    on n'a que le témoin base qui est enrichi de son propre encodage. Le faire avec etree, ce sera probablement plus facile.-->



</xsl:stylesheet>
