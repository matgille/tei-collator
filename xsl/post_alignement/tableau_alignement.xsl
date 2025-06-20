<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:mgl="https://matthiasgillelevenson.fr"
    xmlns="http://www.w3.org/1999/xhtml" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <!--Feuille de transformation pour créer une table d'alignement en HTML pour faciliter le commentaire-->
    <!--Je suis parti pour gagner du temps d'une base de David Birnbaum 
        ici: http://collatex.obdurodon.org/xml-json-conversion.xhtml-->

    <xsl:output method="html" indent="yes" doctype-system="about:legacy-compat"/>
    <xsl:strip-space elements="*"/>
    <xsl:template name="get-color">
        <xsl:param name="key"/>
        <color>
            <value>
                <xsl:choose>
                    <xsl:when test="$key = 1">#FFB6C1</xsl:when>
                    <!-- Light Pink -->
                    <xsl:when test="$key = 2">#98FB98</xsl:when>
                    <!-- Pale Green -->
                    <xsl:when test="$key = 3">#ADD8E6</xsl:when>
                    <!-- Light Blue -->
                    <xsl:when test="$key = 4">#FFFACD</xsl:when>
                    <!-- Lemon Chiffon -->
                    <xsl:when test="$key = 5">#F0E6FF</xsl:when>
                    <!-- Lavender (Light Purple) -->
                    <xsl:when test="$key = 6">#E0FFFF</xsl:when>
                    <!-- Light Cyan -->
                    <xsl:when test="$key = 7">#FFDAB9</xsl:when>
                    <!-- Peach Puff -->
                    <xsl:when test="$key = 8">#E6E6FA</xsl:when>
                    <!-- Lavender -->
                    <xsl:when test="$key = 9">#FFD1DC</xsl:when>
                    <!-- Pastel Pink -->
                    <xsl:when test="$key = 10">#D2B48C</xsl:when>
                    <!-- Tan -->
                    <xsl:when test="$key = 11">#696969</xsl:when>
                    <!-- Dim Gray -->
                    <xsl:when test="$key = 12">#F5F5F5</xsl:when>
                    <!-- White Smoke -->
                    <xsl:otherwise>#ccabca</xsl:otherwise>
                    <!-- Default color -->
                </xsl:choose>
            </value>
        </color>
    </xsl:template>



    <xsl:template match="/">
        <html>
            <head>
                <title>Tableau d'alignement</title>
                <!--
                <script src="http://code.jquery.com/jquery-1.11.0.min.js"/>
                <script src="../../html/jquery/jquery-3.3.1.min.js"/>
                <script type="text/javascript" src="../../html/js/functions.js" async="async"/>-->
                <style>
                    /* https://www.textfixer.com/tutorials/css-table-color-columns.php */
                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    table td {
                        padding: 7px;
                        border: #4e95f4 1px solid;
                    }
                    /* improve visual readability for IE8 and below */
                    table tr {
                        background: #b8d1f3;
                    }
                    /*  Define the background color for all the ODD table columns  */
                    table tr td:nth-child(odd) {
                        background: #b8d1f3;
                    }
                    /*  Define the background color for all the EVEN table columns  */
                    table tr td:nth-child(even) {
                        background: #dae5f4;
                    }
                    th,
                    td {
                        border: 1px solid black;
                        background: #dae5f4;
                    }
                    td.fitwidth {
                        padding-right: 100px;
                        white-space: nowrap;
                    }
                    td.variante1 {
                        border: 10px solid red;
                    }
                    td.variante2 {
                        border: 10px solid black;
                    }
                    td.grammatical {
                        border: 10px solid grey;
                    }
                    .ann_pos {
                        font-size: 10px;
                        font-weight: bold;
                    }
                    .ann_lemma {
                        font-style: italics;
                    }
                    .legende {
                        width: 600px;
                        position: fixed;
                    }
                    
                    .annotation,
                    .ann_lemma,
                    .ann_pos {
                        display: block;
                        max-width: inherit;
                    }
                    
                    
                    .legende.active {
                        transform: translateY(500px);
                    }</style>




            </head>
            <body id="body">
                <div style="position:fixed; background-color:white; z-index:99999;">
                    <xsl:apply-templates mode="boutons_temoins"/>
                </div>
                <div>
                    <table id="container">
                        <xsl:apply-templates select="mgl:texte"/>
                    </table>
                </div>
                <!--                <button id="pause" style="position:fixed;" true="false">Défile</button>-->


                <!--<div class="legende">
                    <table>
                        <tr>
                            <td class="variante1">
                                <span>Variante</span>
                            </td>
                            <td class="variante2">
                                <span>Lemme différent</span>
                            </td>
                            <td class="grammatical">
                                <span>Variante morphosyntaxique (pos différent)</span>
                            </td>

                            <td>
                                <span id="log">0%</span>
                            </td>
                        </tr>
                    </table>
                </div>-->
                <script>
                    document.addEventListener('DOMContentLoaded', function () {
                    console.log('Hello world');
                    // Sélectionner toutes les cases à cocher avec la classe 'toggle-row'
                    var checkboxes = document.querySelectorAll('.toggle-row');
                    var showbox = document.querySelectorAll('.toggle-toggles');
                    
                    // Ajouter un écouteur d'événement à chaque case à cocher
                    checkboxes.forEach(function (checkbox) {
                    checkbox.addEventListener('change', function () {
                    console.log('Something happened');
                    // Récupérer la valeur de l'attribut 'data-target'
                    var targetClass = this.getAttribute('id');
                    console.log(targetClass);
                    // Sélectionner toutes les lignes avec la classe cible
                    var rows = document.querySelectorAll('.' + targetClass);
                    
                    // Parcourir chaque ligne et modifier son style d'affichage
                    rows.forEach(function (row) {
                    if (checkbox.checked) {
                    console.log('Hide');
                    row.style.display = '';
                    } else {
                    console.log('Show');
                    row.style.display = 'none';
                    }
                    });
                    });
                    });
                    
                    // Ajouter un écouteur d'événement à chaque case à cocher
                    showbox.forEach(function (showbox) {
                    showbox.addEventListener('change', function () {
                    console.log('Something incredible happened');
                    
                    // Sélectionner toutes les lignes avec la classe cible
                    var rows = document.querySelectorAll('.options_wits');
                    
                    // Parcourir chaque ligne et modifier son style d'affichage
                    rows.forEach(function (row) {
                    if (showbox.checked) {
                    console.log('Hide');
                    row.style.display = '';
                    } else {
                    console.log('Show');
                    row.style.display = 'none';
                    }
                    });
                    });
                    });
                    });
                    
                    
                </script>
            </body>
        </html>
    </xsl:template>



    <xsl:template match="text()">
        <xsl:value-of select="normalize-space()"/>
    </xsl:template>


    <xsl:template match="tei:w"/>

    <xsl:template match="mgl:texte/tei:app[1]" mode="boutons_temoins">
        <div>
            <input type="checkbox" class="toggle-toggles" id="toggle-toggles" checked="checked"/>
            <label for="scales">
                <xsl:text>Show</xsl:text>
            </label>
        </div>
        <xsl:for-each select="tei:rdg">
            <xsl:variable name="witness" select="replace(@wit, '#', '')"/>
            <div class="options_wits">
                <input type="checkbox" class="toggle-row" id="{$witness}" name="{$witness}"
                    checked="checked"/>
                <label for="scales">
                    <xsl:value-of select="$witness"/>
                </label>
            </div>
        </xsl:for-each>
    </xsl:template>

    <xsl:template match="tei:rdg" mode="boutons_temoins"/>

    <xsl:template match="mgl:texte/tei:app[1]/tei:rdg">

        <xsl:variable name="witness" select="replace(@wit, '#', '')"/>
        <xsl:variable name="position" select="count(preceding-sibling::tei:rdg) + 1"/>
        <tr class="{$witness}">
            <th style="position:fixed; margin-left:2cm;">
                <xsl:value-of select="@wit"/>
            </th>
            <td class="'fitwidth texte">
                <xsl:attribute name="id">
                    <xsl:value-of select="translate(tei:rdg/tei:w/@xml:id, '_', '')"/>
                </xsl:attribute>
                <xsl:value-of select="tei:rdg/tei:w"/>
                <xsl:if test="tei:rdg/om">
                    <i>omisit</i>
                </xsl:if>
            </td>
        </tr>
        <tr class="{$witness}">
            <xsl:for-each select="//tei:rdg[position() = $position]">

                <!--Créer une règle pour mettre les lieux variants avec une omission d'une certaine couleur. Éventuellement, si on détecte une omission, refaire un tour d'évaluation.-->

                <!--Form comparison-->

                <xsl:variable name="first_form"
                    select="concat('(', string-join(translate(string-join(tei:w/text()), 'áéíóúýv', 'áéíóúýv'), '-'), ')')"/>
                <!--Avec cette expression on va pouvoir isoler les pos d'une même leçon pour pouvoir les comparer entre elles-->
                <xsl:variable name="all_forms" select="
                        string-join(for $i in (parent::tei:app/tei:rdg[position() > 1])
                        return
                            concat('(', string-join(translate(string-join($i/tei:w/text()), 'áéíóúýv', 'áéíóúýv'), '-'), ')'), '|')"/>
                <xsl:variable name="form">
                    <xsl:choose>
                        <xsl:when test="not($first_form != tokenize($all_forms, '\|'))"
                            >True</xsl:when>
                        <xsl:otherwise>False</xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <!--Form comparison-->


                <!--Lemma comparison-->
                <xsl:variable name="first_word_lemma"
                    select="concat('(', string-join(tei:w/@lemma, '-'), ')')"/>
                <xsl:variable name="all_lemmas" select="
                        string-join(for $i in (parent::tei:app/tei:rdg[position() > 1])
                        return
                            concat('(', string-join($i/tei:w/@lemma, '-'), ')'), '|')"/>
                <xsl:variable name="lemma">
                    <xsl:choose>
                        <xsl:when test="ancestor::tei:app/@type = 'lexicale'">False</xsl:when>
                        <xsl:otherwise>True</xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <!--Lemma comparison-->




                <!--Pos comparison-->
                <xsl:variable name="first_word_pos"
                    select="concat('(', string-join(tei:w/@pos, '-'), ')')"/>
                <!--Avec cette expression on va pouvoir isoler les pos d'une même leçon pour pouvoir les comparer entre elles-->
                <xsl:variable name="all_poss" select="
                        string-join(for $i in (parent::tei:app/tei:rdg[position() > 1])
                        return
                            concat('(', string-join($i/tei:w/@pos, '-'), ')'), '|')"/>
                <xsl:variable name="pos">
                    <xsl:choose>
                        <xsl:when test="not($first_word_pos != tokenize($all_poss, '\|'))"
                            >True</xsl:when>
                        <xsl:otherwise>False</xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <!--Pos comparison-->

                <xsl:variable name="comparison_value">
                    <xsl:choose>
                        <!--<xsl:when test="$pos = 'True' and $lemma = 'True'">fitwidth texte</xsl:when>-->
                        <xsl:when test="$lemma = 'True'">fitwidth texte</xsl:when>
                        <xsl:otherwise>
                            <xsl:text>fitwidth texte variante1</xsl:text>
                            <!--<xsl:if test="$pos = 'False' and $lemma = 'False'">fitwidth texte variante1</xsl:if>
                            <xsl:if test="$pos = 'False' and $lemma = 'True'">fitwidth texte grammatical</xsl:if>
                            <xsl:if test="$pos = 'True' and $lemma = 'False'">fitwidth texte variante2</xsl:if>-->
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>

                <xsl:element name="td" namespace="http://www.w3.org/1999/xhtml">
                    <xsl:attribute name="class" select="$comparison_value"/>
                    <xsl:if test="tei:w">
                        <xsl:attribute name="id">
                            <xsl:value-of select="translate(string-join(tei:w/@xml:id), '_', '')"/>
                        </xsl:attribute>
                        <xsl:variable name="color">
                            <xsl:call-template name="get-color">
                                <xsl:with-param name="key" select="@color"/>
                                <!-- Change this value to test different keys -->
                            </xsl:call-template>
                        </xsl:variable>
                        <xsl:attribute name="style">
                            <xsl:text>background: </xsl:text>
                            <xsl:value-of select="$color"/>
                            <xsl:text>;</xsl:text>
                        </xsl:attribute>
                        <span class="forme">
                            <xsl:value-of select="tei:w"/>
                        </span>
                        <span id="ann_{translate(string-join(tei:w/@xml:id), '_', '')}">
                            <!--<span class="ann_lemma annotation">
                                <xsl:value-of select="tei:w/@lemma"/>

                            </span>
                            <span class="ann_pos annotation">
                                <xsl:value-of select="tei:w/@pos"/>
                            </span>-->
                        </span>
                    </xsl:if>
                    <xsl:if test="om">
                        <xsl:attribute name="id">
                            <xsl:value-of select="concat('om_', count(preceding::om) + 1)"/>
                        </xsl:attribute>
                        <span style="background: #B1CCC7">
                            <i>omisit</i>
                        </span>
                    </xsl:if>
                </xsl:element>
            </xsl:for-each>
        </tr>
    </xsl:template>


</xsl:stylesheet>
