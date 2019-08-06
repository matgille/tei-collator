<?xml version="1.0" encoding="UTF-8"?>

<!-- IDEE: Gérer les modifications textuelles: Et si je faisais ma transformation en deux temps? D'abord, toutes les grosses transformations EN GARDANT UNE STRUCTURE XML BASIQUE
    et bien formée (une déclaration d'entité, etc) Sur cette transformation, en faire une seconde qui va supprimer tout ce qui est xml et garder que le texte ET qui 
pourra modifier les espaces simplement (translate ou un autre truc) ainsi qu'adapter les détails à LaTeX, comme les - - qui donne un tiret correct, ou transformer tous les e en &, etc-->

<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:tex="placeholder.uri"
    exclude-result-prefixes="tex">
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
            \documentclass[francais,oneside,a4paper, 12pt]{book}
            \input{../../latex/preambule.tex}
            \begin{document}
            \setstretch{1,1}
           \begin{linenumbers}[1]
           <!-- changes the default format of the linenumbers-->
           \renewcommand\linenumberfont{\normalfont\mdseries\footnotesize}
           <!-- changes the default format of the linenumbers-->
        </xsl:text>
        <xsl:apply-templates/>
        <xsl:text>\end{linenumbers}
        \end{document}</xsl:text>


    </xsl:template>


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
    <xsl:template match="tei:note">
        <xsl:text>\footnote{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>

    <xsl:template match="tei:head">
        <xsl:text>\textit{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>

    <xsl:template match="tei:w">
        <xsl:apply-templates/>
<!--        <xsl:if test="not(following-sibling::tei:pct[1])">-->
            <xsl:text>~</xsl:text>
        <!--</xsl:if>-->
    </xsl:template>

    <xsl:template match="tei:pct">
        <xsl:apply-templates/>
        <xsl:text> </xsl:text>
    </xsl:template>

    <!--A terme remplace les tei:hi pour de l'istruction de mise en page dans les notes-->
    <xsl:template match="tei:foreign">
        <xsl:text>\textit{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>
    <!--A terme remplace les tei:hi pour de l'istruction de mise en page dans les notes-->

    <!--MISE EN PAGE-->





    <!--AJOUTS-->
    <!--ajouts du copiste en exposant (interlinéaire) ou en note (marge): deuxième niveau de 
        notes ou ajout en exposation. Si appartient à un apparat, simple indication avec le 
        terme ajouté en italique-->
    <xsl:template match="tei:add">
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
                <xsl:choose>
                    <!--Si l'apparat n'est pas un apparat principal mais un apparat de point notables (notable)
                    >> note. On peut accepter la note de bas de page (éviter les notes de bas de page dans un apparat
                    critique...)-->
                    <xsl:when test="(ancestor::tei:app/@type = 'notable')">
                        <xsl:text>\footnote{Ajouté en marge:\textit{</xsl:text>
                        <xsl:apply-templates select="tei:rdg"/>
                        <xsl:text>}}</xsl:text>
                    </xsl:when>
                    <!--Si l'apparat n'est pas un apparat principal mais un apparat de point notables (notable)-->
                    <xsl:otherwise>
                        <xsl:text>[ajouté en marge:\textit{</xsl:text>
                        <xsl:apply-templates/>
                        <xsl:text>}]</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
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
                    <xsl:value-of select="tei:note"/>
                </xsl:if>
                <xsl:if test="not(@note)"> </xsl:if>
                <xsl:text>}</xsl:text>
            </xsl:if>
        </xsl:if>
        <!--etc-->



    </xsl:template>

    <xsl:template match="tei:ref">
        <xsl:text>\textit{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
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

    <xsl:template match="tei:lb">
        <xsl:text> // </xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:title">
        <xsl:text>\textit{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>

    <xsl:template match="tei:unclear" name="unclear">
        <xsl:text>~??</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>??</xsl:text>
    </xsl:template>

    <xsl:template match="tei:choice">
        <xsl:value-of select="tei:corr"/>
        <xsl:value-of select="tei:reg"/>
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
    <xsl:template match="//tei:del" name="del">
        <xsl:text>[[</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]]</xsl:text>
    </xsl:template>
    <!-- ignorer le text entre balises <del>-->


    <xsl:template match="tei:div[not(@subtype)]">
        <xsl:variable name="temoin_courant">
            <xsl:analyze-string select="@xml:id" regex="([A-Za-z]+_[a-zA-Z]+)(.*)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:variable name="temoin_courant2" select="substring-after($temoin_courant, '_')"/>
        <xsl:text>{\LARGE\textbf{Chapitre </xsl:text>
        <xsl:value-of select="@n"/>
        <xsl:text> (base </xsl:text>
        <xsl:value-of select="$temoin_courant2"/>
        <xsl:text>)}}\newline
        
        
        
        </xsl:text>
        <xsl:apply-templates/>
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

    <xsl:template match="tei:quote">
        <xsl:text>ouioui</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>ouioui</xsl:text>
    </xsl:template>




    <xsl:template match="tei:app">
        <xsl:variable name="temoin_courant">
            <xsl:analyze-string select="ancestor::tei:div[@xml:id]/@xml:id"
                regex="([A-Za-z]+_[a-zA-Z]+)(.*)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:variable name="temoin_courant2" select="substring-after($temoin_courant, '_')"/>
        <xsl:text> \Anote{ </xsl:text>
        <!-- test: UNCLEAR entre crochets avec un ?-->
        <xsl:text> </xsl:text>
        <xsl:apply-templates select="tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]"/>
        <xsl:text>}{</xsl:text>
        <xsl:text>\textit{</xsl:text>
        <xsl:value-of select="$temoin_courant2"/>
        <xsl:text>}~|~</xsl:text>
        <xsl:for-each select="tei:rdg[not(contains(translate(@wit, '#', ''), $temoin_courant))]">
            <xsl:variable name="sigle_temoin">
                <xsl:analyze-string select="@wit" regex="([a-zA-Z]*_)([A-Z])">
                    <xsl:matching-substring>
                        <xsl:value-of select="regex-group(2)"/>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:variable>
            <xsl:apply-templates select="."/>
            <xsl:text>\textit{</xsl:text>
            <xsl:value-of select="$sigle_temoin"/>
            <xsl:text>}~</xsl:text>
        </xsl:for-each>
        <xsl:text>}</xsl:text>
    </xsl:template>
    <!--STRUCTURE DU TEXTE-->



    <!--Choisir et marquer le chapitre-->

    <!--Choisir et marquer la glose/traduction-->


    <!--Choisir et marquer la glose/traduction-->




    <!--STRUCTURE DU TEXTE-->

    <!--MISE EN PAGE-->
    <!--Marquer les paragraphes par un retour à la ligne-->
    <xsl:template match="tei:p">
        <xsl:apply-templates/>
        <xsl:text>
            
            
        </xsl:text>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:variable name="remplacement1" select="replace(., '&amp;', '\\&amp;')"/>
        <xsl:value-of select="$remplacement1"/>
    </xsl:template>


</xsl:stylesheet>
