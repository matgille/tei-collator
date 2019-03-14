<?xml version="1.0"?>
<!--Source: https://docstore.mik.ua/orelly/xml/xslt/appd_03.htm-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0" version="2.0">
    <xsl:output method="text"/>

    <xsl:variable name="newline">
        <xsl:text>
</xsl:text>
    </xsl:variable>

    <xsl:key name="elements" match="*" use="name()"/>
    <xsl:template match="tei:teiHeader"/>
    <xsl:template match="/">
        <xsl:for-each select="descendant::tei:TEI[@type = 'transcription']//tei:text">
            <xsl:value-of select="$newline"/>
            <xsl:text>Liste des éléments dans </xsl:text>
            <xsl:value-of select="ancestor::tei:TEI/@xml:id"/>
            <xsl:value-of select="$newline"/>
            <xsl:value-of select="$newline"/>
            <!-- Ça donne pas exactement ce que je veux, mais toutes les balises sortent-->
            <xsl:for-each select="descendant::*[generate-id(.) = generate-id(key('elements', name())[1])]">
                <xsl:sort select="name()"/>
                <xsl:for-each select="key('elements', name())">
                    <xsl:if test="position() = 1">
                        <xsl:text>L'élément </xsl:text>
                        <xsl:value-of select="upper-case(name())"/>
                        <xsl:text> apparaît </xsl:text>
                        <xsl:value-of select="count(//*[name() = name(current())])"/>
                        <xsl:text> fois.</xsl:text>
                        <xsl:value-of select="$newline"/>
                    </xsl:if>
                </xsl:for-each>
            </xsl:for-each>
            <xsl:value-of select="$newline"/>
        </xsl:for-each>
        <xsl:text>Il y a </xsl:text>
        <xsl:value-of select="count(//*)"/>
        <xsl:text> éléments en tout.</xsl:text>
    </xsl:template>

</xsl:stylesheet>
