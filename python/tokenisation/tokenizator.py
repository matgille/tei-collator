import re
from lxml import etree
import xml.etree.ElementTree as ET
from lxml.etree import XMLSyntaxError
from xml.etree import ElementTree
import traceback
import shutil


with open("tokentest.txt", "r") as file:
    test_string = file.read().replace('\n', ' ')


def main(temoin, punctuation):
    dtd = etree.DTD(file="/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/schemas/Sev_Z.dtd")  # read DTD
    parser = etree.XMLParser(load_dtd=True,
                             resolve_entities=True)  # inutile car les entités ont déjà été résolues
    # auparavant normalement, mais au cas où.
    f = etree.parse(temoin, parser=parser)
    root = f.getroot()
    tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
    groupe_p = "//tei:p[@n][node()]"
    paragraphs = root.xpath(groupe_p, namespaces=tei)
    n = 0
    for paragraph in paragraphs:
        p = paragraph.xpath("@n", namespaces=tei)[0]
        try:
            transformation_string(etree.tostring(paragraph, encoding='utf-8', xml_declaration=True).decode('utf-8').replace("\n", ""), punctuation, p)
        except Exception as e:
            print("Exception for paragraph %s: \n %s" % (p, traceback.format_exc()))
            n = n + 1
            continue
    xml_output(output_dict, file)
    print("number of errors: %s of %s paragraphs" % (n, len(paragraphs)))


def xml_output(output_dict, file):
    # shutil.copy(file, "~/Bureau/tests/sev_z.xml")
    parser = etree.XMLParser(load_dtd=True,
                             resolve_entities=True)  # inutile car les entités ont déjà été résolues
    # auparavant normalement, mais au cas où.
    f = etree.parse(file, parser=parser)
    root = f.getroot()
    tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
    groupe_p = "//tei:p[@n][node()]"
    paragraphs = root.xpath(groupe_p, namespaces=tei)
    for paragraph in paragraphs:
        p = paragraph.xpath("@n", namespaces=tei)[0]
        print("@n = %s" % p)
        try:
            paragraph.getparent().replace(paragraph,etree.fromstring(output_dict[p]))
        except Exception as e:
            print("Exception: \n %s" % e)
            continue

    with open("/home/mgl/Bureau/tests/sev_zz.xml", "w+") as sortie_xml:
        output = etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode(
            'utf8')
        sortie_xml.write(str(output))

def xml_output_production(string, step):
    """
    Replaces all tei:desc by the structure
    :param dictionnary: the dictionnary created by the different extraction steps
    :return:
    """
    tei_namespace = "http://www.tei-c.org/ns/1.0"
    NSMAP1 = {'tei': tei_namespace}  # pour la recherche d'éléments avec la méthode xpath
    ElementTree.register_namespace("", tei_namespace)  # http://effbot.org/zone/element-namespaces.htm#preserving
    # -existing-namespace-attributes
    output_file = "%s_output.xml" % str(step)
    orig_file = "orig.xml"

    with open("%s_output.txt" % str(step), "w+") as sortie_txt:
        sortie_txt.write(string)

    with open(output_file, "w+") as sortie_xml:
        output_root = etree.fromstring(string)
        output = etree.tostring(output_root, pretty_print=True, encoding='utf-8', xml_declaration=True).decode(
            'utf8')
        sortie_xml.write(str(output))



def ajout_pc(string):
    result = "<pc>%s</pc>" % string
    return result

def ajout_w(string):
    result = "<w>%s</w>" % string
    return result

def colon_out(string):
    string = string.replace("xml:id", "xml-id")
    return string


def colon_in(string):
    string = string.replace("xml-id", "xml:id")
    return string



def space_tokenisation(string):
    result = re.split("[\s]", string)
    result = [item for item in result if item != " "]
    return result

def punct_tokenisation(string, punctuation):
    # the colon is not included in the list
    pattern = re.compile(r"([%s])</w><w>" % punctuation)
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</w><pc>%s</pc><w>" % (match.group(1)))

    pattern2 = re.compile(r'([%s])<([^<w\/>]*)>' % punctuation)
    matched = re.finditer(pattern2, string)
    for match in matched:
        string = string.replace(match.group(0), "</w><pc>%s</pc><%s>" % (match.group(1), match.group(2)))

    pattern3 = re.compile(r'<\/pc><(?!seg|w)([^<>]*)')
    matched = re.finditer(pattern3, string)
    for match in matched:
        string = string.replace(match.group(0), "</pc><w><%s" % (match.group(1)))

    return string

def colon_management(string):
    pattern = re.compile("<w>([A-Za-zçáéíóúý]*):([A-Za-zçáéíóúý]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<w>%s</w><pc>:</pc><w>%s</w>" % (match.group(1), match.group(2)))
    return string

def tei_space_management(string):
    pattern = re.compile("([^<>]*)<space/>([^<>]*)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s</w><space/><w>%s" % (match.group(1), match.group(2)))
    return string

def multiple_w_removal(string):
    pattern = re.compile("<w></w>")
    while re.search(pattern, string) is not None:
        string = string.replace("<w></w>", "")
    pattern = re.compile("<w><w>")
    while re.search(pattern, string) is not None:
        string = string.replace("<w><w>", "<w>")
    pattern2 = re.compile("</w></w>")
    while re.search(pattern2, string) is not None:
        string = string.replace("</w></w>", "</w>")
    pattern3 = re.compile("<pc></w>")
    while re.search(pattern3, string) is not None:
        string = string.replace("<pc></w>", "")
    pattern4 = re.compile("<w></pc>")
    while re.search(pattern4, string) is not None:
        string = string.replace("<w></pc>", "")
    pattern = re.compile("^(<p[^<>]*>)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), match.group(1))
    pattern = re.compile("<w><([^<>w]*)><w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<%s><w>" % match.group(1))

    return string

def xml_declaration_removal(string):
    string = string.replace("<?xml version=\'1.0\' encoding=\'utf-8\'?>", "")
    return string

def p_removal(string):
    pattern = re.compile("^<p[^<>]*>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "")

    pattern = re.compile("</p>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "")



    return string

def space_preparation(string):


    pattern = re.compile(r"<choice type=\"segmentation\"><orig/><reg><space/></reg></choice>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), " ")


    pattern = re.compile("<([^<>]*)\s([^<>]*)>")
    while re.search(pattern, string) is not None:
        matched = re.finditer(pattern, string)
        for match in matched:
            string = string.replace(match.group(0), "<%s+-%s>" % (match.group(1), match.group(2)))
    return string


def remove_hyphens(string):
    string = string.replace("+-", " ").replace("<w></w>", "")
    return string


def foreign_management(string):

    string = string.replace("<w><foreign>", "<foreign><w>")
    string = string.replace("</foreign></w>", "</w></foreign>")
    return string


def choice_management(string):

    pattern = re.compile(r"</w><w><choice></w><w><sic>([^<>]*)</sic></w><w><corr>([^<>]*)</corr></w><w></choice></w><w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<w><choice><sic>%s</sic><corr>%s</corr></choice></w><w>" % (match[1], match[2]))

    pattern = re.compile(
        r"</w><w><choice></w><w><sic>([^<>]*)</sic></w><w><corr>([^<>]*)</corr></w><w></choice><lb break=\"n\"")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0),
                                "<w><choice><sic>%s</sic><corr>%s</corr></choice><lb break=\"n\"" % (match[1], match[2]))

    pattern = re.compile(
        r"<space/><choice></w><w><sic>([^<>]*)</sic></w><w><corr>([^<>]*)</corr></w><w></choice></w><w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0),
                                "<space/><w><choice><sic>%s</sic><corr>%s</corr></choice></w>" % (match[1], match[2]))

    string = string.replace("</choice><space/><choice>", "</choice></w><space/><w><choice>")
    string = string.replace("</choice><space/><w>", "</choice></w><space/><w>")

    pattern = re.compile(
        r"</w>([^<>]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</w><w>%s</w>" % match[1])

    pattern = re.compile(r"</w>([^<>]*)<choice>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</w><w>%s<choice>" % match[1])


    pattern = re.compile(r"</choice>([^<>]*)<w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</choice>%s</w><w>" % match[1])


    pattern = re.compile(r"</choice>([^<>]*)<space/><w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</choice>%s<space/></w><w>" % match[1])


    return string

def seg_management(string):
    pattern = re.compile(r"<(w|pc)><(title|seg)([^<>]*)>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<%s%s><%s>" % (match[2], match[3],match[1]))

    pattern2 = re.compile(r"</(title|seg)></(w|pc)>")
    matched = re.finditer(pattern2, string)
    for match in matched:
        string = string.replace(match.group(0), "</%s></%s>" % (match[2], match[1]))


    pattern3 = re.compile(r"<(title|seg)([^<>]*)>([A-Za-zçáéíóúý]*)</w>")
    matched = re.finditer(pattern3, string)
    for match in matched:
        string = string.replace(match.group(0), "<%s%s><w>%s</w>" % (match[1], match[2], match[3]))



    pattern4 = re.compile(r"<(title|seg)([^<>]*)><([^w]*)>")
    matched = re.finditer(pattern4, string)
    for match in matched:
        string = string.replace(match.group(0), "<%s%s><w><%s>" % (match[1], match[2], match[3]))

    return string

def milestone_management(string):


    pattern = re.compile(r"(<milestone[^<>]*/>)<choice")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s<w><choice" % match.group(1))

    pattern = re.compile(r"<w>(<milestone[^<>]*/>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s<w>" % match.group(1))


    pattern = re.compile(r"(<milestone[^<>]*/>)([^<>]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s<w>%s</w>" % (match.group(1), match.group(2)))




    pattern = re.compile(r"<space/>([^<>]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<space/><w>%s</w>" % match.group(1))

    pattern = re.compile(r"</choice>([^<>]*)<milestone")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</choice>%s</w><milestone" % match.group(1))

    return string

def notes_management(string):
    pattern = re.compile(r"<note([^<>]*)>(.+?)(?=<\/note)<\/note>")
    matched = re.finditer(pattern, string)
    for match in matched:
        transformed_string = match[2].replace("<w>", " ").replace("</w>", "").replace("<pc>", "").replace("</pc>", "")
        string = string.replace(match.group(0), "<note%s>%s</note>" % (match[1], transformed_string))

    new_pattern = re.compile(r"<([^<>/]*)>([^<>]*)(<note([^<>]*)>(.+?)(?=<\/note)<\/note>)(</[^<>]*>)")
    matched = re.finditer(new_pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<%s>%s</%s>%s" % (match.group(1), match.group(2), match.group(1),
                                                                   match.group(3)))


    pattern3 = re.compile(r"(<note([^<>]*)>(.+?)(?=<\/note)<\/note>)</w>")
    matched = re.finditer(pattern3, string)
    for match in matched:
        string = string.replace(match.group(0), "</w>%s" % match.group(1))


    return string

def fw_management(string):
    pattern = re.compile(r"(<w>){0,1}<fw([^<>]*)>(.+?)(?=<\/fw)<\/fw>(</w>){0,1}")
    matched = re.finditer(pattern, string)
    for match in matched:
        transformed_string = match[3].replace("<w>", "").replace("</w>", " ").replace("<pc>", " ").replace("</pc>", "")
        string = string.replace(match.group(0), "<fw%s>%s</fw>" % (match[2], transformed_string))

    string = string.replace("</fw><lb break=\"y\"", "</fw></w><lb break=\"y\"")

    # pattern = re.compile(r"(<fw([^<>]*)>(.+?)(?=<\/fw<\/fw></w>){0,1}")
    # matched = re.finditer(pattern, string)
    # for match in matched:
    #     string = string.replace(match.group(0), "<fw%s>%s</fw>" % (match[2])
    return string

def comments_management(string):
    pattern = re.compile(r"<w><!--([^>]*)--></w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<!--%s-->" % match[1])


    pattern = re.compile(r"<!--([^-]*)--></w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</w><!--%s-->" % match[1])
    return string

def multiple_elements_management(string):
    string = string.replace("</persName></w>","</w></persName>")

    pattern = re.compile(r"<w><persName([^<>]*)>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<persName%s><w>" % match[1])

    pattern = re.compile("<w>([^<>]*)<persName")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<w>%s</w><persName" % match[1])

    pattern = re.compile("<persName([^<>]*)>([^<>]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<persName%s><w>%s</w>" % (match[1], match[2]))

    pattern = re.compile("(<\/w><note[^<>]*>.+?(?=<\/note)<\/note>)<\/w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s" % match[1])

    pattern = re.compile("([^<>]*)<note")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s</w><note" % match[1])



    pattern = re.compile("(^<p[^<>]*>)</w><note")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s<note" % match[1])


    string = string.replace("<w><said>","<said><w>")
    string = string.replace("</said></w>","</w></said>")
    string = string.replace("<w><persName>","<persName><w>")
    string = string.replace("</persName>:</w>", "</w></persName><pc>:</pc>")
    string = string.replace("<w><date>","<date><w>")
    string = string.replace("</date></w>","</w></date>")
    string = string.replace("<cb break=\"y\"/></w>", "<cb break=\"y\"/>")
    string = string.replace("<cb break=\"y\"/><w><lb break=\"y\"", "<cb break=\"y\"/><lb break=\"y\"")
    string = string.replace("</w><lb break=\"n\"", "<lb break=\"n\"")
    string = string.replace("</fw></w>", "</fw>")
    string = string.replace("</seg></w>", "</w></seg>")
    string = string.replace("</fw><cb break=\"y\"", "</fw></w><cb break=\"y\"")
    string = string.replace("</pc><w></seg>", "</pc></seg>")
    string = string.replace("<w></seg>", "</seg>")
    string = string.replace("<cb break=\"n\"/></w>", "<cb break=\"n\"/>")
    string = string.replace("<choice type=\"segmentation\"><orig></w><w></orig><reg/></choice>", "")
    string = string.replace("</title>:</w>", "</w></title><pc>:</pc>")
    string = string.replace("<space/><w>", "</w><space/><w>")
    string = string.replace("</w></w><space/><w>", "</w><space/><w>")
    string = string.replace("</pc></w>", "</pc>")
    string = string.replace("<cb break=\"y\"/><w></p>", "<cb break=\"y\"/></p>")
    string = string.replace("</choice><space/>", "</choice></w><space/>")


    pattern = re.compile("<space/>([^<>]*)<choice")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<space/><w>%s<choice" % match.group(1))


    pattern = re.compile("<space/>([^<>]*)</w")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<space/><w>%s</w" % match.group(1))


    pattern = re.compile(r"(<[p|l]b[^<>]*break=\"y\"[^<>]{0,400}\/>)</w>(<[p|l]b[^<>]*break=\"y\"[^<>]*\/>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s%s" % (match.group(1),match.group(2)))

    pattern = re.compile("<w>([^<>]*)</seg>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<w>%s</w></seg>" % match.group(1))


    pattern = re.compile(r"(<[p|l]b[^<>]*break=\"y\"[^<>]*\/>)<w>(<fw[^<>]*>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s%s" % (match.group(1),match.group(2)))


    pattern = re.compile(r"(<[p|l]b[^<>]*break=\"n\"[^<>]*\/>)</w>(<fw[^<>]*>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s%s" % (match.group(1),match.group(2)))


    pattern = re.compile(r"(<w>([^<>]*)<w>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<w>%s</w><w>" % match.group(1))

    pattern = re.compile(r"<w><w>([^<>]*)<w></w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<w>%s</w><w>" % match.group(1))


    string = string.replace("<w><w>", "<w>")

    pattern = re.compile(r"<(title|seg)([^<>]*)></w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<%s%s>" % (match[1], match[2]))

    pattern = re.compile("</said>([^<>]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</said><w>%s</w>" % match[1])


    pattern = re.compile("([A-Za-zçáéíóúý]*)</said>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s</w></said>" % match[1])


    pattern3 = re.compile("<choice></w><w><sic>([^><]*)</sic></w><w><corr>([^><]*)</corr></w><w></choice>")
    matched = re.finditer(pattern3, string)
    for match in matched:
        string = string.replace(match.group(0), "<choice><sic>%s</sic><corr>%s</corr></choice>>" % (match[1], match[2]))

    pattern4 = re.compile("<choice><\/w><w><sic\/><\/w><w><corr>([^><]*)<\/corr><\/w><w><\/choice>")
    matched = re.finditer(pattern4, string)
    for match in matched:
        string = string.replace(match.group(0), "<choice><sic/><corr>%s</corr></choice>" % (match[1]))


    pattern5 = re.compile("<choice><\/w><w><sic>([^><]*)<\/sic><\/w><w><corr\/><\/w><w><\/choice>")
    matched = re.finditer(pattern5, string)
    for match in matched:
        string = string.replace(match.group(0), "<choice><sic>%s</sic><corr/></choice>" % (match[1]))


    pattern = re.compile(r"<w>([^<>]*)(<milestone[^<>]*\/>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<w>%s</w>%s" % (match.group(1), match.group(2)))


    pattern = re.compile(r"<lb break=\"n\"([^<>]*)/>([^<>]*)(<milestone[^<>]*\/>)([^<>]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<lb break=\"n\"%s/>%s</w>%s<w>%s</w>" % (match.group(1), match.group(2), match.group(3), match.group(4)))



    pattern = re.compile(r"<lb break=\"n\"([^<>]*)/>([^<>]*)(<milestone[^<>]*\/>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<lb break=\"n\"%s/>%s</w>%s" % (match.group(1), match.group(2), match.group(3)))

    pattern = re.compile("</note>([^<>]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</note><w>%s</w>" % match[1])


    pattern = re.compile(">([^<>]*)<space\/><w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), ">%s</w><space/><w>" % match.group(1))


    pattern = re.compile("(<[l|p|c]b\s[^<>]*break=\"n\"\s{0,1}[^<>]*\/>)([^<>]{1,500})<w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s%s</w><w>" % (match.group(1), match.group(2)))


    pattern = re.compile(r"(<milestone[^<>]*/>)([^<>]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s<w>%s</w>" % (match.group(1), match.group(2)))

    pattern = re.compile(r"</seg>([^<>]*)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s</w></seg>" % match.group(1))

    pattern2 = re.compile("</w></w>")
    while re.search(pattern2, string) is not None:
        string = string.replace("</w></w>", "</w>")


    string = string.replace("/w>:</w>", "/w><w>:</w>")
    string = string.replace("</title></w>", "</w></title>")

    ########################################################
    return string
    ########################################################



def breaks_corr(string):
    pattern = re.compile(r"<w>([A-Za-zçáéíóúý]*)(<[l|p|c]b\s[^<>]*break=\"y\"\s{0,1}[^<>]*\/>)([^<>]*)?<\/w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<w>%s</w>%s<w>%s</w>" % (match.group(1), match.group(2), match.group(3)))
    string = string.replace("<cb break=\"n\"/></w>", "<cb break=\"n\"/>")
    return string


def linebreaks_corr(string):
    pattern = re.compile(r"(<[c|p|l]b[^<>]*break=\"y\"[^<>]*\/>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</w>%s<w>" % match.group(1))


    pattern = re.compile(r"(<[p|l]b[^<>]*break=\"y\"[^<>]*\/>)<w><fw")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s<fw" % match.group(1))


    pattern = re.compile(r"<w>(<lb[^<>]*break=\"n\"[^<>]*\/>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s" % match.group(1))

    pattern = re.compile(r"(<pb[^<>]*break=\"n\"[^<>]*\/>)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s" % match.group(1))


    string = string.replace("</choice></w><lb break=\"n\"", "</choice><lb break=\"n\"")

    #
    # pattern = re.compile(r"<([^<>w]*)><choice")
    # matched = re.finditer(pattern, string)
    # for match in matched:
    #     string = string.replace(match.group(0), "<%s><w><choice" % match.group(1))
    # string = string.replace("<w><w><choice", "<w><choice")
    #
    #
    # pattern = re.compile(r"<(lb break=\"n\"[^<>]*)/><w><choice")
    # matched = re.finditer(pattern, string)
    # for match in matched:
    #     string = string.replace(match.group(0), "<%s/><choice" % match.group(1))

    return string

def namespace_adding(string):
    pattern = re.compile(r"<([^!\/<>]*)>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<%s namespace=\"http://www.tei-c.org/ns/1.0\">" % (match.group(1)))
    return string



def transformation_string(test_string, punctuation, att_n):
    test_string = xml_declaration_removal(test_string)
    test_string = p_removal(test_string)
    test_string = space_preparation(test_string)
    test_string = colon_out(test_string)
    string_list = space_tokenisation(test_string)
    output_list = [ajout_w(item) for item in string_list]
    output_string = "".join(output_list)
    output_string = punct_tokenisation(output_string, punctuation)
    output_string = remove_hyphens(output_string)
    output_string = notes_management(output_string)
    output_string = fw_management(output_string)
    output_string = milestone_management(output_string)
    output_string = comments_management(output_string)
    output_string = seg_management(output_string)
    output_string = breaks_corr(output_string)
    output_string = linebreaks_corr(output_string)
    # output_string = tei_space_management(output_string)
    output_string ="<p n=\"%s\">%s</p>" % (att_n, output_string)
    output_string = colon_management(output_string)
    output_string = colon_in(output_string)
    output_string = multiple_w_removal(output_string)
    output_string = choice_management(output_string)
    output_string = foreign_management(output_string)
    output_string = multiple_elements_management(output_string)
    output_string = namespace_adding(output_string)
    n = 8940
    # print(output_string[n-20:n+20])
    xml_output_production(output_string, att_n)
    output_dict[att_n] = output_string

if __name__ == '__main__':
    output_dict = {}
    punctuation = "\.¿?!;,"
    file = "/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/analyse_linguistique/Sev_Z.xml"
    main(file, punctuation)
