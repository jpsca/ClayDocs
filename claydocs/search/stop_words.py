"""
Stop-words list
Extracted from https://github.com/fergiemcdowall/stopword/

----
Catalan (ca), Basque (eu), and Greek (el)
Copyright (c) 2017 Peter Graham, contributors
Released under the Apache-2.0 license.

Danish (da)
Creative Commons - Attribution / ShareAlike 3.0 license
http://creativecommons.org/licenses/by-sa/3.0/

German (de)
Copyright (c) 2016 Gene Diaz
Released under the MIT License

Italian (it) and Spanish (es)
Copyright (c) 2011, David Przybilla, Chris Umbel
Released under the MIT License

English (en)
Copyright (c) 2011, Chris Umbel
Released under the MIT License

French (fr)
Copyright (c) 2014, Ismaël Héry

Dutch (nl)
Copyright (c) 2011, Chris Umbel, Martijn de Boer, Damien van Holten
Released under the MIT License

Norwegian (no)
Copyright (c) 2014, Kristoffer Brabrand
Released under the MIT License

Portuguese (pt)
Copyright (c) 2011, Luís Rodrigues
Released under the MIT License

Swedish (sv)
Creative Commons - Attribution / ShareAlike 3.0 license
http://creativecommons.org/licenses/by-sa/3.0/

"""


# Catalan
ca = [
    "a", "abans", "ací", "ah", "així", "això", "al", "aleshores", "algun", "alguna", "algunes", "alguns", "alhora", "allà", "allí", "allò", "als", "altra", "altre", "altres", "amb", "ambdues", "ambdós", "apa", "aquell", "aquella", "aquelles", "aquells", "aquest", "aquesta", "aquestes", "aquests", "aquí", "baix", "cada", "cadascuna", "cadascunes", "cadascuns", "cadascú", "com", "contra", "d'un", "d'una", "d'unes", "d'uns", "dalt", "de", "del", "dels", "des", "després", "dins", "dintre", "donat", "doncs", "durant", "e", "eh", "el", "els", "em", "en", "encara", "ens", "entre", "eren", "es", "esta", "estaven", "esteu", "està", "estàvem", "estàveu", "et", "etc", "ets", "fins", "fora", "gairebé", "ha", "han", "has", "havia", "he", "hem", "heu", "hi", "ho", "i", "igual", "iguals", "ja", "l'hi", "la", "les", "li", "li'n", "llavors", "m'he", "ma", "mal", "malgrat", "mateix", "mateixa", "mateixes", "mateixos", "me", "mentre", "meu", "meus", "meva", "meves", "molt", "molta", "moltes", "molts", "mon", "mons", "més", "n'he", "n'hi", "ne", "ni", "no", "nogensmenys", "només", "nosaltres", "nostra", "nostre", "nostres", "o", "oh", "oi", "on", "pas", "pel", "pels", "per", "perquè", "però", "poc", "poca", "pocs", "poques", "potser", "propi", "qual", "quals", "quan", "quant", "que", "quelcom", "qui", "quin", "quina", "quines", "quins", "què", "s'ha", "s'han", "sa", "semblant", "semblants", "ses", "seu", "seus", "seva", "seves", "si", "sobre", "sobretot", "solament", "sols", "son", "sons", "sota", "sou", "sóc", "són", "t'ha", "t'han", "t'he", "ta", "tal", "també", "tampoc", "tan", "tant", "tanta", "tantes", "teu", "teus", "teva", "teves", "ton", "tons", "tot", "tota", "totes", "tots", "un", "una", "unes", "uns", "us", "va", "vaig", "vam", "van", "vas", "veu", "vosaltres", "vostra", "vostre", "vostres", "érem", "éreu", "és",
]

# Danish
da = [
    "er", "jeg", "det", "du", "ikke", "i", "at", "en", "og", "har", "vi", "til", "på", "hvad", "med", "mig", "så", "for", "de", "dig", "der", "den", "han", "kan", "af", "vil", "var", "her", "et", "skal", "ved", "nu", "men", "om", "ja", "som", "nej", "min", "noget", "ham", "hun", "bare", "kom", "være", "din", "hvor", "dem", "ud", "os", "hvis", "må", "se", "godt", "have", "fra", "ville", "okay", "lige", "op", "alle", "lad", "hvorfor", "sig", "hvordan", "få", "kunne", "eller", "hvem", "man", "bliver", "havde", "da", "ingen", "efter", "når", "alt", "jo", "to", "mit", "ind", "hej", "aldrig", "lidt", "nogen", "over", "også", "mand", "far", "skulle", "selv", "får", "hans", "ser", "vores", "jer", "sådan", "dit", "kun", "deres", "ned", "mine", "komme", "tage", "denne", "sige", "dette", "blive", "helt", "fordi", "end", "tag", "før", "fik", "dine",
]

# German
de = [
    "a", "ab", "aber", "ach", "acht", "achte", "achten", "achter", "achtes", "ag", "alle", "allein", "allem", "allen", "aller", "allerdings", "alles", "allgemeinen", "als", "also", "am", "an", "ander", "andere", "anderem", "anderen", "anderer", "anderes", "anderm", "andern", "anderr", "anders", "au", "auch", "auf", "aus", "ausser", "ausserdem", "außer", "außerdem", "b", "bald", "bei", "beide", "beiden", "beim", "beispiel", "bekannt", "bereits", "besonders", "besser", "besten", "bin", "bis", "bisher", "bist", "c", "d", "d.h", "da", "dabei", "dadurch", "dafür", "dagegen", "daher", "dahin", "dahinter", "damals", "damit", "danach", "daneben", "dank", "dann", "daran", "darauf", "daraus", "darf", "darfst", "darin", "darum", "darunter", "darüber", "das", "dasein", "daselbst", "dass", "dasselbe", "davon", "davor", "dazu", "dazwischen", "daß", "dein", "deine", "deinem", "deinen", "deiner", "deines", "dem", "dementsprechend", "demgegenüber", "demgemäss", "demgemäß", "demselben", "demzufolge", "den", "denen", "denn", "denselben", "der", "deren", "derer", "derjenige", "derjenigen", "dermassen", "dermaßen", "derselbe", "derselben", "des", "deshalb", "desselben", "dessen", "deswegen", "dich", "die", "diejenige", "diejenigen", "dies", "diese", "dieselbe", "dieselben", "diesem", "diesen", "dieser", "dieses", "dir", "doch", "dort", "drei", "drin", "dritte", "dritten", "dritter", "drittes", "du", "durch", "durchaus", "durfte", "durften", "dürfen", "dürft", "e", "eben", "ebenso", "ehrlich", "ei", "ei, ", "eigen", "eigene", "eigenen", "eigener", "eigenes", "ein", "einander", "eine", "einem", "einen", "einer", "eines", "einig", "einige", "einigem", "einigen", "einiger", "einiges", "einmal", "eins", "elf", "en", "ende", "endlich", "entweder", "er", "ernst", "erst", "erste", "ersten", "erster", "erstes", "es", "etwa", "etwas", "euch", "euer", "eure", "eurem", "euren", "eurer", "eures", "f", "folgende", "früher", "fünf", "fünfte", "fünften", "fünfter", "fünftes", "für", "g", "gab", "ganz", "ganze", "ganzen", "ganzer", "ganzes", "gar", "gedurft", "gegen", "gegenüber", "gehabt", "gehen", "geht", "gekannt", "gekonnt", "gemacht", "gemocht", "gemusst", "genug", "gerade", "gern", "gesagt", "geschweige", "gewesen", "gewollt", "geworden", "gibt", "ging", "gleich", "gott", "gross", "grosse", "grossen", "grosser", "grosses", "groß", "große", "großen", "großer", "großes", "gut", "gute", "guter", "gutes", "h", "hab", "habe", "haben", "habt", "hast", "hat", "hatte", "hatten", "hattest", "hattet", "heisst", "her", "heute", "hier", "hin", "hinter", "hoch", "hätte", "hätten", "i", "ich", "ihm", "ihn", "ihnen", "ihr", "ihre", "ihrem", "ihren", "ihrer", "ihres", "im", "immer", "in", "indem", "infolgedessen", "ins", "irgend", "ist", "j", "ja", "jahr", "jahre", "jahren", "je", "jede", "jedem", "jeden", "jeder", "jedermann", "jedermanns", "jedes", "jedoch", "jemand", "jemandem", "jemanden", "jene", "jenem", "jenen", "jener", "jenes", "jetzt", "k", "kam", "kann", "kannst", "kaum", "kein", "keine", "keinem", "keinen", "keiner", "keines", "kleine", "kleinen", "kleiner", "kleines", "kommen", "kommt", "konnte", "konnten", "kurz", "können", "könnt", "könnte", "l", "lang", "lange", "leicht", "leide", "lieber", "los", "m", "machen", "macht", "machte", "mag", "magst", "mahn", "mal", "man", "manche", "manchem", "manchen", "mancher", "manches", "mann", "mehr", "mein", "meine", "meinem", "meinen", "meiner", "meines", "mensch", "menschen", "mich", "mir", "mit", "mittel", "mochte", "mochten", "morgen", "muss", "musst", "musste", "mussten", "muß", "mußt", "möchte", "mögen", "möglich", "mögt", "müssen", "müsst", "müßt", "n", "na", "nach", "nachdem", "nahm", "natürlich", "neben", "nein", "neue", "neuen", "neun", "neunte", "neunten", "neunter", "neuntes", "nicht", "nichts", "nie", "niemand", "niemandem", "niemanden", "noch", "nun", "nur", "o", "ob", "oben", "oder", "offen", "oft", "ohne", "ordnung", "p", "q", "r", "recht", "rechte", "rechten", "rechter", "rechtes", "richtig", "rund", "s", "sa", "sache", "sagt", "sagte", "sah", "satt", "schlecht", "schluss", "schon", "sechs", "sechste", "sechsten", "sechster", "sechstes", "sehr", "sei", "seid", "seien", "sein", "seine", "seinem", "seinen", "seiner", "seines", "seit", "seitdem", "selbst", "sich", "sie", "sieben", "siebente", "siebenten", "siebenter", "siebentes", "sind", "so", "solang", "solche", "solchem", "solchen", "solcher", "solches", "soll", "sollen", "sollst", "sollt", "sollte", "sollten", "sondern", "sonst", "soweit", "sowie", "später", "startseite", "statt", "steht", "suche", "t", "tag", "tage", "tagen", "tat", "teil", "tel", "tritt", "trotzdem", "tun", "u", "uhr", "um", "und", "und?", "uns", "unse", "unsem", "unsen", "unser", "unsere", "unserer", "unses", "unter", "v", "vergangenen", "viel", "viele", "vielem", "vielen", "vielleicht", "vier", "vierte", "vierten", "vierter", "viertes", "vom", "von", "vor", "w", "wahr?", "wann", "war", "waren", "warst", "wart", "warum", "was", "weg", "wegen", "weil", "weit", "weiter", "weitere", "weiteren", "weiteres", "welche", "welchem", "welchen", "welcher", "welches", "wem", "wen", "wenig", "wenige", "weniger", "weniges", "wenigstens", "wenn", "wer", "werde", "werden", "werdet", "weshalb", "wessen", "wie", "wieder", "wieso", "will", "willst", "wir", "wird", "wirklich", "wirst", "wissen", "wo", "woher", "wohin", "wohl", "wollen", "wollt", "wollte", "wollten", "worden", "wurde", "wurden", "während", "währenddem", "währenddessen", "wäre", "würde", "würden", "x", "y", "z", "z.b", "zehn", "zehnte", "zehnten", "zehnter", "zehntes", "zeit", "zu", "zuerst", "zugleich", "zum", "zunächst", "zur", "zurück", "zusammen", "zwanzig", "zwar", "zwei", "zweite", "zweiten", "zweiter", "zweites", "zwischen", "zwölf", "über", "überhaupt", "übrigens",
]

# Greek
el = [
    "αλλα", "αν", "αντι", "απο", "αυτα", "αυτεσ", "αυτη", "αυτο", "αυτοι", "αυτοσ", "αυτουσ", "αυτων", "για", "δε", "δεν", "εαν", "ειμαι", "ειμαστε", "ειναι", "εισαι", "ειστε", "εκεινα", "εκεινεσ", "εκεινη", "εκεινο", "εκεινοι", "εκεινοσ", "εκεινουσ", "εκεινων", "ενω", "επι", "η", "θα", "ισωσ", "κ", "και", "κατα", "κι", "μα", "με", "μετα", "μη", "μην", "να", "ο", "οι", "ομωσ", "οπωσ", "οσο", "οτι", "παρα", "ποια", "ποιεσ", "ποιο", "ποιοι", "ποιοσ", "ποιουσ", "ποιων", "που", "προσ", "πωσ", "σε", "στη", "στην", "στο", "στον", "τα", "την", "τησ", "το", "τον", "τοτε", "του", "των", "ωσ",
]

# English
en = [
    "about", "after", "all", "also", "am", "an", "and", "another", "any", "are", "as", "at", "be", "because", "been", "before", "being", "between", "both", "but", "by", "came", "can", "come", "could", "did", "do", "each", "for", "from", "get", "got", "has", "had", "he", "have", "her", "here", "him", "himself", "his", "how", "if", "in", "into", "is", "it", "like", "make", "many", "me", "might", "more", "most", "much", "must", "my", "never", "now", "of", "on", "only", "or", "other", "our", "out", "over", "said", "same", "should", "since", "some", "still", "such", "take", "than", "that", "the", "their", "them", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "up", "very", "was", "way", "we", "well", "were", "what", "where", "which", "while", "who", "with", "would", "you", "your", "a", "i",
]

# Spanish
es = [
    "a", "un", "el", "ella", "y", "sobre", "de", "la", "que", "en", "los", "del", "se", "las", "por", "un", "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "porque", "cuando", "muy", "sin", "sobre", "también", "me", "hasta", "donde", "quien", "desde", "nos", "durante", "uno", "ni", "contra", "ese", "eso", "mí", "qué", "otro", "él", "cual", "poco", "mi", "tú", "te", "ti", "sí",
]

# Basque
eu = [
    "al", "anitz", "arabera", "asko", "baina", "bat", "batean", "batek", "bati", "batzuei", "batzuek", "batzuetan", "batzuk", "bera", "beraiek", "berau", "berauek", "bere", "berori", "beroriek", "beste", "bezala", "da", "dago", "dira", "ditu", "du", "dute", "edo", "egin", "ere", "eta", "eurak", "ez", "gainera", "gu", "gutxi", "guzti", "haiei", "haiek", "haietan", "hainbeste", "hala", "han", "handik", "hango", "hara", "hari", "hark", "hartan", "hau", "hauei", "hauek", "hauetan", "hemen", "hemendik", "hemengo", "hi", "hona", "honek", "honela", "honetan", "honi", "hor", "hori", "horiei", "horiek", "horietan", "horko", "horra", "horrek", "horrela", "horretan", "horri", "hortik", "hura", "izan", "ni", "noiz", "nola", "non", "nondik", "nongo", "nor", "nora", "ze", "zein", "zen", "zenbait", "zenbat", "zer", "zergatik", "ziren", "zituen", "zu", "zuek", "zuen", "zuten",
]

# French
fr = [
    "être", "avoir", "faire", "a", "au", "aux", "avec", "ce", "ces", "dans", "de", "des", "du", "elle", "en", "et", "eux", "il", "je", "la", "le", "leur", "lui", "ma", "mais", "me", "même", "mes", "moi", "mon", "ne", "nos", "notre", "nous", "on", "ou", "où", "par", "pas", "pour", "qu", "que", "qui", "sa", "se", "ses", "son", "sur", "ta", "te", "tes", "toi", "ton", "tu", "un", "une", "vos", "votre", "vous", "c", "d", "j", "l", "à", "m", "n", "s", "t", "y", "été", "étée", "étées", "étés", "étant", "suis", "es", "est", "sommes", "êtes", "sont", "serai", "seras", "sera", "serons", "serez", "seront", "serais", "serait", "serions", "seriez", "seraient", "étais", "était", "étions", "étiez", "étaient", "fus", "fut", "fûmes", "fûtes", "furent", "sois", "soit", "soyons", "soyez", "soient", "fusse", "fusses", "fût", "fussions", "fussiez", "fussent", "ayant", "eu", "eue", "eues", "eus", "ai", "as", "avons", "avez", "ont", "aurai", "auras", "aura", "aurons", "aurez", "auront", "aurais", "aurait", "aurions", "auriez", "auraient", "avais", "avait", "avions", "aviez", "avaient", "eut", "eûmes", "eûtes", "eurent", "aie", "aies", "ait", "ayons", "ayez", "aient", "eusse", "eusses", "eût", "eussions", "eussiez", "eussent", "ceci", "cela", "cet", "cette", "ici", "ils", "les", "leurs", "quel", "quels", "quelle", "quelles", "sans", "soi",
]

# Italian
it = [
    "ad", "al", "allo", "ai", "agli", "all", "agl", "alla", "alle", "con", "col", "coi", "da", "dal", "dallo", "dai", "dagli", "dall", "dagl", "dalla", "dalle", "di", "del", "dello", "dei", "degli", "dell", "degl", "della", "delle", "in", "nel", "nello", "nei", "negli", "nell", "negl", "nella", "nelle", "su", "sul", "sullo", "sui", "sugli", "sull", "sugl", "sulla", "sulle", "per", "tra", "contro", "io", "tu", "lui", "lei", "noi", "voi", "loro", "mio", "mia", "miei", "mie", "tuo", "tua", "tuoi", "tue", "suo", "sua", "suoi", "sue", "nostro", "nostra", "nostri", "nostre", "vostro", "vostra", "vostri", "vostre", "mi", "ti", "ci", "vi", "lo", "la", "li", "le", "gli", "ne", "il", "un", "uno", "una", "ma", "ed", "se", "perché", "anche", "come", "dov", "dove", "che", "chi", "cui", "non", "più", "quale", "quanto", "quanti", "quanta", "quante", "quello", "quelli", "quella", "quelle", "questo", "questi", "questa", "queste", "si", "tutto", "tutti", "a", "c", "e", "i", "l", "o", "ho", "hai", "ha", "abbiamo", "avete", "hanno", "abbia", "abbiate", "abbiano", "avrò", "avrai", "avrà", "avremo", "avrete", "avranno", "avrei", "avresti", "avrebbe", "avremmo", "avreste", "avrebbero", "avevo", "avevi", "aveva", "avevamo", "avevate", "avevano", "ebbi", "avesti", "ebbe", "avemmo", "aveste", "ebbero", "avessi", "avesse", "avessimo", "avessero", "avendo", "avuto", "avuta", "avuti", "avute", "sono", "sei", "è", "siamo", "siete", "sia", "siate", "siano", "sarò", "sarai", "sarà", "saremo", "sarete", "saranno", "sarei", "saresti", "sarebbe", "saremmo", "sareste", "sarebbero", "ero", "eri", "era", "eravamo", "eravate", "erano", "fui", "fosti", "fu", "fummo", "foste", "furono", "fossi", "fosse", "fossimo", "fossero", "essendo", "faccio", "fai", "facciamo", "fanno", "faccia", "facciate", "facciano", "farò", "farai", "farà", "faremo", "farete", "faranno", "farei", "faresti", "farebbe", "faremmo", "fareste", "farebbero", "facevo", "facevi", "faceva", "facevamo", "facevate", "facevano", "feci", "facesti", "fece", "facemmo", "faceste", "fecero", "facessi", "facesse", "facessimo", "facessero", "facendo", "sto", "stai", "sta", "stiamo", "stanno", "stia", "stiate", "stiano", "starò", "starai", "starà", "staremo", "starete", "staranno", "starei", "staresti", "starebbe", "staremmo", "stareste", "starebbero", "stavo", "stavi", "stava", "stavamo", "stavate", "stavano", "stetti", "stesti", "stette", "stemmo", "steste", "stettero", "stessi", "stesse", "stessimo", "stessero", "stando",
]

# Dutch
nl = [
    "aan", "af", "al", "alles", "als", "altijd", "andere", "ben", "bij", "daar", "dan", "dat", "de", "der", "deze", "die", "dit", "doch", "doen", "door", "dus", "een", "eens", "en", "er", "ge", "geen", "geweest", "haar", "had", "heb", "hebben", "heeft", "hem", "het", "hier", "hij", "hoe", "hun", "iemand", "iets", "ik", "in", "is", "ja", "je ", "kan", "kon", "kunnen", "maar", "me", "meer", "men", "met", "mij", "mijn", "moet", "na", "naar", "niet", "niets", "nog", "nu", "of", "om", "omdat", "ons", "ook", "op", "over", "reeds", "te", "tegen", "toch", "toen", "tot", "u", "uit", "uw", "van", "veel", "voor", "want", "waren", "was", "wat", "we", "wel", "werd", "wezen", "wie", "wij", "wil", "worden", "zal", "ze", "zei", "zelf", "zich", "zij", "zijn", "zo", "zonder", "zou",
]

# Norwegian
no = [
    "og", "i", "jeg", "det", "at", "en", "et", "den", "til", "er", "som", "på", "de", "med", "han", "av", "ikke", "der", "så", "var", "meg", "seg", "men", "ett", "har", "om", "vi", "min", "mitt", "ha", "hadde", "hun", "nå", "over", "da", "ved", "fra", "du", "ut", "sin", "dem", "oss", "opp", "man", "kan", "hans", "hvor", "eller", "hva", "skal", "selv", "sjøl", "her", "alle", "vil", "bli", "ble", "blitt", "kunne", "inn", "når", "kom", "noen", "noe", "ville", "dere", "som", "deres", "kun", "ja", "etter", "ned", "skulle", "denne", "for", "deg", "si", "sine", "sitt", "mot", "å", "meget", "hvorfor", "dette", "disse", "uten", "hvordan", "ingen", "din", "ditt", "blir", "samme", "hvilken", "hvilke", "sånn", "inni", "mellom", "vår", "hver", "hvem", "vors", "hvis", "både", "bare", "enn", "fordi", "før", "mange", "også", "slik", "vært", "være", "begge", "siden", "henne", "hennar", "hennes",
]

# Portuguese
pt = [
    "a", "à", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "às", "até", "com", "como", "da", "das", "de", "dela", "delas", "dele", "deles", "depois", "do", "dos", "e", "ela", "elas", "ele", "eles", "em", "entre", "essa", "essas", "esse", "esses", "esta", "estas", "este", "estes", "eu", "isso", "isto", "já", "lhe", "lhes", "mais", "mas", "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "muitos", "na", "não", "nas", "nem", "no", "nos", "nós", "nossa", "nossas", "nosso", "nossos", "num", "nuns", "numa", "numas", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "quais", "qual", "quando", "que", "quem", "se", "sem", "seu", "seus", "só", "sua", "suas", "também", "te", "teu", "teus", "tu", "tua", "tuas", "um", "uma", "umas", "você", "vocês", "vos", "vosso", "vossos",
]

# Swedish
sw = [
    "jag", "det", "är", "du", "inte", "att", "en", "och", "har", "vi", "på", "i", "för", "han", "vad", "med", "mig", "som", "här", "om", "dig", "var", "den", "så", "till", "kan", "de", "ni", "ska", "ett", "men", "av", "vill", "nu", "ja", "nej", "bara", "hon", "hur", "min", "där", "honom", "kom", "din", "då", "när", "ha", "er", "ta", "ut", "får", "man", "vara", "oss", "dem", "eller", "varför", "alla", "från", "upp", "igen", "sa", "hade", "allt", "in", "sig", "ingen", "henne", "vem", "mitt", "nåt", "blir", "än", "bli", "ju", "två", "tar", "hans", "ditt", "mina", "åt", "väl", "också", "nån", "låt", "detta", "va", "dina", "dom", "blev", "inga", "sin", "just", "många", "vart", "vilken", "ur", "ens", "sitt", "e", "jo", "era", "deras", "fem", "sex", "denna", "vilket", "fyra", "vårt", "emot", "tio", "ert", "sju", "åtta", "nånting", "ned", "ers", "nio", "mej",
]
