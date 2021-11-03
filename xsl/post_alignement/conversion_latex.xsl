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
    <xsl:param name="fusion"/>
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
            \documentclass[francais,oneside,a4paper,12pt]{book}
        </xsl:text>
        <xsl:choose>
            <xsl:when test="$fusion = 'True'"
                >\input{../latex/preambule.tex}</xsl:when>
            <!--Ça ne devrait pas marcher, bizarre.-->
            <xsl:otherwise>
                <xsl:text>\input{latex/preambule.tex}</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>
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
        match="tei:note[@type = 'general'][not(parent::tei:head)][not(@subtype = 'lexicale')]">
        <xsl:text>\footnote{</xsl:text>
        <xsl:choose>
            <xsl:when test="@corresp">
                <xsl:text>[</xsl:text>
                <xsl:value-of select="translate(translate(@corresp, '#', ''), '_', ' ')"></xsl:value-of>
                <xsl:text>] </xsl:text>
            </xsl:when>
        </xsl:choose>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>

    <xsl:template match="tei:note[@type = 'particulier']">
        <xsl:text>\footnote{</xsl:text>
        <xsl:choose>
            <xsl:when test="@corresp">
                <xsl:text>[</xsl:text>
                <xsl:value-of select="translate(translate(@corresp, '#', ''), '_', ' ')"></xsl:value-of>
                <xsl:text>] </xsl:text>
            </xsl:when>
        </xsl:choose>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>

    <xsl:template match="tei:note[@subtype = 'lexicale'][not(parent::tei:head)]">
        <xsl:text>\footnote{</xsl:text>
        <xsl:choose>
            <xsl:when test="@corresp">
                <xsl:text>[</xsl:text>
                <xsl:value-of select="translate(@corresp, '#', '')"></xsl:value-of>
                <xsl:text>] </xsl:text>
            </xsl:when>
        </xsl:choose>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>


    <xsl:template match="tei:sic[not(@ana = '#omission')]">
        <xsl:apply-templates/>
        <xsl:text>\footnote{\textit{sic}.}</xsl:text>
    </xsl:template>


    <xsl:template match="tei:sic[@ana = '#omission']">
        <xsl:apply-templates/>
        <xsl:text>\footnote{Omission chez le témoin.}</xsl:text>
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

    <xsl:template match="tei:head">
        <xsl:choose>
            <xsl:when test="$fusion = 'False'">
                <xsl:text>{\large\textit{</xsl:text>
                <xsl:apply-templates/>
                <xsl:text>}}
        
        
        </xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:lb"/>

    <xsl:template match="tei:w">
        <xsl:if test="not(parent::tei:del)">
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

    <xsl:template match="tei:teiHeader"/>

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
        <xsl:text>[[</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]]</xsl:text>
    </xsl:template>
    <!-- ignorer le text entre balises <del>-->

    <xsl:template match="tei:div[@type = 'glose']">
        <xsl:text>\marginpar{\textbf{[Glose]}}</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:div[@type = 'traduction']">
        <xsl:apply-templates/>
        <xsl:text>~\\</xsl:text>
    </xsl:template>

    <!--Ici on va créer des règles pour afficher les éléments dans les apparats-->



    <!--Ici on va créer des règles pour afficher les éléments dans les apparats-->




    <xsl:template
        match="tei:div[@type = 'chapitre'][not(@type = 'glose' or @type = 'traduction')]">
        <xsl:variable name="temoin_courant">
            <xsl:analyze-string select="@xml:id"
                regex="([A-Za-z]+_[a-zA-Z]+)(.*)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:variable name="temoin_courant2"
            select="substring-after($temoin_courant, '_')"/>
        <xsl:text>\chapter{Chapitre </xsl:text>
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
        <xsl:text>}</xsl:text>
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
        <xsl:text>``</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>''</xsl:text>
    </xsl:template>


    <!--Les apparats de type filtre sont à ignorer-->
    <xsl:template
        match="tei:app[@type = 'graphique'] | tei:app[@type = 'filtre'][count(descendant::tei:rdg) = 1]">
        <!--Ajouter un test sur la présence d'une note-->
        <xsl:text> </xsl:text>
        <!--Afficher ici la lecture du témoin courant, voir plus bas-->
        <xsl:variable name="temoin_courant">
            <xsl:analyze-string
                select="ancestor::tei:div[@type = 'chapitre'][@xml:id]/@xml:id"
                regex="([A-Za-z]+_[a-zA-Z]+)(.*)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:apply-templates
            select="tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]"/>
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
            <xsl:text>}</xsl:text>
        </xsl:if>

        <xsl:if test="@unit = 'item_rang_2'">
            <xsl:text>\textbf{ </xsl:text>
            <xsl:value-of
                select="preceding::tei:milestone[@unit = 'item_rang_1'][1]/@n"/>
            <xsl:text>.</xsl:text>
            <xsl:value-of select="@n"/>
            <xsl:text> }</xsl:text>
        </xsl:if>

        <xsl:if test="@unit = 'item_rang_3'">
            <xsl:text>\textbf{ </xsl:text>
            <xsl:value-of
                select="preceding::tei:milestone[@unit = 'item_rang_1'][1]/@n"/>
            <xsl:text>.</xsl:text>
            <xsl:value-of
                select="preceding::tei:milestone[@unit = 'item_rang_2'][1]/@n"/>
            <xsl:text>.</xsl:text>
            <xsl:value-of select="@n"/>
            <xsl:text> }</xsl:text>
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
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template
        match="tei:app[@type = 'filtre'][count(descendant::tei:rdg) > 1]">
        <xsl:variable name="temoin_courant">
            <xsl:analyze-string
                select="ancestor::tei:div[@type = 'chapitre'][@xml:id]/@xml:id"
                regex="([A-Za-z]+_[a-zA-Z]+)(.*)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:apply-templates
            select="descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]"
        />
    </xsl:template>



    <xsl:template
        match="tei:app[@type = 'entite_nommee'][count(descendant::tei:rdg) > 1] | tei:app[@type = 'lexicale'][count(descendant::tei:rdg) > 1] | tei:app[@type = 'morphosyntactique'][count(descendant::tei:rdg) > 1] | tei:app[@type = 'indetermine'][count(descendant::tei:rdg) > 1] | tei:app[@type = 'personne'][count(descendant::tei:rdg) > 1]">
        <xsl:text> </xsl:text>
        <xsl:variable name="temoin_courant">
            <xsl:analyze-string
                select="ancestor::tei:div[@type = 'chapitre'][@xml:id]/@xml:id"
                regex="([A-Za-z]+_[a-zA-Z]+)(.*)">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:variable name="temoin_courant2"
            select="substring-after($temoin_courant, '_')"/>
        <xsl:text> \Anote{</xsl:text>
        <!-- test: UNCLEAR entre crochets avec un ?-->
        <xsl:apply-templates
            select="descendant::tei:rdg[contains(translate(@wit, '#', ''), $temoin_courant)]"/>
        <xsl:text>}{</xsl:text>
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
                        <xsl:value-of
                            select="concat($lemma_wits, '`', $siblings)"/>
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
                            <xsl:analyze-string select="@wit"
                                regex="([a-zA-Z]*_)([A-Z])">
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
                <xsl:for-each
                    select="tei:rdg[not(contains(translate(@wit, '#', ''), $temoin_courant))]">
                    <xsl:variable name="sigle_temoin">
                        <xsl:analyze-string select="@wit"
                            regex="([a-zA-Z]*_)([A-Z])">
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

    <xsl:template match="tei:fw"/>

    <xsl:template match="tei:witEnd">
        <xsl:text>\footnote{Le témoin </xsl:text>
        <xsl:value-of select="substring-after(parent::tei:rdg/@wit, '_')"/>
        <xsl:text> s'arrête ici.}</xsl:text>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:variable name="remplacement1"
            select="replace(., '&amp;', '\\&amp;')"/>
        <xsl:value-of select="$remplacement1"/>
    </xsl:template>


</xsl:stylesheet>
