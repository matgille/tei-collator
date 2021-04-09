<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <!--Feuille de transformation pour créer une table d'alignement en HTML pour faciliter le commentaire-->
    <!--Je suis parti pour gagner du temps d'une base de David Birnbaum 
        ici: http://collatex.obdurodon.org/xml-json-conversion.xhtml-->

    <xsl:output method="html" indent="yes"
        doctype-system="about:legacy-compat"/>
    <xsl:strip-space elements="*"/>
    <xsl:template match="/">
        <html>
            <head>
                <title>Tableau d'alignement</title>
                <script src="http://code.jquery.com/jquery-1.11.0.min.js"/>
                <script src="../../html/jquery/jquery-3.3.1.min.js"/>
                <script type="text/javascript" src="../../html/js/functions.js" async="async"/>
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
                        width: 1px;
                        white-space: nowrap;
                    }</style>




            </head>
            <body>
                <h1>Tableau d'alignement</h1>
                <table>
                    <xsl:apply-templates select="texte"/>
                </table>
                <button id="pause" style="position:fixed;"
                    true="false">Défile</button>
            </body>
        </html>
    </xsl:template>
    <xsl:template match="text()">
        <xsl:value-of select="normalize-space()"/>
    </xsl:template>


    <xsl:template match="tei:w"/>

    <xsl:template match="texte/tei:app[1]/tei:rdg">
        <xsl:variable name="position"
            select="count(preceding-sibling::tei:rdg) + 1"/>
        <tr>
            <th style="position:fixed;">
                <xsl:value-of select="@wit"/>
            </th>
            <td class="fitwidth texte">
                <xsl:attribute name="id">
                    <xsl:value-of
                        select="translate(tei:rdg/tei:w/@xml:id, '_', '')"
                    />
                </xsl:attribute>
                <xsl:value-of select="tei:rdg/tei:w"/>
                <xsl:if test="tei:rdg/om">
                    <i>omisit</i>
                </xsl:if>
            </td>
        </tr>
        <tr>
            <xsl:for-each select="//tei:rdg[position() = $position]">
                <td class="fitwidth texte">
                    <xsl:if test="tei:w">
                        <xsl:attribute name="id">
                            <xsl:value-of
                                select="translate(string-join(tei:w/@xml:id), '_', '')"
                            />
                        </xsl:attribute>
                        <xsl:value-of select="tei:w"/>
                        <span class="annotation"
                            id="ann_{translate(string-join(tei:w/@xml:id), '_', '')}">
                            <br/>
                            <i>
                                <xsl:value-of select="tei:w/@lemma"/>
                            </i>
                            <br/>
                            <b>
                                <xsl:value-of select="tei:w/@pos"/>
                            </b>
                        </span>
                    </xsl:if>
                    <xsl:if test="om">
                        <xsl:attribute name="id">
                            <xsl:value-of
                                select="concat('om_', count(preceding::om) + 1)"
                            />
                        </xsl:attribute>
                        <i>omisit</i>
                    </xsl:if>
                </td>
            </xsl:for-each>
        </tr>
    </xsl:template>


</xsl:stylesheet>
