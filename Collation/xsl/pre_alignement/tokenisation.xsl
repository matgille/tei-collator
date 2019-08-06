<?xml version="1.0" encoding="UTF-8"?>

<!--Feuille XSL qui permet de tokeniser la source.-->
<!--étape 1: tokeniser.-->
<!--Reste à gérer la ponctuation (seule est conservée celle qui finit un noeud comme un p), 
    les mots coupés par des balises.-->
<!--Il faut deux niveaux de tokenisation: un niveau où on conserve tout (qui va reservir à la fin pour la réinjection), 
et un niveau où on élimine le bruit (choix des choice, etc). Sinon, on perd de l'information: les choice > sic par exemples-->
<!--à faire, URGENT: 1) nettoyer la feuille et 2) créer une sécurité pour ne pas perdre tout le travail en re-tokenisant
avec de nouveaux xml:id. Faire une feuille de comparaison: si le token existe, ne pas recréer un identifiant par exemple, 
simplement actualiser le texte -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs tei" version="2.0"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:xf="http://www.w3.org/2002/xforms"
    xmlns:f="urn:stylesheet-func">
    <xsl:strip-space elements="*"/>
    <!--    <xsl:output doctype-system="Sal_J.dtd"/>-->




    <xsl:template match="/">
        <xsl:result-document href="../temoins/groupe.xml">
            <xsl:element name="group">
                <xsl:apply-templates xpath-default-namespace="tei"/>
            </xsl:element>
        </xsl:result-document>
    </xsl:template>

    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="tei:choice">
        <xsl:apply-templates select="tei:reg"/>
        <xsl:apply-templates select="tei:expan"/>
        <xsl:apply-templates select="tei:corr"/>
    </xsl:template>

    <xsl:template match="tei:text">
        <text xml:id="{ancestor::tei:TEI/@xml:id}">
            <xsl:apply-templates/>
        </text>
    </xsl:template>

    <!--    <!-\-Conserver les commentaires pour ne pas perdre d'information-\->
    <xsl:template match="comment()">
        <xsl:comment><xsl:value-of select="."/></xsl:comment>
    </xsl:template>-->
    <!--problème de tokénisation: les virgules-->
    <xsl:template match="tei:TEI[@type = 'bibliographie'] | tei:TEI[@type = 'these']"/>

    <xsl:template match="tei:TEI[@type = 'transcription']">
        <xsl:element name="TEI" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:apply-templates/>
        </xsl:element>


        <!-- <xsl:analyze-string select="." regex="([.,:;!?])">
            <xsl:matching-substring>
                <xsl:element name="pct">
                    <xsl:attribute name="xml:id">a<xsl:value-of
                        select="substring-before(uuid:randomUUID(), '-')"/></xsl:attribute>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:element>
                <xsl:element name="w">
                    <xsl:attribute name="xml:id">a<xsl:value-of
                        select="substring-before(uuid:randomUUID(), '-')"/></xsl:attribute>
                    <xsl:value-of select="regex-group(2)"/>
                </xsl:element>
            </xsl:matching-substring>
        </xsl:analyze-string>-->
    </xsl:template>


    <!--On procède en deux temps: d'abord, tokeniser avec espace comme séparateur. Puis on analyse la chaîne produite
    et on en extrait la ponctuation-->
    <!--Pour l'instant la ponctuation n'est pas prise en compte dans la collation, étant donné qu'hormis l'incunable, elle
    est du fait de l'éditeur (moi).-->
    <xsl:template match="text()[not(ancestor::tei:note)][not(ancestor::tei:teiHeader)]">
        <xsl:for-each select="tokenize(., '\s+')">
            <xsl:analyze-string select="." regex="([:,;¿?.])">
                <xsl:matching-substring>
                    <xsl:element name="pct" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:value-of select="regex-group(1)"/>
                    </xsl:element>
                </xsl:matching-substring>
                <xsl:non-matching-substring>
                    <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:value-of select="."/>
                    </xsl:element>
                </xsl:non-matching-substring>
            </xsl:analyze-string>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="tei:teiHeader"/>

</xsl:stylesheet>
