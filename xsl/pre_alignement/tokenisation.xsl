
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:cw="chezwam"
    xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xsl:output method="xml" indent="no"/>
    <xsl:strip-space elements="*"/>
    <!--Première phase de la tokénisation: -->
    <!--Méthode suivie: sur suggestion de Marjorie Burghart, le "multi-pass" https://stackoverflow.com/a/8215981-->
    <!--Problèmes à régler: tei:cb suivi de tei:lb ne tokénise pas comme il faut.-->
    <!--Première Passe-->
    <!--Il serait probablement plus simple de passer par du python pour faire ça-->
    <!--Une possibilité à envisager: on extrait paragraphe par paragraphe, 
        on convertir en chaîne de caractère et on fait ça avec des expressions régulières-->
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




    <xsl:template
        match="tei:TEI[@type = 'transcription'][not(descendant::tei:text[@xml:lang = 'la'])]">
        <xsl:element name="TEI" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="xml:id" select="@xml:id"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>



    <!--Première Passe-->





    <!--Seconde Passe-->


    <xsl:variable name="ResultatSecondePasse">
        <xsl:apply-templates select="$ResultatPremierePasse" mode="secondePasse"
        />
    </xsl:variable>

    <xsl:template match="@* | node()" mode="secondePasse">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates mode="secondePasse" select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <!--<xsl:template
        match="tei:hi[following-sibling::text()][not(following-sibling::tei:hi[@rend = 'lettre_capitulaire'])][@rend = 'lettrine']"
        mode="secondePasse">
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:copy-of select="."/>
            <xsl:value-of select="substring-before(following-sibling::text()[1], ' ')"/>
        </xsl:element>
    </xsl:template>-->

    <!--Il faut faire la même chose avec les unclear|damage|add-->
    <!--Qu'est-ce que le texte: c'est ici ce que tu va processer. Donc un élément éliminé marqué par un <del> n'est pas le texte-->
    <!--Meilleure idée: plutôt que les supprimer, les traiter comme une note (pas de tokénisation donc)-->
    <xsl:template match="tei:hi[following-sibling::text()][@rend = 'lettrine']"
        mode="secondePasse">
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:copy-of
                select="preceding-sibling::tei:hi[@rend = 'lettre_attente']"/>
            <xsl:copy-of select="."/>
            <xsl:copy-of
                select="following-sibling::tei:hi[@rend = 'lettre_capitulaire']"/>
            <xsl:value-of
                select="substring-before(following-sibling::text()[1], ' ')"/>
        </xsl:element>
    </xsl:template>


    <xsl:template
        match="tei:hi[@rend = 'lettre_attente'] | tei:hi[@rend = 'lettre_capitulaire']"
        mode="secondePasse"/>

    <!--https://stackoverflow.com/questions/17468891/substring-after-last-character-in-xslt-->
    <xsl:function name="cw:substring-after-last" as="xs:string"
        xmlns:cw="chezwam">
        <xsl:param name="value" as="xs:string?"/>
        <xsl:param name="separator" as="xs:string"/>
        <xsl:choose>
            <xsl:when test="contains($value, $separator)">
                <xsl:value-of
                    select="cw:substring-after-last(substring-after($value, $separator), $separator)"
                />
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$value"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:function>
    <!--
    <xsl:template match="tei:anchor[not(substring(following-sibling::text()[1], 1) = ' ')]">
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:value-of select="cw:substring-after-last(preceding-sibling::text()[1], ' ')"/>
            <xsl:if test="preceding-sibling::*[1][self::tei:lb]">
                <xsl:copy-of select="preceding-sibling::*[1][self::tei:lb]"/>
            </xsl:if>
            <xsl:copy-of select="."/>
            <xsl:if test="following-sibling::*[1][self::tei:lb]">
                <xsl:copy-of select="following-sibling::*[1][self::tei:lb]"/>
            </xsl:if>
            <xsl:value-of select="substring-before(following-sibling::text()[1], ' ')"/>
        </xsl:element>
    </xsl:template>
-->

    <!--Ici commencent les problèmes d'overlapping-->
    <xsl:template match="tei:hi[@rend = 'souligne' or @rend = 'rubrique']">
        <xsl:element name="hi" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="rend" select="@rend"/>
            <xsl:apply-templates/>
        </xsl:element>
    </xsl:template>


    <xsl:template match="tei:choice" mode="secondePasse">
        <!--Si on a un corr avec plusieurs mots, ça peut planter. Reprendre le code.-->
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:value-of
                select="substring-after(preceding-sibling::text()[-1], ' ')"/>
            <xsl:copy-of select="."/>
            <xsl:if
                test="not(contains(',.;?!¡¿', substring-before(following-sibling::text()[1], ' ')))">
                <xsl:value-of
                    select="substring-before(following-sibling::text()[1], ' ')"
                />
            </xsl:if>
            <!--Attention à ne pas copier un élément de ponctuation par mégarde-->
        </xsl:element>
    </xsl:template>

    <!--On procède en deux temps: d'abord, tokeniser avec espace comme séparateur. Puis on analyse la chaîne produite
    et on en extrait la ponctuation-->
    <xsl:template
        match="text()[not(ancestor::tei:note)][not(ancestor::tei:teiHeader)][not(ancestor::tei:w)][not(ancestor::tei:desc)]"
        mode="secondePasse">
        <xsl:for-each select="tokenize(., '\s+')">
            <xsl:analyze-string select="." regex="([():,;¿?!¡.])">
                <xsl:matching-substring>
                    <xsl:element name="pc"
                        namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:value-of select="regex-group(1)"/>
                    </xsl:element>
                </xsl:matching-substring>
                <xsl:non-matching-substring>
                    <xsl:element name="w"
                        namespace="http://www.tei-c.org/ns/1.0">
                        <xsl:value-of select="."/>
                    </xsl:element>
                </xsl:non-matching-substring>
            </xsl:analyze-string>
        </xsl:for-each>
    </xsl:template>


    <!--Seconde Passe-->



    <!--Troisième Passe: division du document, suppression des doublons-->


    <xsl:variable name="ResultatTroisiemePasse">
        <xsl:apply-templates select="$ResultatSecondePasse"
            mode="troisiemePasse"/>
    </xsl:variable>


    <xsl:template match="@* | node()" mode="troisiemePasse">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates mode="troisiemePasse" select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template
        match="tei:w[preceding-sibling::tei:w[1][tei:hi][text() = text()]]"
        mode="troisiemePasse"/>
    <xsl:template
        match="tei:cb[@break = 'n'] | tei:lb[@break = 'n'] | tei:pb[@break = 'n']"
        mode="troisiemePasse">
        <!--<xsl:template
        match="tei:cb[@break = 'n'] | tei:lb[@break = 'n'][not(ancestor::tei:w)] | tei:pb[@break = 'n']"
        mode="troisiemePasse">-->
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:choose>
                <xsl:when test="preceding::tei:w[1]/child::text()">
                    <xsl:copy-of select="preceding::tei:w[1]/child::text()"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy-of select="preceding::tei:w[1]/child::node()"/>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:copy-of select="."/>
            <xsl:choose>
                <xsl:when test="following::tei:w[1]/child::text()">
                    <xsl:copy-of select="following::tei:w[1]/child::text()"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:copy-of select="following::tei:w[1]/child::node()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:element>
    </xsl:template>
    <!--
    <xsl:template match="tei:lb[@break = 'y'] | tei:pb[@break = 'y'] | tei:pb[not(@break)]"
        mode="troisiemePasse">
        <xsl:copy-of select="."/>
    </xsl:template>
-->

    <!--Troisième Passe-->


    <!--Quatrième passe: travail sur les tei:lb et les tei:w-->


    <xsl:template match="@* | node()" mode="quatriemePasse">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates mode="quatriemePasse" select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template
        match="tei:w[not(descendant::text())] | tei:w[preceding-sibling::tei:w[1][child::tei:pb[@break = 'n']]] | tei:w[preceding-sibling::tei:w[1][child::tei:lb[@break = 'n']]] | tei:w[preceding-sibling::tei:w[1][child::tei:cb[@break = 'n']]] | tei:w[following-sibling::tei:w[1][child::tei:pb[@break = 'n']]] | tei:w[following-sibling::tei:w[1][child::tei:lb[@break = 'n']]] | tei:w[following-sibling::tei:w[1][child::tei:cb[@break = 'n']]]"
        mode="quatriemePasse"/>



    <xsl:template match="/">
        <xsl:for-each
            select="//tei:TEI[@type = 'transcription'][not(descendant::tei:text[@xml:lang = 'la'])]">
            <xsl:variable name="nom_fichier" select="@xml:id"/>
            <xsl:result-document href="temoins_tokenises/{$nom_fichier}.xml">
                <xsl:apply-templates
                    select="$ResultatTroisiemePasse//tei:TEI[@xml:id = $nom_fichier]"
                    mode="quatriemePasse" xpath-default-namespace="tei"/>
            </xsl:result-document>
        </xsl:for-each>
    </xsl:template>





    <!--Quatrième passe-->



</xsl:stylesheet>