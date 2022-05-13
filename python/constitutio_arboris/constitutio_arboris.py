import glob

from lxml import etree


def substring_after(string, delimiter):
    """
    Function that returns the string after the first delimiter (if there is more than one)
    """
    return string.split(delimiter)[1]


class seeder:
    def __init__(self, signtificative_variants):
        self.significative_variants = signtificative_variants
        self.tei_ns = 'http://www.tei-c.org/ns/1.0'
        self.ns_decl = {'tei': self.tei_ns}  # pour la recherche d'éléments avec la méthode xpath


    def create_tables(self, files):
        analysis_list = []
        variatio_list = []
        for file in glob.glob(files):
            with open(file, 'r') as input_file:
                f = etree.parse(file)
            significative_variants = f.xpath(f"//tei:app[contains(@ana, '{self.significative_variants}')]", namespaces=self.ns_decl)
            for apparatus in significative_variants:
                apparatus_dict = {}
                intermed_list = []
                # In case of readingGroups
                if apparatus.xpath("boolean(descendant::tei:rdgGrp)", namespaces=self.ns_decl):
                    for readingGroup in apparatus.xpath("descendant::tei:rdgGrp", namespaces=self.ns_decl):
                        # We get the first element of our reading group as lectio, as they all read the same modulo graphical variation
                        lectio = readingGroup.xpath("descendant::tei:rdg[1]/descendant::tei:w/text()", namespaces=self.ns_decl)
                        witnesses = " ".join(readingGroup.xpath("descendant::tei:rdg/@wit", namespaces=self.ns_decl)).replace("#", "").split()
                        try:
                            apparatus_dict[lectio[0]] = [substring_after(witness, "_") for witness in witnesses]
                        # Si on a un IndexError, c'est que le tei:rdg n'a pas d'enfant, et qu'il s'agit donc d'une omission
                        except IndexError:
                            apparatus_dict["om."] = [substring_after(witness, "_") for witness in witnesses]
                        intermed_list.append([substring_after(witness, "_") for witness in witnesses])
                else:
                    for reading in apparatus.xpath("descendant::tei:rdg", namespaces=self.ns_decl):
                        # We get the first element of our reading group as lectio, as they all read the same modulo graphical variation
                        lectio = reading.xpath("descendant::tei:w/text()", namespaces=self.ns_decl)
                        witnesses = " ".join(reading.xpath("@wit", namespaces=self.ns_decl)).replace("#", "").split()
                        try:
                            apparatus_dict[lectio[0]] = [substring_after(witness, "_") for witness in witnesses]
                        # Si on a un IndexError, c'est que le tei:rdg n'a pas d'enfant, et qu'il s'agit donc d'une omission
                        except IndexError:
                            apparatus_dict["om."] = [substring_after(witness, "_") for witness in witnesses]
                        intermed_list.append([substring_after(witness, "_") for witness in witnesses])

                analysis_list.append(intermed_list)
                variatio_list.append(apparatus_dict)


        with open("/home/mgl/Documents/variatio_list", "w") as output:
            for locus in variatio_list:
                output.write("/".join(locus.keys()))
                output.write("\t")
                output.write("/".join([" ".join(value) for value in locus.values()]))
                output.write("\n")


        # Maintenant on va travailler sur le regroupement des variantes de façon statistique, sans
        # regarder le texte qui varie (suppose d'avoir une typologie de qualité.
        wit_list = ['A', 'B', 'G', 'Q', 'J', 'R', 'Z']
        dictionnary = {}
        for witness in wit_list:
            witlist_without_witness = wit_list.copy()
            witlist_without_witness.remove(witness)
            for corresponding_witness in witlist_without_witness:
                for locus in analysis_list:
                    for reading in locus:
                        if witness in reading and corresponding_witness in reading:
                            try:
                                dictionnary[f"{witness}{corresponding_witness}"] += 1
                            except:
                                dictionnary[f"{witness}{corresponding_witness}"] = 1

        output_dict = {}
        for key, value in dictionnary.items():
            if key[1] + key[0] in output_dict:
                pass
            else: output_dict[key] = value


        output_list = [[key, value] for key, value in output_dict.items()]
        output_list.sort(key=lambda x:x[1], reverse=True)
        with open("/home/mgl/Documents/reading_stats.txt", "w") as stats_output:
            for element in output_list:
                stats_output.write(f"{element[1]}\t{element[0]}\n")

if __name__ == '__main__':
    seeder = seeder(signtificative_variants="lexicale")
    seeder.create_tables("/home/mgl/Bureau/These/Edition/collator/divs/div*/apparat_Sal_J_*_injected_punct.transposed.xml")