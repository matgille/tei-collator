<?xml version="1.0" encoding="UTF-8"?>
<!--Cette feuille est la troisième phase d'injection: on ajoute la ponctuation en comparant le
fichier précédent avec la transcription tokenisée originelle. 
Résultat: un fichier final qui marche !-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:tei="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output method="xml"/>
    <xsl:strip-space elements="*"/>

    <xsl:param name="nom_fichier"/>

    <xsl:template match="@* | node()">
        <xsl:copy copy-namespaces="yes">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/">
        <xsl:result-document href="resultat/{$nom_fichier}">
            <xsl:apply-templates/>
        </xsl:result-document>
    </xsl:template>


    <xsl:template match="tei:w">
        <xsl:variable name="xml_id" select="@xml:id"/>
        <xsl:variable name="temoins_tokenises_regularises"
            select="concat('../../temoins_tokenises_regularises/', $nom_fichier)"/>
        <xsl:choose>
            <xsl:when test="document($temoins_tokenises_regularises)//tei:w[@xml:id = $xml_id]">
                <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
                    <xsl:attribute name="xml:id" select="@xml:id"/>
                    <xsl:attribute name="lemma"
                        select="document($temoins_tokenises_regularises)//tei:w[@xml:id = $xml_id]/@lemma"/>
                    <xsl:if
                        test="document($temoins_tokenises_regularises)//tei:w[@xml:id = $xml_id]/@pos">
                        <xsl:attribute name="pos"
                            select="document($temoins_tokenises_regularises)//tei:w[@xml:id = $xml_id]/@pos"
                        />
                    </xsl:if>
                    <xsl:if
                        test="document($temoins_tokenises_regularises)//tei:w[@xml:id = $xml_id]/@morph">
                        <xsl:attribute name="morph"
                            select="document($temoins_tokenises_regularises)//tei:w[@xml:id = $xml_id]/@morph"
                        />
                    </xsl:if>
                    <xsl:copy-of select="node() | text()"/>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
