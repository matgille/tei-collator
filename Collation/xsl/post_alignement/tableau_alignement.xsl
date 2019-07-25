<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <!--Feuille de transformation pour créer une table d'alignement en HTML pour faciliter le commentaire-->
    <!--Je suis parti pour gagner du temps d'une base de David Birnbaum 
        ici: http://collatex.obdurodon.org/xml-json-conversion.xhtml-->

    <xsl:output method="xml" indent="yes" doctype-system="about:legacy-compat"/>
    <xsl:strip-space elements="*"/>
    <xsl:template match="/">
        <html>
            <head>
                <title>Tableau d'alignement</title>


                <style type="text/css">
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
            </body>
        </html>
    </xsl:template>
    <xsl:template match="text()">
        <xsl:value-of select="normalize-space()"/>
    </xsl:template>
    <xsl:template match="w"/>

    <xsl:template match="texte/app[1]/rdg">
        <xsl:variable name="position" select="count(preceding-sibling::rdg) + 1"/>
        <tr>
            <th>
                <xsl:value-of select="@wit"/>
            </th>
            <td class="fitwidth">
                <xsl:value-of select="rdg/w"/>
                <xsl:if test="rdg/om">
                    <i>ommisit</i>
                </xsl:if>
            </td>
        </tr>
        <tr>
            <xsl:for-each select="//rdg[position() = $position]">
                <td class="fitwidth">
                    <xsl:value-of select="w"/>
                    <xsl:if test="om">
                        <i>ommisit</i>
                    </xsl:if>
                </td>
            </xsl:for-each>
        </tr>
    </xsl:template>


</xsl:stylesheet>
