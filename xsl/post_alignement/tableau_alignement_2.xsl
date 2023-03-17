<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"
    xmlns:xi="http://www.w3.org/2001/XInclude" version="2.0">
    <!--Cette feuille permet de produire un document csv qui sera utilisé pour filtrer les variantes lexicales.-->
    <xsl:output method="html"/>
    <xsl:strip-space elements="*"/>

    <xsl:variable name="tokens" select="tokenize('A B G J Q R Z U', '\s')"/>


    <xsl:variable name="tokens_sans_U" select="tokenize('A B G J Q R Z', '\s')"/>


    <xsl:template match="/">
        <xsl:for-each select="descendant::tei:div[@type = 'chapitre']">
            <xsl:variable name="chapitre" select="@n"/>
            <xsl:result-document href="../../divs/div{$chapitre}/alignement_final.html">
                <html>
                    <head>
                        <title>Tableau d'alignement</title>
                        <script src="http://code.jquery.com/jquery-1.11.0.min.js"/>
                        <script src="../../html/jquery/jquery-3.3.1.min.js"/>
                        <script type="text/javascript" src="../../html/js/functions.js" async="async"/>
                        <style>
                            /* https://www.textfixer.com/tutorials/css-table-color-columns.php */
                            
                            table {
                                display: table;
                            }
                            table tr {
                                display: table-cell;
                            }
                            table tr td {
                                display: block;
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
                        <table>
                            <tr>
                                <td>
                                    <a href="../div{$chapitre - 1}/alignement_final.html">Chapitre
                                        précédent</a>
                                </td>
                            </tr>
                            <tr>
                                <td>&#160;</td>
                                <td>&#160;</td>
                                <td>&#160;</td>
                                <xsl:for-each select="$tokens">
                                    <td class="sigla">
                                        <xsl:value-of select="."/>
                                    </td>
                                </xsl:for-each>
                            </tr>
                            <xsl:apply-templates select="descendant-or-self::tei:app"/>
                            <tr>
                                <td>
                                    <a href="../div{$chapitre + 1}/alignement_final.html">Chapitre
                                        suivant</a>
                                </td>
                            </tr>
                        </table>
                    </body>
                </html>
            </xsl:result-document>
        </xsl:for-each>

    </xsl:template>

    <xsl:template match="tei:app | tei:note | tei:desc"/>
    <xsl:template match="tei:hi">
        <xsl:value-of select="."/>
    </xsl:template>

    <xsl:template match="tei:choice">
        <xsl:apply-templates select="tei:reg | tei:corr"/>
    </xsl:template>

    <xsl:template match="tei:app" priority="10">
        <xsl:variable name="chapter" select="ancestor-or-self::tei:div[@type = 'chapitre']/@n"/>
        <xsl:variable name="self" select="self::node()"/>
        <xsl:variable name="ancestor">
            <xsl:choose>
                <xsl:when test="ancestor-or-self::tei:div[@type = 'glose']">
                    <xsl:text>glose</xsl:text>
                </xsl:when>
                <xsl:when test="ancestor-or-self::tei:div[@type = 'traduction']">
                    <xsl:text>trad.</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>head</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <tr>
            <td>
                <xsl:value-of select="$ancestor"/>
            </td>
            <td>
                <xsl:value-of select="position()"/>
            </td>
            <td>
                <xsl:value-of select="$self/@ana"/>
            </td>
            <xsl:for-each select="$tokens">
                <xsl:variable name="current_sigla">
                    <xsl:value-of select="."/>
                </xsl:variable>
                <td>
                    <xsl:choose>
                        <xsl:when test="$self/descendant::tei:rdg[contains(@wit, $current_sigla)]/tei:w">
                            <xsl:apply-templates
                                select="$self/descendant::tei:rdg[contains(@wit, $current_sigla)]/tei:w/text()"
                            />
                        </xsl:when>
                        <xsl:otherwise>
                            <i>om.</i>
                        </xsl:otherwise>
                    </xsl:choose>
                </td>
            </xsl:for-each>
        </tr>
    </xsl:template>



</xsl:stylesheet>
