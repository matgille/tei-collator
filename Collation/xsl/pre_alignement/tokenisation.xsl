
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0">
    <xsl:output indent="no"/>
    <xsl:strip-space elements="*"/>
    <!--Première phase de la tokénisation: -->
    <!--Méthode suivie: sur suggestion de Marjorie Burghart, le "multi-pass" https://stackoverflow.com/a/8215981-->
    <!--Première Passe-->
    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="/" mode="premierePasse">
        <xsl:apply-templates/>
    </xsl:template>



    <xsl:variable name="ResultatPremierePasse">
        <xsl:apply-templates select="/" mode="premierePasse"/>
    </xsl:variable>




    <xsl:template match="tei:TEI[@type = 'transcription']">
        <xsl:element name="TEI" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="xml:id" select="@xml:id"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>



    <!--Première Passe-->





    <!--Seconde Passe-->


    <xsl:variable name="ResultatSecondePasse">
        <xsl:apply-templates select="$ResultatPremierePasse" mode="secondePasse"/>
    </xsl:variable>

    <xsl:template match="@* | node()" mode="secondePasse">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates mode="secondePasse" select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="tei:hi[following-sibling::text()][@rend = 'lettrine']" mode="secondePasse">
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:copy-of select="."/>
            <xsl:value-of select="substring-before(following-sibling::text()[1], ' ')"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="tei:hi[@rend = 'lettre_attente']" mode="secondePasse">
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:copy-of select="."/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="tei:hi[@rend = 'souligne']">
        <xsl:element name="hi" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="rend">souligne</xsl:attribute>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>

    <!--Ici commencent les problèmes d'overlapping-->
    <xsl:template match="tei:hi[@rend = 'souligne' or @rend = 'rubrique']">
        <xsl:element name="hi" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="rend" select="@rend"/>
            <xsl:apply-templates/>
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


    <xsl:variable name="ResultatTroisiemePasse">
        <xsl:apply-templates select="$ResultatSecondePasse" mode="troisiemePasse"/>
    </xsl:variable>


    <xsl:template match="@* | node()" mode="troisiemePasse">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates mode="troisiemePasse" select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="tei:w[preceding-sibling::tei:w[1][tei:hi][text() = text()]]"
        mode="troisiemePasse"/>

    <xsl:template match="tei:lb[@break = 'n'] | tei:pb[@break = 'n']" mode="troisiemePasse">
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:value-of select="preceding-sibling::tei:w[1]"/>
            <xsl:copy-of select="."/>
            <xsl:value-of select="following-sibling::tei:w[1]"/>
        </xsl:element>
    </xsl:template>


    <!--Troisième Passe-->


    <!--Quatrième passe: travail sur les tei:lb et les tei:w-->


    <xsl:template match="@* | node()" mode="quatriemePasse">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates mode="quatriemePasse" select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <xsl:for-each select="//tei:TEI[@type = 'transcription']">
            <xsl:variable name="nom_fichier" select="@xml:id"/>
            <xsl:result-document href="../temoins_tokenises/{$nom_fichier}.xml">
                <xsl:apply-templates
                    select="$ResultatTroisiemePasse//tei:TEI[@xml:id = $nom_fichier]"
                    mode="quatriemePasse" xpath-default-namespace="tei"/>
            </xsl:result-document>
        </xsl:for-each>
    </xsl:template>



    <xsl:template
        match="tei:w[following-sibling::tei:w[1][child::tei:pb]] | tei:w[preceding-sibling::tei:w[1][child::tei:pb]] | tei:w[following-sibling::tei:w[1][child::tei:lb]] | tei:w[preceding-sibling::tei:w[1][child::tei:lb]]"
        mode="quatriemePasse"/>


    <!--        <xsl:template match="tei:w[following-sibling::tei:lb[1]]" mode="troisiemePasse"/>-->


    <!--Quatrième passe-->



</xsl:stylesheet>
