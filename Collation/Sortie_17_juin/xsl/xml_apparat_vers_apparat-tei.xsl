<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="xml"/>
    <!--Idée de la feuille de transformation: on a un alignement qui a été fait, il suffit juste de le compléter en regroupant les leçons une à une. 
        On va utiliser essentiellement pour cela la fonction xpath position(). En un second temps il s'agit de rendre les informations 
        d'identifiant pour chaque token.-->
    <!--Il apparaît que collatex, dans le cas d'une sortie JSON, ne s'occupe que de l'alignement. Pour créer un apparat, il faut s'occuper de comparer les chaînes de caractères une à une.
    C'est vraiment une limite pour collatex... Il faut donc s'occuper des lemmes communs et du texte qui n'est pas dans un apparat. Demander à Elisa.-->

    <xsl:template match="/">
        <racine>
            <xsl:apply-templates/>
        </racine>
    </xsl:template>


    <xsl:template match="//table">
        <!--Processus: aller regarder un item, comparer aux autres items qui ont la même position. Si la chaîne est identique pour tous les témoins, 
        l'imprimer comme un noeud textuel simple. -->
        <!--Si la chaîne est différente, créer une balise d'apparat. -->
        <!--Si la valeur de item est null, créer un apparat avec un rdg vide.-->
        <xsl:for-each select="item[1]/item">
            <!--Trouver la position du noeud item courant. Fonctionnel-->
            <xsl:variable name="position"
                select="count(preceding::item[parent::item[not(parent::item)]]) + 1"/>
            <!--Trouver la position du noeud item courant-->
            <xsl:if test="@type = 'null'">

                <app>
                    <xsl:attribute name="pos">
                        <xsl:value-of select="$position"/>
                    </xsl:attribute>
                    <!--Créer un apparat avec une omission. Fonctionnel.-->
                    <xsl:element name="rdg">
                        <xsl:attribute name="wit">
                            <xsl:variable name="position_temoin"
                                select="count(preceding::item[child::item[child::item]]) + 1"/>
                            <xsl:variable name="nom_temoin"
                                select="//witnesses/item[position() = $position_temoin]"/>
                            <xsl:value-of select="concat('#', $nom_temoin)"/>
                        </xsl:attribute>
                    </xsl:element>


                    <!--Créer un apparat avec une omission. Non Fonctionnel.-->
                    <xsl:variable name="identite">
                        <xsl:for-each select="//table/item[position() > 1]/item">
                            <xsl:variable name="position_temoin"
                                select="count(preceding::item[child::item[child::item]]) + 1"/>
                            <xsl:variable name="position"
                                select="count(preceding::item[parent::item[not(parent::item)]]) + 1"/>
                            <xsl:variable name="noeud_textuel1" select="descendant::t"/>
                            <xsl:variable name="noeud_textuel0"
                                select="preceding::item[parent::item[position() = $position_temoin - 1][not(parent::item)]][position() = $position]//t"/>
                            <xsl:choose>
                                <xsl:when test="$noeud_textuel0 = $noeud_textuel1">
                                    <xsl:text>0</xsl:text>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>1</xsl:text>
                                    <xsl:value-of select="$noeud_textuel0"/>

                                    <xsl:value-of select="$noeud_textuel1"/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:for-each>
                    </xsl:variable>


                    <appa>
                        <xsl:value-of select="$identite"/>
                    </appa>

                    <xsl:choose>
                        <!--Quand les chaînes de même position sont identiques-->
                        <xsl:when test="not(//item/descendant::t)"/>
                    </xsl:choose>

                    <!--Pour chaque autre chaîne de l'alignement-->



                    <!--         <xsl:variable name="autres_temoin"
                        select="count(preceding::item[child::item[child::item]]) + 1"/>
                        <xsl:element name="rdg">
                        <xsl:attribute name="wit">
                            <xsl:variable name="position_temoin"
                                select="count(preceding::item[child::item[child::item]]) + 1"/>
                            <xsl:variable name="nom_temoin"
                                select="//witnesses/item[position() = $position_temoin]"/>
                            <xsl:value-of select="concat('#', $nom_temoin)"/>
                        </xsl:attribute>
                        <xsl:value-of select="descendant::t"/>
                    </xsl:element>
-->
                </app>
            </xsl:if>








            <xsl:if test="@type = 'dict'">
                <xsl:variable name="chaine_comparee">
                    <xsl:value-of select="descendant::t"/>
                </xsl:variable>
                <xsl:choose>
                    <!--Si on retrouve exactement la même chaîne de caractère-->
                    <xsl:when
                        test="descendant::t/text() = //item[position() > 1][not(parent::item)]/item[position() = $position]/t/text()">
                        <!--Gestion de la différence entre les -->
                        <xsl:choose>


                            <!--Si toutes les chaînes sont identiques (si aucune des chaîne n'est différente): ne pas créer d'apparat-->
                            <xsl:when
                                test="not(descendant::t/text() != //item[position() > 1][not(parent::item)]/item[position() = $position]/t/text())">
                                <xsl:for-each select="descendant::t">
                                    <xsl:element name="w">
                                        <xsl:attribute name="xml:id">
                                            <xsl:value-of select="following-sibling::xmlid"/>
                                        </xsl:attribute>
                                        <xsl:value-of select="."/>
                                    </xsl:element>
                                </xsl:for-each>
                            </xsl:when>
                            <!--Si toutes les chaînes sont identiques (si aucune des chaîne n'est différente)-->


                            <!--Sinon-->
                            <xsl:otherwise>
                                <xsl:element name="rdg">
                                    <xsl:attribute name="wit"/>
                                    <xsl:for-each select="descendant::t">
                                        <xsl:element name="w">
                                            <xsl:attribute name="xml:id">
                                                <xsl:value-of select="following-sibling::xmlid"/>
                                            </xsl:attribute>
                                            <xsl:value-of select="t"/>
                                        </xsl:element>
                                    </xsl:for-each>
                                </xsl:element>
                                <xsl:for-each
                                    select="//item[position() > 1][not(parent::item)]/item[position() = $position]">
                                    <xsl:element name="rdg">
                                        <xsl:attribute name="wit"/>
                                        <xsl:for-each select="descendant::t">
                                            <xsl:element name="w">
                                                <xsl:attribute name="xml:id">
                                                  <xsl:value-of select="following-sibling::xlmid"/>
                                                </xsl:attribute>
                                                <xsl:value-of select="."/>
                                            </xsl:element>
                                        </xsl:for-each>
                                    </xsl:element>
                                </xsl:for-each>
                            </xsl:otherwise>


                        </xsl:choose>
                    </xsl:when>



                    <xsl:otherwise>
                        <xsl:element name="rdg">
                            <xsl:attribute name="temoin">les_temoins_concernés</xsl:attribute>
                            <xsl:value-of select="t"/>
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>

            </xsl:if>
            <!--select="//table/item[position() > 1]/item[position() = $position]-->


        </xsl:for-each>
    </xsl:template>


    <!--Ignorer la branche witness qui n'apporte aucune nouvelle information-->
    <xsl:template match="witnesses"/>
    <!--Ignorer la branche witness qui n'apporte aucune nouvelle information-->



</xsl:stylesheet>
