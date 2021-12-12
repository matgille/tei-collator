<?xml version="1.0" encoding="UTF-8"?>

<!-- IDEE: Gérer les modifications textuelles: Et si je faisais ma transformation en deux temps? D'abord, toutes les grosses transformations EN GARDANT UNE STRUCTURE XML BASIQUE
    et bien formée (une déclaration d'entité, etc) Sur cette transformation, en faire une seconde qui va supprimer tout ce qui est xml et garder que le texte ET qui 
pourra modifier les espaces simplement (translate ou un autre truc) ainsi qu'adapter les détails à LaTeX, comme les - - qui donne un tiret correct, ou transformer tous les e en &, etc-->

<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:tex="placeholder.uri" exclude-result-prefixes="tex">
    <!--RECOMMANDÉ: la feuille xsl est construite pour une utilisation du document .tex comme annexe 
        vers laquelle pointe le document principal (utilisant \input{...} par exemple).-->
    <!--IMPÉRATIF: Le package latex utilisé pour l'apparat est ednotes (https://www.ctan.org/pkg/ednotes). 
    Il doit impérativement être accompagné du package lineno (https://www.ctan.org/pkg/lineno)
    et du package manyfoot (https://www.ctan.org/pkg/manyfoot) pour 
    les différents niveaux de notes 
    (\DeclareNewFootnote{B}[arabic]
\usepackage{perpage}
\MakePerPage{footnote}
\renewcommand{\thefootnote}{\alph{footnote}} pour adapter le préambule LaTex à la feuille de transformation)
    , ainsi que du package marginpar (https://www.ctan.org/pkg/marginpar)
    pour permettre l'indication en marge des lacunes et des commencements/fins de témoins-->
    <!--Je propose mon preambule LaTex à l'adresse: http://perso.ens-lyon.fr/matthias.gille-levenson/preambule.txt. 
    Si le lien est périmé, me contacter sur mon adresse ens: matthias.gille-levenson[arobase]ens[point]fr -->
    <!--Cette feuille est adaptée à mon propre document XML-->
    <!--Merci à Arianne Pinche pour son aide précieuse dans cette feuille-->
    <!--Merci à Marjorie Burghart de m'avoir envoyé sa feuille de transformation qui m'a bien aidé-->
    <xsl:output method="text" omit-xml-declaration="no" encoding="UTF-8"/>
    <xsl:strip-space elements="*"/>
    <xsl:param name="fusion"/>

    <!--Variables concernant les omissions-->
    <xsl:variable name="omission_binaire">
        <xsl:text>#omission #binary</xsl:text>
    </xsl:variable>


    <!--Variables concernant les omissions-->


    <xsl:variable name="temoin_courant">
        <xsl:analyze-string select="//tei:div[@type = 'chapitre'][@xml:id]/@xml:id"
            regex="([A-Za-z]+_[a-zA-Z]+)(.*)">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
            </xsl:matching-substring>
        </xsl:analyze-string>
    </xsl:variable>


    <xsl:template match="/">
        <!--<xsl:text>\textbf{Sigles des témoins}\newline\newline</xsl:text>
        <xsl:for-each
            select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:listWit/tei:witness">
            <xsl:text>\noindent \textbf{</xsl:text>
            <xsl:value-of select="@xml:id"/>
            <xsl:text>}: </xsl:text>
            <xsl:value-of select="text()"/>
            <xsl:text>\newline </xsl:text>
        </xsl:for-each>-->
        <xsl:text>
            \documentclass[french,twoside,a4paper,12pt]{book}
        </xsl:text>
        <xsl:choose>
            <xsl:when test="$fusion = 'True'">\input{../latex/preambule.tex}</xsl:when>
            <!--Ça ne devrait pas marcher, bizarre.-->
            <xsl:otherwise>
                <xsl:text>\input{latex/preambule.tex}</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>
            \begin{document}
            \setstretch{1,1}
           <!-- changes the default format of the linenumbers-->
            \setcounter{chapter}{
        </xsl:text>
        <xsl:value-of select="tei:div/@n"/>
        <xsl:text>}</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>
        \end{document}</xsl:text>
    </xsl:template>


    <!--Revenir sur cette règle après attention qui nous fait perdre des notes !!!-->
    <xsl:template match="tei:note[parent::tei:head]"/>
    <!--Revenir sur cette règle après attention qui nous fait perdre des notes !!!-->

    <xsl:template match="tei:persName[@type = 'auteur']">
        <xsl:text>\textsc{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>
    <!--

    <xsl:template match="tei:alt">
        <xsl:variable name="proba">
            <xsl:analyze-string select="@weights" regex="([\.][\d])\s([\.][\d])">
                <xsl:matching-substring>
                    <xsl:value-of select="concat(number(regex-group(1)) * 100, '%')"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <!-\-pour l'instant ça ne marche que pour deux alternatives-\->
        <xsl:variable name="alt1">
            <xsl:analyze-string select="@target" regex="(#.+)\s(.+)">
                <xsl:matching-substring>
                    <xsl:value-of select="translate(regex-group(1), '#', '')"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:variable name="alt2">
            <xsl:analyze-string select="@target" regex="(#.+)\s(.+)">
                <xsl:matching-substring>
                    <xsl:value-of select="translate(regex-group(2), '#', '')"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:if test="//*[@xml:id = $alt1]">
            <xsl:if test="//*[@xml:id = $alt1] = tei:mod">
                <xsl:if test="tei:mod[@xml:id = $alt1]/tei:del/tei:space">
                    <xsl:text>Le terme </xsl:text>
                    <xsl:value-of select="tei:mod[@xml:id = $alt1]//tei:add"/>
                    <xsl:text>a été ajouté sur un blanc.</xsl:text>
                </xsl:if>
            </xsl:if>
            <xsl:text> Il existe une autre possibilité (</xsl:text>
            <xsl:value-of select="$proba"/>
            <xsl:text> de probabilité):</xsl:text>
            <xsl:if test="//*[@xml:id = $alt2] = tei:subst">
                <xsl:if test="//*[@xml:id = $alt2]/tei:del//not(text())">
                    <xsl:text>Un mot inconnu a été remplacé par</xsl:text>
                    <xsl:value-of select="//*[@xml:id = $alt2]/tei:add"/>
                </xsl:if>
            </xsl:if>
        </xsl:if>
<xsl:value-of select="concat($alt1,$alt2)"/>
    </xsl:template>
    -->
    <!--Notes en bas de page. -->
    <!--Est ce que je me complique pas la vie à écrire deux fois les mêmes règles?-->
    <!--Si la note est thématique, second niveau de notes, appel en chiffres arabes-->

    <xsl:template
        match="tei:note[@subtype = 'lexicale'][not(parent::tei:head)] | tei:note[@type = 'particulier'] | tei:note[@type = 'general']">
        <xsl:text>\footnote</xsl:text>
        <xsl:choose>
            <xsl:when test="ancestor::tei:TEI[@subtype = 'version_a']">
                <xsl:text>A</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>B</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>{\label{</xsl:text>
        <xsl:value-of select="@xml:id"/>
        <xsl:text>}</xsl:text>
        <xsl:choose>
            <xsl:when test="@corresp">
                <xsl:variable name="corresponding_witness" select="@corresp"/>
                <xsl:if test="@type">
                    <!--<xsl:if test="@type = 'particulier'"> Mode debug-->
                    <xsl:text>[</xsl:text>
                    <xsl:value-of select="translate(@corresp, '_#', ' ')"/>
                    <!--<xsl:text>. Leçon du témoin: \enquote{</xsl:text>
                    <xsl:for-each
                        select="ancestor::tei:app/descendant::tei:rdg[contains(@wit, $corresponding_witness)]//tei:w">
                        <xsl:apply-templates select="."/>
                    </xsl:for-each>
                    <xsl:text>}</xsl:text>-->
                    <xsl:text>] </xsl:text>
                </xsl:if>
            </xsl:when>
            <xsl:otherwise>
                <!--Debug pour retrouver plus facilement les notes dans le xml-->
                <xsl:text>[Témoin </xsl:text>
                <xsl:value-of select="replace(ancestor::tei:div/@xml:id, '_', ' ')"/>
                <xsl:text>]</xsl:text>
                <!--Debug pour retrouver plus facilement les notes dans le xml-->
            </xsl:otherwise>
        </xsl:choose>
        <!--On fait ça pour ne pas avoir à tout calculer lorsqu'on change une note de bas de page-->
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="division" select="ancestor::tei:div[not(ancestor::tei:div)]/@n"/>
        <xsl:variable name="corresponding_wit">
            <xsl:choose>
                <xsl:when test="@injected">
                    <xsl:value-of select="translate(@corresp, '#', '')"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of
                        select="translate(ancestor::tei:div[not(ancestor::tei:div)]/@corresp, '#', '')"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:message>Searching for <xsl:value-of select="$corresponding_wit"/> / <xsl:value-of
                select="$division"/> / <xsl:value-of select="$xml_id"/></xsl:message>
        <xsl:apply-templates
            select="collection('/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/temoins/castillan?select=*.xml')//tei:TEI[@xml:id = $corresponding_wit]//tei:div[@n = $division]//tei:note[@xml:id = $xml_id]/node()"/>
        <!--On fait ça pour ne pas avoir à tout refaire lorsqu'on change une note de bas de page-->
        <xsl:text>
            }</xsl:text>
    </xsl:template>



    <xsl:template match="tei:ref[@type = 'document_exterieur']">
        <xsl:text>\color{blue}</xsl:text>
        <xsl:value-of select="replace(replace(@target, '_', '\\_'), '../../../', '')"/>
        <xsl:text>\color{black}</xsl:text>
    </xsl:template>

    <xsl:template match="tei:soCalled">
        <xsl:text>``</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>''</xsl:text>
    </xsl:template>

    <xsl:template match="tei:sic[not(@ana = '#omission')]">
        <xsl:apply-templates/>
        <xsl:text>\textsuperscript{\textit{[sic]}.}</xsl:text>
    </xsl:template>


    <xsl:template match="tei:sic[@ana = '#omission']">
        <xsl:apply-templates/>
        <xsl:text>\footnoteB{Omission chez le témoin.}</xsl:text>
    </xsl:template>



    <xsl:template match="tei:lg">
        <xsl:apply-templates/>
    </xsl:template>


    <xsl:template match="tei:l">
        <xsl:apply-templates/>
        <xsl:if test="following-sibling::tei:l">
            <xsl:text>\\</xsl:text>
        </xsl:if>
    </xsl:template>

    <xsl:template match="tei:head" mode="test">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:lb[@break = 'y']">
        <xsl:text> </xsl:text>
    </xsl:template>

    <xsl:template match="tei:w">
        <xsl:if test="not(parent::tei:del[count(descendant::tei:w) = 1])">
            <xsl:text> </xsl:text>
        </xsl:if>
        <xsl:apply-templates/>
        <xsl:choose>
            <xsl:when test="following::tei:pc[1]"/>
            <xsl:otherwise> </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <!--A terme remplace les tei:hi pour de l'istruction de mise en page dans les notes-->
    <xsl:template match="tei:foreign">
        <xsl:text>\textit{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>
    <!--A terme remplace les tei:hi pour de l'istruction de mise en page dans les notes-->

    <!--MISE EN PAGE-->

    <xsl:template match="tei:ab"/>



    <!--AJOUTS-->
    <!--ajouts du copiste en exposant (interlinéaire) ou en note (marge): deuxième niveau de 
        notes ou ajout en exposation. Si appartient à un apparat, simple indication avec le 
        terme ajouté en italique-->
    <xsl:template match="tei:add[not(parent::tei:head)]">
        <xsl:if test="not(@place)">
            <xsl:value-of select="."/>
        </xsl:if>
        <xsl:if test="@place = 'inline'">
            <xsl:if test="ancestor::tei:app">
                <xsl:text>\textit{</xsl:text>
                <xsl:apply-templates/>
                <xsl:text>}</xsl:text>
            </xsl:if>
        </xsl:if>
        <xsl:if test="@place = 'above'">
            <xsl:text>\textit{</xsl:text>
            <xsl:apply-templates/>
            <xsl:text>}</xsl:text>
        </xsl:if>
        <xsl:if test="@place = 'margin'">
            <!--Si le add est inclus dans un apparat-->
            <xsl:if test="ancestor::tei:app">
                <!--Si l'apparat n'est pas un apparat principal mais un apparat de point notables (notable)
                    >> note. On peut accepter la note de bas de page (éviter les notes de bas de page dans un apparat
                    critique...)-->
                <!--Si l'apparat n'est pas un apparat principal mais un apparat de point notables (notable)-->

                <xsl:text>\textit{</xsl:text>
                <xsl:apply-templates/>
                <xsl:text>}</xsl:text>


            </xsl:if>
            <!--Si le add est inclus dans un apparat-->
            <xsl:if test="not(ancestor::tei:app)">
                <xsl:text>\footnote{</xsl:text>
                <xsl:if test="@corresp">
                    <xsl:text> [Ms. </xsl:text>
                    <xsl:value-of select="translate(@corresp, '#', '')"/>
                    <xsl:text>] </xsl:text>
                </xsl:if>
                <xsl:text>Ajouté </xsl:text>
                <xsl:text>(marge)</xsl:text>
                <xsl:text>: ``\textit{</xsl:text>
                <xsl:value-of select="text()"/>
                <xsl:text>}''</xsl:text>
                <xsl:if test="@hand">
                    <xsl:text> Main </xsl:text>
                    <xsl:value-of select="translate(@hand, '#', '')"/>
                    <xsl:text>. </xsl:text>
                </xsl:if>
                <xsl:if test="./tei:note">
                    <xsl:apply-templates select="tei:note"/>
                </xsl:if>
                <xsl:if test="not(@note)"/>
                <xsl:text>}</xsl:text>
            </xsl:if>
        </xsl:if>
        <!--etc-->



    </xsl:template>

    <xsl:template match="tei:ref[@type = 'edition']">
        <!--Créer une règle pour gérer les multiples appels de références, avec un analyse-string-->
        <xsl:choose>
            <xsl:when test="parent::tei:note">
                <xsl:if test="parent::tei:quote[@xml:lang][not(@xml:lang = 'fr')]">
                    <xsl:text> {\normalfont </xsl:text>
                </xsl:if>
                <xsl:text> [\cite</xsl:text>
                <xsl:if test="@n">
                    <xsl:text>[</xsl:text>
                    <xsl:apply-templates select="@n"/>
                    <xsl:text>]</xsl:text>
                </xsl:if>
                <xsl:text>{</xsl:text>
                <xsl:value-of select="translate(translate(@target, ' ', ','), '#', '')"/>
                <xsl:text>}]</xsl:text>
                <xsl:if test="parent::tei:quote[@xml:lang][not(@xml:lang = 'fr')]">
                    <xsl:text>}</xsl:text>
                </xsl:if>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>\footcite</xsl:text>
                <xsl:if test="@n">
                    <xsl:text>[</xsl:text>
                    <xsl:apply-templates select="@n"/>
                    <xsl:text>]</xsl:text>
                </xsl:if>
                <xsl:text>{</xsl:text>
                <xsl:value-of select="translate(translate(@target, ' ', ','), '#', '')"/>
                <xsl:text>}</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:ref[@type = 'url'][not(parent::tei:note)]">
        <xsl:variable name="echappement_url" select="replace(@target, '#', '\\#')"/>
        <xsl:choose>
            <xsl:when test="node()">
                <xsl:text>\href{</xsl:text>
                <xsl:value-of select="$echappement_url"/>
                <xsl:text>}{</xsl:text>
                <xsl:apply-templates/>
                <xsl:text>}</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>\footnote{\url{</xsl:text>
                <xsl:value-of select="$echappement_url"/>
                <xsl:text>}}</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:ref[@type = 'interne']">
        <xsl:variable name="target" select="translate(@target, '#', '')"/>
        <xsl:if test="not(//tei:*[@xml:id = $target][ancestor-or-self::tei:graphic])">
            <xsl:choose>
                <xsl:when test="@subtype = 'section'">
                    <xsl:text>\nameref{</xsl:text>
                </xsl:when>
                <xsl:when test="@subtype = 'note'">
                    <xsl:text>\ref{</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>\nameref{</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
            <xsl:value-of select="$target"/>
            <xsl:text>}, page \pageref{</xsl:text>
            <xsl:value-of select="$target"/>
            <xsl:text>}</xsl:text>
        </xsl:if>
        <xsl:if test="//tei:*[@xml:id = $target][ancestor-or-self::tei:graphic]">
            <xsl:text>figure \ref{</xsl:text>
            <xsl:value-of select="$target"/>
            <xsl:text>}</xsl:text>
        </xsl:if>
        <!--
        <xsl:if
            test="//tei:*[@xml:id = $target][ancestor-or-self::tei:graphic][node()]">
            <xsl:apply-templates/>
            <xsl:text> (figure \ref{</xsl:text>
            <xsl:value-of select="$target"/>
            <xsl:text>}, page \pageref{</xsl:text>
            <xsl:value-of select="$target"/>
            <xsl:text>})</xsl:text>
        </xsl:if>-->
    </xsl:template>

    <xsl:template match="tei:code[@lang = 'tagset'] | tei:code[@rend = 'show']">
        <xsl:text>\codeword{</xsl:text>
        <!--On supprime les espaces surnuméraires qui forment un saut de ligne 
            d'une façon ou d'une autre. codeword (verbatim) n'acceptent que des éléments en ligne.-->
        <xsl:value-of select="replace(., '\s+', ' ')"/>
        <xsl:text>}</xsl:text>
    </xsl:template>

    <xsl:template match="tei:ref[@type = 'biblio'][not(@rend)]">
        <!--Créer une règle pour gérer les multiples appels de références, avec un analyse-string-->
        <xsl:if test="parent::tei:quote[@xml:lang][not(@xml:lang = 'fr')]">
            <xsl:text> {\normalfont [</xsl:text>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="ancestor::tei:note">
                <xsl:text>\cite</xsl:text>
            </xsl:when>
            <xsl:when test="ancestor::tei:quote and not(node())">
                <xsl:text>\footcite</xsl:text>
            </xsl:when>
            <xsl:when test="node()">
                <xsl:text>\footnoteB{\cite</xsl:text>
            </xsl:when>
            <xsl:otherwise> [\cite</xsl:otherwise>
        </xsl:choose>
        <xsl:choose>
            <xsl:when test="@n">
                <xsl:text>[</xsl:text>
                <xsl:value-of select="@n"/>
                <xsl:text>]</xsl:text>
            </xsl:when>
        </xsl:choose>
        <xsl:text>{</xsl:text>
        <xsl:value-of select="translate(translate(@target, ' ', ','), '#', '')"/>
        <xsl:text>}</xsl:text>
        <xsl:choose>
            <xsl:when test="node() and not(ancestor::tei:note)">
                <xsl:text>, </xsl:text>
                <xsl:apply-templates/>
                <xsl:text>}</xsl:text>
            </xsl:when>
            <xsl:when test="node() and ancestor::tei:note">
                <xsl:text>, </xsl:text>
                <xsl:apply-templates/>
            </xsl:when>
        </xsl:choose>
        <xsl:if test="not(node() | ancestor::tei:note | ancestor::tei:quote)">
            <xsl:text>]</xsl:text>
        </xsl:if>
        <xsl:if test="parent::tei:quote[@xml:lang][not(@xml:lang = 'fr')]">
            <xsl:text>]}</xsl:text>
        </xsl:if>
    </xsl:template>




    <xsl:template match="tei:ref[@type = 'biblio'][@rend = 'print_title']">
        <!--Créer une règle pour gérer les multiples appels de références, avec un analyse-string-->
        <xsl:choose>
            <xsl:when test="parent::tei:note">
                <xsl:text>\citetitle</xsl:text>
                <xsl:text>{</xsl:text>
                <xsl:value-of select="translate(translate(@target, ' ', ','), '#', '')"/>
                <xsl:text>} </xsl:text>
                <xsl:text>[\cite</xsl:text>
                <xsl:if test="@n">
                    <xsl:text>[</xsl:text>
                    <xsl:apply-templates select="@n"/>
                    <xsl:text>]</xsl:text>
                </xsl:if>
                <xsl:text>{</xsl:text>
                <xsl:value-of select="translate(translate(@target, ' ', ','), '#', '')"/>
                <xsl:text>}]</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>\citetitle</xsl:text>
                <xsl:text>{</xsl:text>
                <xsl:value-of select="translate(translate(@target, ' ', ','), '#', '')"/>
                <xsl:text>}\footcite</xsl:text>
                <xsl:if test="@n">
                    <xsl:text>[</xsl:text>
                    <xsl:apply-templates select="@n"/>
                    <xsl:text>]</xsl:text>
                </xsl:if>
                <xsl:text>{</xsl:text>
                <xsl:value-of select="translate(translate(@target, ' ', ','), '#', '')"/>
                <xsl:text>}</xsl:text>
            </xsl:otherwise>
        </xsl:choose>

    </xsl:template>



    <!--Les ajouts de ma part sont entre crochets-->
    <xsl:template match="//tei:supplied" name="supplied">
        <xsl:text>&lt;</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>&gt;</xsl:text>
    </xsl:template>
    <!--Les ajouts de ma part sont entre crochets-->
    <!--AJOUTS-->


    <!--MODIFICATIONS CORRECTIONS-->
    <xsl:template match="//tei:space" name="space">
        <xsl:text>\indent </xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:teiHeader"/>

    <xsl:template match="tei:title">
        <xsl:if test="@type = 'section'">
            <xsl:text>\textsc{</xsl:text>
        </xsl:if>
        <xsl:text>\textit{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
        <xsl:if test="@type = 'section'">
            <xsl:text>}</xsl:text>
        </xsl:if>
    </xsl:template>

    <xsl:template match="tei:unclear" name="unclear">
        <xsl:apply-templates/>
        <xsl:text>~(?)</xsl:text>
    </xsl:template>

    <xsl:template match="tei:choice">
        <xsl:value-of select="tei:corr"/>
        <xsl:value-of select="tei:reg"/>
        <xsl:value-of select="tei:expan"/>
    </xsl:template>


    <!--<xsl:template match="tei:damage" name="damage">
        <xsl:choose>
            <xsl:when test="text() = ''">
                <xsl:text>&#x2020; &#x2020;</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>\underline{</xsl:text>
                <xsl:apply-templates/>
                <xsl:text>}</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>-->

    <xsl:template match="tei:gap">
        <xsl:text>\indent </xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <!-- ignorer le text entre balises <del>-->
    <xsl:template match="tei:del">
        <xsl:text> [[</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]]</xsl:text>
    </xsl:template>
    <!-- ignorer le text entre balises <del>-->

    <!--Ici on va créer des règles pour afficher les éléments dans les apparats-->



    <!--Ici on va créer des règles pour afficher les éléments dans les apparats-->




    <xsl:template match="tei:div[@type = 'chapitre'][not(@type = 'glose' or @type = 'traduction')]">
        <xsl:text>\pagestyle{edition_vis_a_vis}</xsl:text>
        <xsl:variable name="div_n" select="@n"/>
        <xsl:text>
        \begin{pages}
        \begin{Leftside}
        \beginnumbering </xsl:text>
        <xsl:message>Found you</xsl:message>
        <xsl:apply-templates
            select="document('/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/temoins/castillan/Val_S.xml')//tei:div[@n = $div_n][@type = 'chapitre']/node()"/>
        <xsl:text>
        \endnumbering
        \end{Leftside}</xsl:text>
        <xsl:variable name="temoin_courant2" select="substring-after($temoin_courant, '_')"/>
        <!--<xsl:text>\chapter{Chapitre </xsl:text>
        <xsl:value-of select="@n"/>
        <xsl:choose>
            <xsl:when test="$fusion = 'False'">
                <xsl:text> (base </xsl:text>
                <xsl:value-of select="$temoin_courant2"/>
                <xsl:text>)</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>:</xsl:text>
                <xsl:apply-templates select="tei:head"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>}</xsl:text>-->
        <xsl:text>
        \begin{Rightside}
        \beginnumbering</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>
        \endnumbering
        \end{Rightside}
        \end{pages}
        \Pages</xsl:text>
    </xsl:template>

    <!--Foliation en exposant entre crochets -->
    <xsl:template match="tei:pb">
        <xsl:text>\textsuperscript{[fol. </xsl:text>
        <xsl:value-of select="@n"/>
        <xsl:text>]}</xsl:text>
    </xsl:template>
    <!--Foliation en exposant entre crochets -->


    <xsl:template match="tei:cb">
        <xsl:text>\textit{[col. b]}</xsl:text>
    </xsl:template>
    <!--Foliation-->


    <xsl:template match="tei:quote[@type = 'secondaire'][ancestor::tei:note][not(@subtype = 'vers')]">
        <xsl:variable name="langue">
            <xsl:choose>
                <xsl:when test="@xml:lang = 'lat'">latin</xsl:when>
                <xsl:when test="@xml:lang = 'eng'">english</xsl:when>
                <xsl:when test="@xml:lang = 'spo' or @xml:lang = 'esp'">spanish</xsl:when>
                <xsl:otherwise>french</xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:choose>
            <xsl:when test="$langue = 'french'">
                <xsl:choose>
                    <xsl:when test="string-length(string-join(descendant::text())) > 200">
                        <xsl:text>\begin{quote}</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text> \end{quote}</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>\enquote{</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>}</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
                <xsl:choose>
                    <xsl:when test="string-length(string-join(descendant::text())) > 200">
                        <xsl:text>\begin{quote}\begin{otherlanguage}{</xsl:text>
                        <xsl:value-of select="$langue"/>
                        <xsl:text>}\textit{</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>}\end{otherlanguage}\end{quote}</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>\enquote{\begin{otherlanguage}{</xsl:text>
                        <xsl:value-of select="$langue"/>
                        <xsl:text>}\textit{</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>}\end{otherlanguage}}</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template
        match="tei:quote[@type = 'secondaire'][not(ancestor::tei:note)][not(@subtype = 'vers')]">
        <xsl:variable name="langue">
            <xsl:choose>
                <xsl:when test="@xml:lang = 'lat'">latin</xsl:when>
                <xsl:when test="@xml:lang = 'eng'">english</xsl:when>
                <xsl:when test="@xml:lang = 'fra'">french</xsl:when>
                <xsl:when test="@xml:lang = 'spo' or @xml:lang = 'esp'">spanish</xsl:when>
                <xsl:otherwise>french</xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:choose>
            <xsl:when test="$langue = 'french'">
                <xsl:choose>
                    <xsl:when test="string-length(.) &gt; 100">
                        <xsl:text>\begin{quote}</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text> \end{quote}</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>\enquote{</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>}</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
                <xsl:choose>
                    <xsl:when test="string-length(string-join(descendant::text())) &gt; 200">
                        <xsl:text>\begin{quote}\begin{otherlanguage}{</xsl:text>
                        <xsl:value-of select="$langue"/>
                        <xsl:text>}\textit{</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>}\end{otherlanguage}\end{quote}</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>\enquote{\begin{otherlanguage}{</xsl:text>
                        <xsl:value-of select="$langue"/>
                        <xsl:text>}\textit{</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>}\end{otherlanguage}}</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template match="tei:quote[@type = 'primaire'][parent::tei:note]">
        <xsl:variable name="langue">
            <xsl:choose>
                <xsl:when test="@xml:lang = 'lat'">latin</xsl:when>
                <xsl:when test="@xml:lang = 'eng'">english</xsl:when>
                <xsl:when test="@xml:lang = 'spo' or @xml:lang = 'esp'">spanish</xsl:when>
                <xsl:otherwise>french</xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:choose>
            <xsl:when test="$langue != 'french'">
                <xsl:choose>
                    <xsl:when test="not(child::tei:l)">
                        <xsl:choose>
                            <xsl:when test="string-length(string-join(descendant::text())) &gt; 200">
                                <xsl:text>\begin{note_quote}\begin{otherlanguage}{</xsl:text>
                                <xsl:value-of select="$langue"/>
                                <xsl:text>}\textit{</xsl:text>
                                <xsl:apply-templates/>
                                <xsl:text>}\end{otherlanguage}\end{note_quote}</xsl:text>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:text>\enquote{\begin{otherlanguage}{</xsl:text>
                                <xsl:value-of select="$langue"/>
                                <xsl:text>}\textit{</xsl:text>
                                <xsl:apply-templates/>
                                <xsl:text>}\end{otherlanguage}}</xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>\begin{quote}\begin{otherlanguage}{</xsl:text>
                        <xsl:value-of select="$langue"/>
                        <xsl:text>}\textit{</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>}\end{otherlanguage}\end{quote}</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
                <xsl:choose>
                    <xsl:when test="not(child::tei:l)">
                        <xsl:text>\enquote{</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>}</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>\begin{quote}</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>\end{quote}</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <!--Les apparats de type filtre sont à ignorer-->
    <xsl:template
        match="tei:app[@type = 'graphique'] | tei:app[@type = 'filtre'][count(descendant::tei:rdg) = 1] | tei:app[@type = 'auxiliarite']">
        <!--Ajouter un test sur la présence d'une note-->
        <xsl:text> </xsl:text>
        <!--Afficher ici la lecture du témoin courant, voir plus bas-->
        <xsl:apply-templates select="tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]"/>
        <xsl:if
            test="descendant::tei:note[not(ancestor::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)])]">
            <xsl:apply-templates
                select="descendant::tei:note[not(ancestor::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)])]"
            />
        </xsl:if>
    </xsl:template>

    <xsl:template match="tei:milestone">

        <xsl:if test="@unit = 'item_rang_1'">
            <xsl:text>\textbf{ </xsl:text>
            <xsl:value-of select="@n"/>
            <xsl:text>}~</xsl:text>
        </xsl:if>

        <xsl:if test="@unit = 'item_rang_2'">
            <xsl:text>\textbf{ </xsl:text>
            <xsl:value-of select="preceding::tei:milestone[@unit = 'item_rang_1'][1]/@n"/>
            <xsl:text>.</xsl:text>
            <xsl:value-of select="@n"/>
            <xsl:text>}~</xsl:text>
        </xsl:if>

        <xsl:if test="@unit = 'item_rang_3'">
            <xsl:text>\textbf{ </xsl:text>
            <xsl:value-of select="preceding::tei:milestone[@unit = 'item_rang_1'][1]/@n"/>
            <xsl:text>.</xsl:text>
            <xsl:value-of select="preceding::tei:milestone[@unit = 'item_rang_2'][1]/@n"/>
            <xsl:text>.</xsl:text>
            <xsl:value-of select="@n"/>
            <xsl:text>}~</xsl:text>
        </xsl:if>
    </xsl:template>

    <!--  Ne marche pas pour l'instant avec ednotes (il faudrait pouvoir faire apparaitre
      le texte non mis en forme en note)
      <xsl:template match="tei:hi[@rend = 'initiale']">
        <xsl:text>\initiale[lines=3, findent=3pt, nindent=0pt]{</xsl:text>
        <xsl:value-of select="upper-case(.)"/>
        <xsl:text>}</xsl:text>
    </xsl:template>-->

    <xsl:template match="tei:hi[@rend = 'lettre_attente']"/>

    <xsl:template match="tei:hi[@rend = 'lettre_capitulaire']">
        <xsl:value-of select="lower-case(.)"/>
    </xsl:template>

    <xsl:template
        match="tei:app[@type = 'lexicale'][count(descendant::tei:rdg) = 1] | tei:app[@type = 'morphosyntactique'][count(descendant::tei:rdg) = 1] | tei:app[@type = 'indetermine'][count(descendant::tei:rdg) = 1]">
        <!--Essayer de trouver un moyen de faire apparaître les omissions clairement. Par exemple: dans un niveau de note spécifique.-->
        <!--On omet les omissions pour l'instant-->
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:app[@type = 'filtre'][count(descendant::tei:rdg) > 1]">
        <xsl:variable name="temoin_courant">
            <xsl:analyze-string select="ancestor::tei:div[@type = 'chapitre'][@xml:id]/@xml:id"
                regex="([A-Za-z]+_[a-zA-Z]+)(.*)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:apply-templates
            select="descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]"/>
    </xsl:template>



    <!-- <xsl:template match="tei:seg[@ana = '#omission']">
        <xsl:text> </xsl:text>

        <xsl:variable name="omitted_lemma">
            <xsl:choose>
                <xsl:when test="preceding-sibling::node()[self::tei:app | self::tei:w][1]/name() = 'app'">
                    <xsl:apply-templates
                        select="preceding-sibling::node()[self::tei:app][1]/child::tei:rdg[contains(@wit, $temoin_courant)]/tei:w"
                    />
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates select="preceding-sibling::node()[self::tei:w][1]"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:variable name="temoin_courant2" select="substring-after($temoin_courant, '_')"/>


        <!-\-Ici il faudra reconstruire le texte des témoins en cas de variation au sein de l'omission.-\->
        <xsl:variable name="omm_wits">
            <!-\-<xsl:for-each select="tokenize(descendant::tei:rdg[contains(@wit, 'Sev_Z')]/@wit, '\s')">
                <xsl:value-of select="substring-after(., '_')"/>
            </xsl:for-each>-\->
            <xsl:text>Z</xsl:text>
        </xsl:variable>
        <xsl:text>\edtext{}{</xsl:text>
        <xsl:text>\Cfootnote{Lacune (après \enquote{</xsl:text>
        <xsl:value-of select="$omitted_lemma"/>
        <xsl:text>}): </xsl:text>
        <xsl:apply-templates select="descendant::tei:rdg[@wit = '#Sev_Z']/tei:w"/>
        <xsl:variable name="non_omm_wits">
            <!-\-<xsl:for-each select="tokenize(descendant::tei:rdg[@wit = 'Sev_Z']/@wit, '\s')">
                <xsl:value-of select="substring-after(., '_')"/>
            </xsl:for-each>-\->
            <xsl:text>Z</xsl:text>
        </xsl:variable>
        <xsl:text> \textit{</xsl:text>
        <xsl:value-of select="$non_omm_wits"/>
        <xsl:text>}}}
        </xsl:text>
    </xsl:template>
-->

    <xsl:template match="tei:seg[@ana = $omission_binaire]">
        <!--On rappelle que @exclude indique les témoins qui sont lacunaires-->
        <!--Et que @corresp correspond aux témoins qui partagent le texte de la lacune-->
        <xsl:choose>
            <xsl:when test="@corresp = concat('#', $temoin_courant)">
                <xsl:text>\edtext{</xsl:text>
                <xsl:apply-templates
                    select="descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]"/>
                <xsl:text>}{\lemma{</xsl:text>
                <xsl:apply-templates
                    select="descendant::tei:app[1]/descendant::tei:rdg[translate(@wit, '#', '') = $temoin_courant]"/>
                <xsl:apply-templates
                    select="descendant::tei:app[2]/descendant::tei:rdg[translate(@wit, '#', '') = $temoin_courant]"/>
                <xsl:text>~\ldots~</xsl:text>
                <xsl:apply-templates
                    select="descendant::tei:app[last()]/descendant::tei:rdg[translate(@wit, '#', '') = $temoin_courant]"/>
                <xsl:text>}\Cfootnote{\textit{</xsl:text>
                <xsl:value-of select="substring-after($temoin_courant, '_')"/>
                <xsl:text>} | \textit{om. </xsl:text>
                <xsl:for-each select="tokenize(@exclude, '\s')">
                    <xsl:value-of select="substring-after(., '_')"/>
                </xsl:for-each>
                <xsl:text>}}}</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:variable name="preceding_lemma">
                    <xsl:choose>
                        <xsl:when
                            test="preceding-sibling::node()[self::tei:app | self::tei:w][1]/name() = 'app'">
                            <xsl:apply-templates
                                select="preceding-sibling::node()[self::tei:app][1]/child::tei:rdg[contains(@wit, $temoin_courant)]/tei:w"
                            />
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:apply-templates select="preceding-sibling::node()[self::tei:w][1]"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <xsl:text>\edtext{}{</xsl:text>
                <xsl:text>\Cfootnote{</xsl:text>
                <xsl:value-of select="$preceding_lemma"/>
                <xsl:text> \textit{</xsl:text>
                <xsl:for-each select="tokenize(@exclude, '\s')">
                    <xsl:value-of select="substring-after(., '_')"/>
                </xsl:for-each>
                <xsl:text>} | </xsl:text>
                <xsl:value-of select="$preceding_lemma"/>
                <xsl:apply-templates
                    select="descendant::tei:rdg[not(contains(translate(@wit, '#', ''), $temoin_courant))]"/>
                <xsl:text> \textit{</xsl:text>
                <xsl:for-each select="tokenize(@exclude, '\s')">
                    <xsl:value-of select="substring-after(., '_')"/>
                </xsl:for-each>
                <xsl:text>}}}</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <!--
    <xsl:template match="tei:app[@type = 'omission'][not(parent::tei:seg)]">
        <!-\-On traite ici les omissions ponctuelles: il faut adapter cela à la sensibilité choisie lors du traitement des
            omissions, pour l'instant seules les omissions isolées (1 seul élément) ne sont pas dans un tei:seg-\->
        <xsl:text> </xsl:text>
        <xsl:variable name="temoin_courant">
            <xsl:analyze-string select="ancestor::tei:div[@type = 'chapitre'][@xml:id]/@xml:id"
                regex="([A-Za-z]+_[a-zA-Z]+)(.*)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:variable name="preceding_omitted_lemma">
            <xsl:choose>
                <xsl:when test="preceding-sibling::node()[self::tei:app | self::tei:w][1]/name() = 'app'">
                    <xsl:apply-templates
                        select="preceding-sibling::node()[self::tei:app][1]/descendant::tei:rdg[contains(@wit, $temoin_courant)]/tei:w"
                    />
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates select="preceding-sibling::node()[self::tei:w][1]"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:variable name="omm_wits">
            <xsl:for-each
                select="tokenize(descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]/@wit, '\s')">
                <xsl:value-of select="substring-after(., '_')"/>
            </xsl:for-each>
        </xsl:variable>
        <xsl:text>\edtext{</xsl:text>
        <xsl:text>}{</xsl:text>
        <xsl:text>\Dfootnote{[OM]</xsl:text>
        <xsl:value-of select="$preceding_omitted_lemma"/>
        <xsl:text> \textit{</xsl:text>
        <xsl:value-of select="$omm_wits"/>
        <xsl:text>} | </xsl:text>
        <xsl:value-of select="$preceding_omitted_lemma"/>
        <xsl:text> </xsl:text>
        <xsl:apply-templates
            select="descendant::tei:rdg[not(contains(translate(@wit, '#', ''), $temoin_courant))]"/>
        <xsl:variable name="non_omm_wits">
            <xsl:for-each
                select="tokenize(string-join(descendant::tei:rdg[not(contains(translate(@wit, '#', ''), $temoin_courant))]/@wit), '\s')">
                <xsl:value-of select="translate(substring-after(., '_'), '_#', '')"/>
            </xsl:for-each>
        </xsl:variable>
        <xsl:text> \textit{</xsl:text>
        <xsl:value-of select="$non_omm_wits"/>
        <xsl:text>}}}
        </xsl:text>
    </xsl:template>
-->

    <xsl:template match="
            tei:app[@type = 'entite_nommee'][count(descendant::tei:rdg) > 1]
            | tei:app[@type = 'lexicale'][count(descendant::tei:rdg) > 1]
            | tei:app[@type = 'morphosyntactique'][count(descendant::tei:rdg) > 1]
            | tei:app[@type = 'indetermine'][count(descendant::tei:rdg) > 1]
            | tei:app[@type = 'personne'][count(descendant::tei:rdg) > 1]
            | tei:app[@type = 'genre'][count(descendant::tei:rdg) > 1]
            | tei:app[@type = 'omission'][not(ancestor::tei:seg[@ana = $omission_binaire])]">
        <xsl:text> </xsl:text>
        <xsl:variable name="temoin_courant2" select="substring-after($temoin_courant, '_')"/>
        <xsl:text> \edtext{</xsl:text>
        <xsl:apply-templates
            select="descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]"/>
        <xsl:text>}{\Dfootnote{</xsl:text>
        <!-- test: UNCLEAR entre crochets avec un ?-->
        <!--Ici il faut ajouter un omm. dans l'apparat sans que ça se voie dans le corps du texte.-->
        <xsl:text>\textit{</xsl:text>
        <!--Pour chaque témoin, ne faire apparaître que la lettre correspondante-->
        <xsl:choose>
            <!--S'il y a un rdgGrp (= si d'autres leçons sont identiques modulo variation graphique à la leçon base)-->
            <xsl:when
                test="boolean(descendant::tei:rdgGrp[descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]])">
                <xsl:variable name="lemma_wits">
                    <xsl:for-each
                        select="tokenize(descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]/@wit, '\s')">
                        <xsl:value-of select="substring-after(., '_')"/>
                    </xsl:for-each>
                </xsl:variable>
                <xsl:variable name="siblings">
                    <xsl:for-each
                        select="descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]/following-sibling::tei:rdg">
                        <xsl:for-each select="tokenize(@wit, '\s')">
                            <xsl:value-of select="substring-after(., '_')"/>
                        </xsl:for-each>
                    </xsl:for-each>
                    <xsl:for-each
                        select="descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]/preceding-sibling::tei:rdg">
                        <xsl:for-each select="tokenize(@wit, '\s')">
                            <xsl:value-of select="substring-after(., '_')"/>
                        </xsl:for-each>
                    </xsl:for-each>
                </xsl:variable>

                <!--Il y a parfois des rdgGrp qui ne contiennent qu'un tei:rdg: dans ce cas, n'imprimer que la valeur du témoin base-->
                <xsl:choose>
                    <!--<xsl:when
                        test="boolean(count(descendant::tei:rdgGrp[descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]]/descendant::tei:rdg) > 1)">
                        <xsl:value-of
                            select="concat($lemma_wits, '~', $siblings, '~c.v.')"
                        />-->
                    <xsl:when
                        test="boolean(count(descendant::tei:rdgGrp[descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]]/descendant::tei:rdg) > 1)">
                        <xsl:value-of select="concat($lemma_wits, '`', $siblings)"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="$lemma_wits"/>
                    </xsl:otherwise>
                </xsl:choose>
                <!--Il y a parfois des rdgGrp qui ne contiennent qu'un tei:rdg: dans ce cas, n'imprimer que la valeur du témoin base-->
            </xsl:when>
            <!--S'il y a un rdgGrp (= si d'autres leçons sont identiques modulo variation graphique à la leçon base)-->
            <xsl:otherwise>
                <xsl:for-each
                    select="tokenize(tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]/@wit, '\s')">
                    <xsl:value-of select="substring-after(., '_')"/>
                </xsl:for-each>
            </xsl:otherwise>
        </xsl:choose>
        <!--Pour chaque témoin, ne faire apparaître que la lettre correspondante-->
        <xsl:text>}\,|\,</xsl:text>
        <!--La même chose mais en utilisant une autre méthode-->
        <xsl:choose>
            <xsl:when test="descendant::tei:rdgGrp">
                <xsl:for-each
                    select="descendant::tei:rdgGrp[count(descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]) = 0]">
                    <!--L'idée ici est de raffiner les apparats pour rassembler les variantes graphiques entre elles-->
                    <xsl:for-each select="descendant::tei:rdg">
                        <xsl:variable name="sigle_temoin">
                            <xsl:analyze-string select="@wit" regex="([a-zA-Z]*_)([A-Z])">
                                <xsl:matching-substring>
                                    <xsl:value-of select="regex-group(2)"/>
                                </xsl:matching-substring>
                            </xsl:analyze-string>
                        </xsl:variable>
                        <xsl:choose>
                            <xsl:when test="descendant::text()">
                                <xsl:if test="not(preceding-sibling::tei:rdg)">
                                    <xsl:apply-templates select="."/>
                                </xsl:if>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:text>\textit{om.}</xsl:text>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:text>\,\textit{</xsl:text>
                        <xsl:value-of select="$sigle_temoin"/>
                        <!--<xsl:if
                            test="not(count(ancestor::tei:rdgGrp/descendant::tei:rdg) = 1) and not(following-sibling::tei:rdg)">
                            <xsl:text>~c.v.</xsl:text>
                            </xsl:if>-->
                        <xsl:text>}\,</xsl:text>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
                <xsl:for-each select="tei:rdg[not(contains(translate(@wit, '#', ''), $temoin_courant))]">
                    <xsl:variable name="sigle_temoin">
                        <xsl:analyze-string select="@wit" regex="([a-zA-Z]*_)([A-Z])">
                            <xsl:matching-substring>
                                <xsl:value-of select="regex-group(2)"/>
                            </xsl:matching-substring>
                        </xsl:analyze-string>
                    </xsl:variable>
                    <xsl:choose>
                        <xsl:when test="descendant::text()">
                            <xsl:apply-templates select="."/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text>\textit{om.}</xsl:text>
                        </xsl:otherwise>
                    </xsl:choose>
                    <xsl:text>\,\textit{</xsl:text>
                    <xsl:value-of select="$sigle_temoin"/>
                    <xsl:text>}\,</xsl:text>
                </xsl:for-each>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>}}</xsl:text>
    </xsl:template>
    <!--STRUCTURE DU TEXTE-->



    <!--Choisir et marquer le chapitre-->

    <!--Choisir et marquer la glose/traduction-->


    <!--Choisir et marquer la glose/traduction-->




    <!--STRUCTURE DU TEXTE-->

    <!--MISE EN PAGE-->
    <!--Marquer les paragraphes par un retour à la ligne-->
    <xsl:template match="tei:p[parent::tei:div[@type = 'traduction']]">
        <xsl:variable name="div_n" select="ancestor::tei:div[@type = 'chapitre']/@n"/>
        <xsl:choose>
            <xsl:when test="not(preceding::tei:p[ancestor::tei:div[@type = 'chapitre'][@n = $div_n]])">
                <xsl:text>\pstart[\section*{</xsl:text>
                <xsl:apply-templates select="ancestor::tei:div[@type = 'chapitre']/tei:head" mode="test"/>
                <xsl:text>}]</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>\pstart </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:choose>
            <xsl:when
                test="not(preceding-sibling::tei:p) and not(ancestor::tei:TEI[@subtype = 'version_a'])">
                <xsl:text>
             {\ledrightnote{\hspace{.6cm}\textbf{[Traduction]}}}</xsl:text>
            </xsl:when>
            <xsl:otherwise/>
        </xsl:choose>
        <xsl:apply-templates/>
        <xsl:text>\pend
        
        
        </xsl:text>
    </xsl:template>



    <xsl:template match="tei:p[parent::tei:div[@type = 'glose']]">
        <xsl:variable name="div_n" select="ancestor::tei:div[@type = 'chapitre']/@n"/>
        <xsl:choose>
            <xsl:when test="not(preceding::tei:p[ancestor::tei:div[@type = 'chapitre'][@n = $div_n]])">
                <!--                <xsl:text>\pstart[\pagestyle{edition_glose}\section*{</xsl:text>-->
                <xsl:text>~\\ \section*{</xsl:text>
                <xsl:apply-templates select="ancestor::tei:div[@type = 'chapitre']/tei:head" mode="test"/>
                <xsl:text>}]</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <!--                <xsl:text>\pstart </xsl:text>-->
                <xsl:text>~\\ </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:choose>
            <xsl:when
                test="not(preceding-sibling::tei:p) and not(ancestor::tei:TEI[@subtype = 'version_a'])">
                <xsl:text>{\ledrightnote{\hspace{.6cm}\textbf{[Glose]}}}</xsl:text>
            </xsl:when>
            <xsl:otherwise/>
        </xsl:choose>
        <xsl:apply-templates/>
        <!--        <xsl:text>\pend-->

        <!--</xsl:text>-->
    </xsl:template>


    <xsl:template match="tei:div[@type = 'glose']">
        <xsl:text>\pstart ~\\</xsl:text>
        <!--<xsl:text>\pstart ~\\</xsl:text>-->
        <xsl:apply-templates/>
        <xsl:text>\pend </xsl:text>
    </xsl:template>


    <xsl:template match="tei:div[@type = 'traduction']">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:fw"/>

    <xsl:template match="tei:witEnd">
        <xsl:text>\footnoteB{Le témoin </xsl:text>
        <xsl:value-of select="substring-after(parent::tei:rdg/@wit, '_')"/>
        <xsl:text> s'arrête ici.}</xsl:text>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:variable name="remplacement1" select="replace(., '&amp;', '\\&amp;')"/>
        <xsl:value-of select="$remplacement1"/>
    </xsl:template>


</xsl:stylesheet>
