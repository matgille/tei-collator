màj le 17 juin

http://collatex.obdurodon.org/xml-json-conversion.xhtml 

http://collatex.obdurodon.org/ Pour un tutoriel sur collatex pour python. On va réussir !

pour le passage entre xml et json. 
progrès: j'ai réussi à transformer en un json valide; à faire une première collation et un export vers la TEI. comme prévu, on perd les xml:id. 

Il faut écrire à Marjorie pour voir si cela marche. D'abord, faire les modifications qu'elle a suggérées dans notre rdv. 

Un premier problème s'est posé dans la tokenisation: on perd aussi la ponctuation, trouver un moyen d'y remédier. 

Un autre problème apparaît et semble plus important: la collation n'est pas terrible. Écrire à Elisa pour voir ce qu'elle en pense. Ce problème semble réglé avec la version python, plus à jour, qui propose un algorithme qui semble vraiment bon. 

À faire: compléter le script pour comprendre comment ça marche, transformer en JSON pour conserver les xml:id, voir un script pour transformer les JSON en xml d'apparat. En attendant, les fichiers XML produits permettent assez facilement de corriger les erreurs de transcription !


Un troisième problème: retrouver le contexte marche quand on a une collation mot à mot (un item d'apparat = un mot), mais quand c'est plusieurs mots, comment faire ?   En général, la collation prend maximum 2 mots dans un apparat. 


**Mise à jour du 20 juin**: j'ai créé des scripts qui permettent de passer automatiquement du corpus xml à un apparat simple en xml, avec perte des xml:id pour l'instant. 
J'ai utilisé dictxml pour voir comment transformer du json en xml. Ça marche, mais c'est moche. Il faudra probablement passer par un script python maison. 
 
 **Reste à faire**: ajouter plus de témoins pour voir si collatex gère aussi bien. 


créé le 15 janvier 2019. 

# Le processus de collation 

Pour la collation on va utiliser des fichiers xml à comparer. Pour ce faire, il nous faut un fichier xml par paragraphe à comparer. 
Problème: comment faire quand on a utilisé les entités pour marquer les phénomènes linguistiques ? 
## 1 - Préparation des fichiers

- création d'une feuille de style xsl > 
	_ texte normalisés, pour pouvoir comparer efficacement (generation_w.xsl: tokenise et met dans un w; regularisation.xsl: choisit la forme régularisée comme base de la comparaison)
	
	_ comment retrouver les textes du départ ? utiliser la tokénisation, donner un id pour chaque mot. Suppose de travailler en xml et pas en txt. 
	
	0) *mae&slong-s;tro* vs *mae&slong-s;tra*; dans le document d'origine
	
	
	1) <w xml:id="FNpwCFHBXF">mae&slong-s;tro</w> vs  <w xml:id="FNpwCFHBqoeifh">mae&slong-s;tra</w>
	
	1,5) les entités sont automatiquement résolues: il faut bidouiller avant. > remplacer & par ± et ; par ™
	
	dans le document intermédiaire; [= tokénisation + inclusion dans un <w> avec un xml:id aléatoire]
	
	2) <w xml:id="FNpwCFHBXF">maestro</w> vs <w xml:id="FNpwCFHBqoeifh">maestra</w> 
	
	dans le texte à collationer [= conservation de la seule forme régularisée], pour arriver à  
	
	3) <app>
		<rdg witness="x">
			<w xml:id="FNpwCFHBXF">maestro</w>
		</rdg>
		<rdg witness="y">
			<w xml:id="FNpwCFHBqoeifh">maestra</w>
		</rdg>
	</app>
	
	
	[= collation grâce à collatex][donner la commande de collation avec collatex] et enfin au résultat final: 
	``java -jar ~/Bureau/Programme/collatex-tools-1.7.1.jar -f tei -xml -xp "//w" insev.xml msj.xml -o collation.xml 
	``
	-f tei > au format de sortie TEI
	-xml > format d'entrée xml
	-xp "//w" > expression xpath qui va chercher le texte contenu dans //w
	insev.xml ... > témoins
	-o collation > document de sortie. 
	Pour l'instant, ça marche bien SAUF qu'on perde l'id, ce qui est fort embêtant. Comment faire ? Je suis bloqué là. Ça veut dire pour l'instant que je ne vais pouvoir comparer que régularisé avec régularisé. Est-ce un problème ? 
	
	4) <app>
		<rdg witness="x">
			mae&slong-s;tro
		</rdg>
		<rdg witness="y">
			mae&slong-s;tra
		</rdg>
	</app>
	
	[= retrouver avec l'xml id le mot originel. [xsl:for-each tei:w, xsl:value-of document(...)//w[xml:id='xml:id(.)'] ]]
	[problème: on perd toutes les informations contextuelles: id, les autres balises: suppose de faire la collation avant d'enrichir et de baliser le texte.]
- collation à l'aide de collatex > création de fichiers .dot

- visualisation des fichiers .dot en les transformant en .pdf

- export de la collation en fichiers .xml tei. 


----------------------------------------------
12 mars 2019. Qu'est ce que je veux ? 





