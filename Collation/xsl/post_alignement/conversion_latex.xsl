<?xml version="1.0" encoding="ISO-8859-1"?>
<!--PROBLEMES-->
<!--REFAIRE LES REGLES D AJOUTS EN MARGE-->
<!--notable: tout ce qui est notable (renommer le type)-->
<!--Int�grer les notes dans un apparat de lemmes...-->
<!--R�gulariser les diff�rences dans les add entre above et pas above-->

<!-- IDEE: G�rer les modifications textuelles: Et si je faisais ma transformation en deux temps? D'abord, toutes les grosses transformations EN GARDANT UNE STRUCTURE XML BASIQUE
    et bien form�e (une d�claration d'entit�, etc) Sur cette transformation, en faire une seconde qui va supprimer tout ce qui est xml et garder que le texte ET qui 
pourra modifier les espaces simplement (translate ou un autre truc) ainsi qu'adapter les d�tails � LaTeX, comme les - - qui donne un tiret correct, ou transformer tous les e en &, etc-->

<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:tex="placeholder.uri"
    exclude-result-prefixes="tex">
    <!--RECOMMAND�: la feuille xsl est construite pour une utilisation du document .tex comme annexe 
        vers laquelle pointe le document principal (utilisant \input{...} par exemple).-->
    <!--IMP�RATIF: Le package latex utilis� pour l'apparat est ednotes (https://www.ctan.org/pkg/ednotes). 
    Il doit imp�rativement �tre accompagn� du package lineno (https://www.ctan.org/pkg/lineno)
    et du package manyfoot (https://www.ctan.org/pkg/manyfoot) pour 
    les diff�rents niveaux de notes 
    (\DeclareNewFootnote{B}[arabic]
\usepackage{perpage}
\MakePerPage{footnote}
\renewcommand{\thefootnote}{\alph{footnote}} pour adapter le pr�ambule LaTex � la feuille de transformation)
    , ainsi que du package marginpar (https://www.ctan.org/pkg/marginpar)
    pour permettre l'indication en marge des lacunes et des commencements/fins de t�moins-->
    <!--Je propose mon preambule LaTex � l'adresse: http://perso.ens-lyon.fr/matthias.gille-levenson/preambule.txt. 
    Si le lien est p�rim�, me contacter sur mon adresse ens: matthias.gille-levenson[arobase]ens[point]fr -->
    <!--Cette feuille est adapt�e � mon propre document XML-->
    <!--Merci � Arianne Pinche pour son aide pr�cieuse dans cette feuille-->
    <!--Merci � Marjorie Burghart de m'avoir envoy� sa feuille de transformation qui m'a bien aid�-->
    <xsl:output method="text" omit-xml-declaration="no" encoding="UTF-8"/>
    <xsl:strip-space elements="*"/>
    <xsl:template match="/">
        <xsl:text>\textbf{Sigles des t�moins}\newline\newline</xsl:text>
        <xsl:for-each
            select="/tei:TEI/tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:listWit/tei:witness">
            <xsl:text>\noindent \textbf{</xsl:text>
            <xsl:value-of select="@xml:id"/>
            <xsl:text>}: </xsl:text>
            <xsl:value-of select="text()"/>
            <xsl:text>\newline </xsl:text>
        </xsl:for-each>
        <xsl:text> 
            \setstretch{1,1}
           \begin{linenumbers}[1]
           <!-- changes the default format of the linenumbers-->
           \renewcommand\linenumberfont{\normalfont\mdseries\footnotesize}
           <!-- changes the default format of the linenumbers-->
        \modulolinenumbers[5]</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>\end{linenumbers}</xsl:text>


    </xsl:template>


    <xsl:template match="tei:persName[@type = 'auteur']">
        <xsl:text>\textsc{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>




    <!--Notes en bas de page. -->
    <!--Est ce que je me complique pas la vie � �crire deux fois les m�mes r�gles?-->
    <!--Si la note est th�matique, second niveau de notes, appel en chiffres arabes-->
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
        <xsl:text> </xsl:text>
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
    <!--ajouts du copiste en exposant (interlin�aire) ou en note (marge): deuxi�me niveau de 
        notes ou ajout en exposation. Si appartient � un apparat, simple indication avec le 
        terme ajout� en italique-->
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
                    >> note. On peut accepter la note de bas de page (�viter les notes de bas de page dans un apparat
                    critique...)-->
                    <xsl:when test="(ancestor::tei:app/@type = 'notable')">
                        <xsl:text>\footnote{Ajout� en marge:\textit{</xsl:text>
                        <xsl:apply-templates select="tei:rdg"/>
                        <xsl:text>}}</xsl:text>
                    </xsl:when>
                    <!--Si l'apparat n'est pas un apparat principal mais un apparat de point notables (notable)-->
                    <xsl:otherwise>
                        <xsl:text>[ajout� en marge:\textit{</xsl:text>
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
                <xsl:text>Ajout� </xsl:text>
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

    <xsl:template match="tei:subst">
        <xsl:apply-templates/>
    </xsl:template>

    <!--MODIFICATIONS CORRECTIONS-->
    <xsl:template match="//tei:space" name="space">
        <xsl:text>\indent</xsl:text>
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


    <xsl:template match="tei:damage" name="damage">
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
    </xsl:template>

    <xsl:template match="tei:gap">
        <xsl:text>\indent</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <!-- ignorer le text entre balises <del>-->
    <xsl:template match="//tei:del" name="del">
        <xsl:text>[[</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]]</xsl:text>
    </xsl:template>
    <!-- ignorer le text entre balises <del>-->




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
            <xsl:analyze-string select="ancestor::tei:div[@xml:id]/@xml:id" regex="([.*]_[.*])[.*]">
                <xsl:matching-substring>
                    <xsl:value-of select="regex-group(1)"/>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:variable>
        <xsl:text> \Anote{ </xsl:text>
        <!-- test: UNCLEAR entre crochets avec un ?-->
        <xsl:value-of select="tei:rdg[translate(@wit, '#', '') = $temoin_courant]"/>
        <xsl:text>}{</xsl:text>
        <xsl:text>\textit{</xsl:text>
        <xsl:value-of
            select="tei:rdg[translate(@wit, '#', '') = $temoin_courant]/translate(@wit, '#_', ' ')"/>
        <xsl:text>};~</xsl:text>
        <xsl:for-each select="tei:rdg[translate(@wit, '#', '') != $temoin_courant]">
            <!--La suite au prochain num�ro-->
        </xsl:for-each>
    </xsl:template>
    <!--STRUCTURE DU TEXTE-->



    <!--Choisir et marquer le chapitre-->

    <!--Choisir et marquer la glose/traduction-->


    <!--Choisir et marquer la glose/traduction-->




    <!--STRUCTURE DU TEXTE-->

    <!--MISE EN PAGE-->
    <!--Marquer les paragraphes par un retour � la ligne-->
    <xsl:template match="tei:p">
        <xsl:apply-templates/>
        <xsl:text>
            
            
        </xsl:text>
    </xsl:template>



</xsl:stylesheet>
