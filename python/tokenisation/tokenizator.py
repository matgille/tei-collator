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
    groupe_p = "//tei:p[@n='KBFrGbnqTj'][node()]"
    paragraphs = root.xpath(groupe_p, namespaces=tei)
    for paragraph in paragraphs:
        p = paragraph.xpath("@n", namespaces=tei)[0]
        try:
            transformation_string(etree.tostring(paragraph, pretty_print=True, encoding='utf-8', xml_declaration=True).decode('utf-8').replace("\n", ""), punctuation, p)
        except Exception as e:
            print("Exception for paragraph %s: \n %s" % (p, traceback.format_exc()))
            continue
    xml_output(output_dict, file)


def xml_output(output_dict, file):
    # shutil.copy(file, "~/Bureau/tests/sev_z.xml")
    parser = etree.XMLParser(load_dtd=True,
                             resolve_entities=True)  # inutile car les entités ont déjà été résolues
    # auparavant normalement, mais au cas où.
    f = etree.parse(file, parser=parser)
    root = f.getroot()
    tei = {'tei': 'http://www.tei-c.org/ns/1.0'}
    groupe_p = "//tei:p[@n='KBFrGbnqTj'][node()]"
    paragraphs = root.xpath(groupe_p, namespaces=tei)
    for paragraph in paragraphs:
        p = paragraph.xpath("@n", namespaces=tei)[0]
        print("@n = %s" % p)
        try:
            paragraph.getparent().replace(paragraph,etree.fromstring(output_dict[p]))
        except Exception as e:
            print("Exception: \n %s" % e)
            continue


    with open("/home/mgl/Bureau/tests/sev_z.xml", "w+") as sortie_xml:
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
        print(match.group(1))
        string = string.replace(match.group(0), "</pc><w><%s" % (match.group(1)))

    return string

def colon_management(string):
    pattern = re.compile("([A-Za-zçáéíóúý]*):([A-Za-zçáéíóúý]*)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s</w><pc>:</pc><w>%s" % (match.group(1), match.group(2)))
    return string

def tei_space_management(string):
    pattern = re.compile("([A-Za-zçáéíóúý]*)<space/>([A-Za-zçáéíóúý]*)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s</w><space/><w>%s" % (match.group(1), match.group(2)))
    return string

def multiple_w_removal(string):
    print("Removal..")
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
    pattern = re.compile("<([^<>]*)\s([^<>]*)>")
    while re.search(pattern, string) is not None:
        matched = re.finditer(pattern, string)
        for match in matched:
            string = string.replace(match.group(0), "<%s+-%s>" % (match.group(1), match.group(2)))
    return string


def remove_hyphens(string):
    string = string.replace("+-", " ").replace("<w></w>", "")
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

    return string

def milestone_management(string):
    pattern = re.compile(r"<w>(<milestone[^<>]*/>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s<w>" % match.group(1))
    return string

def notes_management(string):
    pattern = re.compile(r"<note([^<>]*)>(.+?)(?=<\/note)<\/note>")
    matched = re.finditer(pattern, string)
    for match in matched:
        transformed_string = match[2].replace("<w>", " ").replace("</w>", "").replace("<pc>", "").replace("</pc>", "")
        string = string.replace(match.group(0), "<note%s>%s</note>" % (match[1], transformed_string))
    new_pattern = re.compile(r"<([^<>]*)>([^<>]*)(<note([^<>]*)>(.+?)(?=<\/note)<\/note>)(</[^<>]*>)")
    matched = re.finditer(new_pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<%s>%s</%s>%s" % (match.group(1), match.group(2), match.group(1),
                                                                   match.group(3)))
    return string

def fw_management(string):
    pattern = re.compile(r"(<w>){0,1}<fw([^<>]*)>(.+?)(?=<\/fw)<\/fw>(</w>){0,1}")
    matched = re.finditer(pattern, string)
    for match in matched:
        transformed_string = match[3].replace("<w>", "").replace("</w>", " ").replace("<pc>", " ").replace("</pc>", "")
        string = string.replace(match.group(0), "<fw%s>%s</fw>" % (match[2], transformed_string))
    return string

def breaks_corr(string):
    pattern = re.compile(r"<w>([A-Za-zçáéíóúý]*)(<[l|p|c]b\s[^<>]*break=\"y\"\s{0,1}[^<>]*\/>)([^<>]*)?<\/w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "<w>%s</w>%s<w>%s</w>" % (match.group(1), match.group(2), match.group(3)))
    return string


def linebreaks_corr(string):
    pattern = re.compile(r"(<lb[^<>]*break=\"y\"[^<>]*\/>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "</w>%s<w>" % match.group(1))

    pattern = re.compile(r"<w>(<lb[^<>]*break=\"n\"[^<>]*\/>)")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s" % match.group(1))

    pattern = re.compile(r"(<pb[^<>]*break=\"n\"[^<>]*\/>)</w>")
    matched = re.finditer(pattern, string)
    for match in matched:
        string = string.replace(match.group(0), "%s" % match.group(1))
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
    output_string = seg_management(output_string)
    output_string = breaks_corr(output_string)
    output_string = linebreaks_corr(output_string)
    # output_string = tei_space_management(output_string)
    output_string = colon_management(output_string)
    output_string ="<p n=\"%s\">%s</p>" % (att_n, output_string)
    output_string = colon_in(output_string)
    output_string = multiple_w_removal(output_string)
    # output_string = namespace_adding(output_string)
    n = 3367
    print(output_string[n-20:n+20])
    xml_output_production(output_string, att_n)
    output_dict[att_n] = output_string

if __name__ == '__main__':
    output_dict = {}
    punctuation = "\.¿?!;,"
    file = "/home/mgl/Bureau/These/Edition/hyperregimiento-de-los-principes/Dedans/XML/analyse_linguistique/Sev_Z.xml"
    main(file, punctuation)
