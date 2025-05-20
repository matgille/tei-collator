<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" xmlns:xi="http://www.w3.org/2001/XInclude"
    xmlns:chezmoi="https://www.matthiasgillelevenson.fr" version="2.0">
    <!--Cette feuille permet de produire un document csv qui sera utilisé pour filtrer les variantes lexicales.-->
    <xsl:output method="html"/>
    <xsl:strip-space elements="*"/>

    <xsl:variable name="tokens"
        select="tokenize('Rome_1607 Rome_1556 Planck Bevilaqua_1498 Vat_Lat_590 CCC_MSS_283 Borgh_360 Geneve_Ms_Lat_92 Beinecke_Marston_MS_139 BNE_MSS_958 BNF_Lat_6477 BNE_9236  BNF_Lat_1234 Valencia_BH_Ms_0594', '\s+')"/>




    <xsl:template match="/">
        <xsl:for-each select="descendant::tei:div[@type = 'chapitre']">
            <xsl:variable name="chapitre" select="@n"/>
            <xsl:result-document href="/home/mgl/Téléchargements/{$chapitre}.html">
                <xsl:text disable-output-escaping="yes">&lt;!DOCTYPE html&gt;</xsl:text>
                <html>
                    <meta name="viewport" charset="UTF-8" content="height=100%, 
                        width=100%, initial-scale=1.0, 
                        minimum-scale=0.5, maximum-scale=1.5, 
                        user-scalable=yes, target-densitydpi=device-dpi"/>
                    <head>
                        <title>Tableau d'alignement</title>
                        <style>
                            /* https://www.textfixer.com/tutorials/css-table-color-columns.php */
                            
                            body {
                                font-size: 180%;
                                font-family: Garamond, serif;
                            }
                            sup {
                                vertical-align: top;
                                font-size: 0.6em;
                            }
                            table {
                                display: table;
                            }
                            table tr {
                                display: table-cell;
                                max-width: 3000px;
                            }
                            table tr td {
                                display: block;
                                text-align: center;
                                padding-left: 10px;
                                padding-right: 10px;
                                white-space: nowrap;
                            
                            }
                            
                            tr:nth-child(even) {
                                background-color: #f2f2f2;
                            }
                            tr:hover {
                                background-color: #ddd;
                            }
                            /*  Define the background color for all the ODD table columns  */
                            table tr td:nth-child(odd):not(.white) {
                                background: #e5e5e5;
                            }
                            /*  Define the background color for all the EVEN table columns  */
                            table tr td:nth-child(even):not(.white) {
                                background: white;
                            }
                            
                            /*  Define the background color for all the ODD table columns  */
                            .sigla:nth-child(odd):not(.white) {
                                /*background: #dae5f4;*/
                                background-color: white !important;
                                padding-right: 425px !important;
                                padding-left: 20px !important;
                                outline: black 1px solid;
                            }
                            /*  Define the background color for all the EVEN table columns  */
                            .sigla:nth-child(even):not(.white) {
                                /*background: #b8d1f3;*/
                                background-color: white !important;
                                padding-right: 425px !important;
                                padding-left: 20px !important;
                                outline: black 1px solid;
                            }
                            a:link {
                                text-decoration: none;
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
                            .white {
                                color: rgba(0, 0, 0, 0) !important;
                                ;
                            }
                            .transparent {
                                background-color: white !important;
                            }
                            .sigla {
                                background-color: white !important;
                                font-style: bold;
                            }
                            .analyse {
                                background-color: #ce688d !important;
                            }
                            .lexicale {
                                background-color: #65b9b4 !important;
                            }
                            .trad {
                                background-color: #f3ffcc !important;
                            }
                            .glose {
                                background-color: #ffbd76 !important;
                            }
                            .head {
                                background-color: #cfa9e7 !important;
                            }
                            .transparent_text {
                                color: rgba(0, 0, 0, 0) !important;
                            }
                            
                            .legende {
                                width: 20px;
                                position: fixed;
                                background-color: rgba(0, 0, 0, 0) !important;
                                left: 8em;
                                scroll-margin-left: 10em;
                                scroll-margin-right: 10em;
                            }</style>



                    </head>
                    <body id="body">
                        <div>
                            <form>
                                <input id="path"
                                    value="/home/mgl/Bureau/Travail/Communications_et_articles/Alignement_multilingue_regimine"/>
                                <button id="button_path" type="button">Apply</button>
                            </form>
                        </div>
                        <table>
                            <tr class="legende">
                                <!--<td>&#160;</td>-->
                                <!--                                <td class="white">~</td>-->
                                <td class="white">~</td>
                                <td class="white">~</td>
                                <td class="white">~</td>
                                <xsl:for-each select="$tokens">
                                    <td class="sigla">
                                        <xsl:value-of select="."/>
                                    </td>
                                </xsl:for-each>
                                <xsl:if test="$chapitre - 1 &gt; 0">
                                    <td class="sigla white">
                                        <a href="chapitre_{$chapitre - 1}.html"> Chapitre <xsl:value-of select="$chapitre - 1"/>
                                        </a>
                                    </td>
                                </xsl:if>
                                <xsl:if test="$chapitre + 1 &lt; 24">
                                    <td class="sigla white">
                                        <a href="chapitre_{$chapitre + 1}.html"> Chapitre <xsl:value-of select="$chapitre + 1"/>
                                        </a>
                                    </td>
                                </xsl:if>
                            </tr>
                            <xsl:apply-templates select="descendant-or-self::tei:app"/>
                        </table>
                    </body>

                    <script>
                        
                        let savedValue = '/home/mgl/Bureau/Travail/Communications_et_articles/Alignement_multilingue_regimine';
                        const inputElement = document.getElementById('path');
                        const buttonElement = document.getElementById('button_path');
                        // Ajoute un écouteur d'événements sur le bouton
                        buttonElement.addEventListener('click', function() {
                        
                        // Récupère la valeur de l'input
                        const inputValue = inputElement.value;
                        
                        // Enregistre la valeur dans une variable
                        savedValue = inputValue;
                        
                        // Affiche la valeur enregistrée dans la console (ou toute autre utilisation)
                        console.log('Valeur enregistrée :', savedValue);
                        });
                        
                        function pastLineURL() {
                        const lastLineCells = document.querySelectorAll('td[data-last-line]');
                        lastLineCells.forEach(function(cell) {
                        cell.addEventListener('click', function() {
                        console.log("Here " +  savedValue);
                        var lineUrl = this.getAttribute('data-last-line');
                        console.log(copyContent)
                        var copyContent = "oxygen.sh " + savedValue + lineUrl
                        navigator.clipboard.writeText(copyContent).then(function() {
                        console.log('Copied to clipboard: ' + copyContent);
                        }).catch(function(err) {
                        console.error('Failed to copy: ', err);
                        });
                        });
                        });
                        }
                        
                        // Function to generate a random color
                        function getRandomColor() {
                        return '#' + Math.floor(Math.random() * 16777215).toString(16);
                        }
                        
                        // Function to cluster and color the table cells
                        function clusterAndColorCells() {
                        console.log('Run');
                        // Reset all cells in the table to default
                        document.querySelectorAll('#myTable td').forEach(td => td.style.backgroundColor = '');
                        
                        // Find all unique texts in the table excluding rows with class 'not_apparat'
                        const uniqueTexts = [...new Set(
                        Array.from(document.querySelectorAll('#myTable tr'))
                        .filter(tr => !tr.querySelector('.not_apparat')) // Exclude rows with 'not_apparat' class
                        .flatMap(tr => Array.from(tr.querySelectorAll('td')).map(td => td.textContent))
                        )];
                        
                        // Create a color map for each unique text
                        const colors = {};
                        uniqueTexts.forEach(text => {
                        colors[text] = getRandomColor();
                        });
                        
                        // Highlight all cells in applicable rows based on their cluster colors
                        document.querySelectorAll('#myTable tr')
                        .forEach(tr => {
                        // Skip rows containing cells with class 'not_apparat'
                        if (!tr.querySelector('.not_apparat')) {
                        tr.querySelectorAll('td').forEach(td => {
                        const text = td.textContent;
                        td.style.backgroundColor = colors[text];
                        });
                        }
                        });
                        }
                        
                        // Run the function when the page loads
                        window.addEventListener('load', clusterAndColorCells);
                        document.addEventListener('DOMContentLoaded', pastLineURL, clusterAndColorCells);
                    </script>
                </html>
            </xsl:result-document>
        </xsl:for-each>

    </xsl:template>

    <xsl:template match="tei:app | tei:desc | tei:note | tei:fw | tei:hi[@rend = 'lettre_attente']"/>
    <xsl:template match="tei:hi">
        <xsl:value-of select="."/>
    </xsl:template>

    <xsl:template match="tei:choice">
        <xsl:apply-templates select="tei:reg | tei:corr | tei:expan"/>
    </xsl:template>

    <xsl:template match="tei:sic">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:function name="chezmoi:map_types">
        <xsl:param name="class"/>
        <xsl:variable name="key_1" select="translate($class, '#', '')"/>
        <xsl:variable name="key_2" select="replace($key_1, 'not_apparat', '~')"/>
        <xsl:variable name="key_3" select="replace($key_2, 'lexicale', 'lex.')"/>
        <xsl:variable name="key_4" select="replace($key_3, 'graphique', 'graph.')"/>
        <xsl:variable name="key_5" select="replace($key_4, 'omission', 'om.')"/>
        <xsl:variable name="key_6" select="replace($key_5, 'morphosyntaxique', 'morph.')"/>
        <xsl:variable name="key_7" select="replace($key_6, 'transposition', 'transp.')"/>
        <xsl:variable name="key_8" select="replace($key_7, 'normalisation', 'norm.')"/>
        <xsl:variable name="key_9" select="replace($key_8, 'entite_nommee', 'n.propre')"/>
        <xsl:variable name="key_10" select="replace($key_9, ' ', '/')"/>
        <xsl:value-of select="$key_10"/>
    </xsl:function>

    <xsl:template match="tei:quote">
        <div class="quote">
            <xsl:apply-templates/>
        </div>
    </xsl:template>

    <xsl:template match="tei:app" priority="10">
        <xsl:variable name="chapter" select="ancestor-or-self::tei:div[@type = 'chapitre']/@n"/>
        <xsl:variable name="self" select="self::node()"/>
        <xsl:variable name="ancestor">
            <xsl:choose>
                <xsl:when test="ancestor-or-self::tei:ab">
                    <xsl:text>ab</xsl:text>
                </xsl:when>
                <xsl:when test="ancestor-or-self::tei:p">
                    <xsl:text>p</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>head</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <tr>
            <td class="{translate($ancestor, '\.', '')}">
                <xsl:value-of select="$ancestor"/>
            </td>
            <xsl:choose>
                <xsl:when test="preceding::node()[1][self::tei:witEnd[@ana = '#homeoteleuton']]">
                    <td class="analyse">
                        <xsl:text>homéotéleute</xsl:text>
                    </td>
                </xsl:when>
                <xsl:when test="preceding::node()[1][self::tei:space]">
                    <td class="analyse">
                        <xsl:text>blanc (</xsl:text>
                        <xsl:value-of select="chezmoi:witstosigla(preceding::node()[1][self::tei:space]/@corresp)"/>
                        <xsl:text>)</xsl:text>
                    </td>
                </xsl:when>
                <xsl:when test="descendant::tei:pb">
                    <td class="analyse">
                        <xsl:choose>
                            <xsl:when test="descendant::tei:pb/@corresp">
                                <xsl:value-of select="chezmoi:witstosigla(descendant::tei:pb/@corresp)"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="chezmoi:witstosigla(descendant::tei:pb/ancestor::tei:rdg/@wit)"/>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:text>: fol. </xsl:text>
                        <xsl:value-of select="descendant::tei:pb/@n"/>
                    </td>
                </xsl:when>
                <xsl:otherwise>
                    <td class="white">~</td>
                </xsl:otherwise>
            </xsl:choose>

            <!--
            <td>
                <xsl:value-of select="position()"/>
            </td>-->
            <td class="{translate($self/@ana, '#', '')} transparent">
                <xsl:value-of select="chezmoi:map_types($self/@ana)"/>
            </td>
            <xsl:for-each select="$tokens">
                <xsl:variable name="current_sigla">
                    <xsl:value-of select="."/>
                </xsl:variable>
                <xsl:variable name="last_line">
                    <xsl:text>/data/HTR/txt_1/</xsl:text>
                    <xsl:value-of select="$current_sigla"/>
                    <xsl:text>/sortie_HTR/</xsl:text>
                    <xsl:value-of select="$current_sigla"/>
                    <xsl:text>_out.replaced.xml#</xsl:text>
                    <xsl:choose>
                        <xsl:when test="$self/descendant::tei:lb[@break = 'yes'][contains(@facs, $current_sigla)]">
                            <xsl:value-of
                                select="$self/descendant::tei:lb[@break = 'yes'][contains(@facs, $current_sigla)][1]/replace(@xml:id, 'elem', 'facs')"
                            />
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of
                                select="$self/preceding::tei:lb[contains(@facs, $current_sigla)][1]/replace(@xml:id, 'elem', 'facs')"
                            />
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <td data-last-line="{$last_line}" sigla="{$current_sigla}">
                    <xsl:choose>
                        <xsl:when test="$self/descendant::tei:rdg[contains(@wit, $current_sigla)]/tei:w">
                            <xsl:apply-templates select="$self/descendant::tei:rdg[contains(@wit, $current_sigla)]/tei:w"/>
                            <xsl:if
                                test="$self/descendant::tei:rdg[contains(@wit, $current_sigla)]/tei:w/following-sibling::tei:pc[contains(@corresp, $current_sigla)]">
                                <xsl:value-of
                                    select="$self/descendant::tei:rdg[contains(@wit, $current_sigla)]/tei:w/following-sibling::tei:pc[contains(@corresp, $current_sigla)]"
                                />
                            </xsl:if>
                        </xsl:when>
                        <xsl:otherwise>
                            <i>
                                <span class="transparent_text">om.</span>
                            </i>
                        </xsl:otherwise>
                    </xsl:choose>
                </td>
            </xsl:for-each>
        </tr>

    </xsl:template>

    <xsl:function name="chezmoi:witstosigla">
        <xsl:param name="witnesses"/>
        <xsl:for-each select="tokenize(string-join($witnesses, ' '), '\s')">
            <xsl:value-of select="substring-after(., '_')"/>
        </xsl:for-each>
    </xsl:function>



</xsl:stylesheet>
