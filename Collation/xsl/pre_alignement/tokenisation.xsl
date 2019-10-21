
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output indent="yes"/>
    <xsl:strip-space elements="*"/>
    <!--Première phase de la tokénisation: -->
    <!--Méthode suivie: sur suggestion de Marjorie Burghart, le "multi-pass" https://stackoverflow.com/a/8215981-->
    <!--Première Passe-->
    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="/" mode="PremierePasse">
        <xsl:apply-templates/>
    </xsl:template>



    <xsl:variable name="ResultatPremierePasse">
        <xsl:apply-templates select="/" mode="PremierePasse"/>
    </xsl:variable>



    <xsl:template match="//comment()" mode="PremierePasse">
        <xsl:comment><xsl:value-of select="."/></xsl:comment>
    </xsl:template>


    <xsl:template match="tei:TEI[@type = 'transcription']">
        <xsl:element name="TEI" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="xml:id" select="@xml:id"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>


    <!--Première Passe-->





    <!--Seconde Passe-->


    <xsl:variable name="ResultatSecondePasse">
        <xsl:apply-templates select="/" mode="secondePasse"/>
    </xsl:variable>

    <xsl:template match="@* | node()" mode="secondePasse">
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates mode="secondePasse" select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template
        match="tei:hi[following-sibling::text()][not(@rend = 'rubrique')][not(@rend = 'souligne')]"
        mode="secondePasse">
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:copy-of select="."/>
            <xsl:value-of select="substring-before(following-sibling::text()[1], ' ')"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="tei:choice" mode="secondePasse">
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:value-of select="substring-after(preceding-sibling::text()[-1], ' ')"/>
            <xsl:copy-of select="."/>
            <xsl:value-of select="substring-before(following-sibling::text()[1], ' ')"/>
        </xsl:element>
    </xsl:template>

    <!--On procède en deux temps: d'abord, tokeniser avec espace comme séparateur. Puis on analyse la chaîne produite
    et on en extrait la ponctuation-->
    <!--Pour l'instant la ponctuation n'est pas prise en compte dans la collation, étant donné qu'hormis l'incunable, elle
    est du fait de l'éditeur (moi).-->
    <xsl:template
        match="text()[not(ancestor::tei:note)][not(ancestor::tei:teiHeader)][not(ancestor::tei:w)][not(ancestor::tei:desc)]"
        mode="secondePasse">
        <xsl:for-each select="tokenize(., '\s+')">
            <xsl:analyze-string select="." regex="([:,;¿?.])">
                <xsl:matching-substring>
                    <xsl:element name="pc" namespace="http://www.tei-c.org/ns/1.0">
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


    <!--Seconde Passe-->



    <!--Troisième Passe: division du document, suppression des doublons-->

    <xsl:template match="/">
        <xsl:for-each select="//tei:TEI[@type = 'transcription']">
            <xsl:variable name="nom_fichier" select="@xml:id"/>
            <xsl:result-document href="../temoins_tokenises/{$nom_fichier}.xml">
                <xsl:apply-templates select="$ResultatSecondePasse//tei:TEI[@xml:id = $nom_fichier]"
                    mode="troisiemePasse" xpath-default-namespace="tei"/>
            </xsl:result-document>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="@* | node()" mode="troisiemePasse">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates mode="troisiemePasse" select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="tei:w[preceding-sibling::tei:w[1][tei:hi][text() = text()]]"
        mode="troisiemePasse"/>

    <!--Troisième Passe-->





</xsl:stylesheet>
