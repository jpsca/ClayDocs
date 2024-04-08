"""
Translated from lunr-languages
"""
from lunr.stop_word_filter import generate_stop_word_filter

from .stemmer import Among, Snowball, generate_trimmer


__all__ = ("trimmer", "stop_words_filter", "stemmer")

LANG = "es"
WORD_CHARACTERS = "A-Za-z\xAA\xBA\xC0-\xD6\xD8-\xF6\xF8-\u02B8\u02E0-\u02E4\u1D00-\u1D25\u1D2C-\u1D5C\u1D62-\u1D65\u1D6B-\u1D77\u1D79-\u1DBE\u1E00-\u1EFF\u2071\u207F\u2090-\u209C\u212A\u212B\u2132\u214E\u2160-\u2188\u2C60-\u2C7F\uA722-\uA787\uA78B-\uA7AD\uA7B0-\uA7B7\uA7F7-\uA7FF\uAB30-\uAB5A\uAB5C-\uAB64\uFB00-\uFB06\uFF21-\uFF3A\uFF41-\uFF5A"
STOP_WORDS = "a al algo algunas algunos ante antes como con contra cual cuando de del desde donde durante e el ella ellas ellos en entre era erais eran eras eres es esa esas ese eso esos esta estaba estabais estaban estabas estad estada estadas estado estados estamos estando estar estaremos estará estarán estarás estaré estaréis estaría estaríais estaríamos estarían estarías estas este estemos esto estos estoy estuve estuviera estuvierais estuvieran estuvieras estuvieron estuviese estuvieseis estuviesen estuvieses estuvimos estuviste estuvisteis estuviéramos estuviésemos estuvo está estábamos estáis están estás esté estéis estén estés fue fuera fuerais fueran fueras fueron fuese fueseis fuesen fueses fui fuimos fuiste fuisteis fuéramos fuésemos ha habida habidas habido habidos habiendo habremos habrá habrán habrás habré habréis habría habríais habríamos habrían habrías habéis había habíais habíamos habían habías han has hasta hay haya hayamos hayan hayas hayáis he hemos hube hubiera hubierais hubieran hubieras hubieron hubiese hubieseis hubiesen hubieses hubimos hubiste hubisteis hubiéramos hubiésemos hubo la las le les lo los me mi mis mucho muchos muy más mí mía mías mío míos nada ni no nos nosotras nosotros nuestra nuestras nuestro nuestros o os otra otras otro otros para pero poco por porque que quien quienes qué se sea seamos sean seas seremos será serán serás seré seréis sería seríais seríamos serían serías seáis sido siendo sin sobre sois somos son soy su sus suya suyas suyo suyos sí también tanto te tendremos tendrá tendrán tendrás tendré tendréis tendría tendríais tendríamos tendrían tendrías tened tenemos tenga tengamos tengan tengas tengo tengáis tenida tenidas tenido tenidos teniendo tenéis tenía teníais teníamos tenían tenías ti tiene tienen tienes todo todos tu tus tuve tuviera tuvierais tuvieran tuvieras tuvieron tuviese tuvieseis tuviesen tuvieses tuvimos tuviste tuvisteis tuviéramos tuviésemos tuvo tuya tuyas tuyo tuyos tú un una uno unos vosotras vosotros vuestra vuestras vuestro vuestros y ya yo él éramos".split(
    " "
)

a_0 = [
    Among("", -1, 6),
    Among("á", 0, 1),
    Among("é", 0, 2),
    Among("í", 0, 3),
    Among("ó", 0, 4),
    Among("ú", 0, 5),
]
a_1 = [
    Among("la", -1, -1),
    Among("sela", 0, -1),
    Among("le", -1, -1),
    Among("me", -1, -1),
    Among("se", -1, -1),
    Among("lo", -1, -1),
    Among("selo", 5, -1),
    Among("las", -1, -1),
    Among("selas", 7, -1),
    Among("les", -1, -1),
    Among("los", -1, -1),
    Among("selos", 10, -1),
    Among("nos", -1, -1),
]
a_2 = [
    Among("ando", -1, 6),
    Among("iendo", -1, 6),
    Among("yendo", -1, 7),
    Among("ándo", -1, 2),
    Among("iéndo", -1, 1),
    Among("ar", -1, 6),
    Among("er", -1, 6),
    Among("ir", -1, 6),
    Among("ár", -1, 3),
    Among("ér", -1, 4),
    Among("ír", -1, 5),
]
a_3 = [
    Among("ic", -1, -1),
    Among("ad", -1, -1),
    Among("os", -1, -1),
    Among("iv", -1, 1),
]
a_4 = [Among("able", -1, 1), Among("ible", -1, 1), Among("ante", -1, 1)]
a_5 = [
    Among("ic", -1, 1),
    Among("abil", -1, 1),
    Among("iv", -1, 1),
]
a_6 = [
    Among("ica", -1, 1),
    Among("ancia", -1, 2),
    Among("encia", -1, 5),
    Among("adora", -1, 2),
    Among("osa", -1, 1),
    Among("ista", -1, 1),
    Among("iva", -1, 9),
    Among("anza", -1, 1),
    Among("logía", -1, 3),
    Among("idad", -1, 8),
    Among("able", -1, 1),
    Among("ible", -1, 1),
    Among("ante", -1, 2),
    Among("mente", -1, 7),
    Among("amente", 13, 6),
    Among("ación", -1, 2),
    Among("ución", -1, 4),
    Among("ico", -1, 1),
    Among("ismo", -1, 1),
    Among("oso", -1, 1),
    Among("amiento", -1, 1),
    Among("imiento", -1, 1),
    Among("ivo", -1, 9),
    Among("ador", -1, 2),
    Among("icas", -1, 1),
    Among("ancias", -1, 2),
    Among("encias", -1, 5),
    Among("adoras", -1, 2),
    Among("osas", -1, 1),
    Among("istas", -1, 1),
    Among("ivas", -1, 9),
    Among("anzas", -1, 1),
    Among("logías", -1, 3),
    Among("idades", -1, 8),
    Among("ables", -1, 1),
    Among("ibles", -1, 1),
    Among("aciones", -1, 2),
    Among("uciones", -1, 4),
    Among("adores", -1, 2),
    Among("antes", -1, 2),
    Among("icos", -1, 1),
    Among("ismos", -1, 1),
    Among("osos", -1, 1),
    Among("amientos", -1, 1),
    Among("imientos", -1, 1),
    Among("ivos", -1, 9),
]
a_7 = [
    Among("ya", -1, 1),
    Among("ye", -1, 1),
    Among("yan", -1, 1),
    Among("yen", -1, 1),
    Among("yeron", -1, 1),
    Among("yendo", -1, 1),
    Among("yo", -1, 1),
    Among("yas", -1, 1),
    Among("yes", -1, 1),
    Among("yais", -1, 1),
    Among("yamos", -1, 1),
    Among("yó", -1, 1),
]
a_8 = [
    Among("aba", -1, 2),
    Among("ada", -1, 2),
    Among("ida", -1, 2),
    Among("ara", -1, 2),
    Among("iera", -1, 2),
    Among("ía", -1, 2),
    Among("aría", 5, 2),
    Among("ería", 5, 2),
    Among("iría", 5, 2),
    Among("ad", -1, 2),
    Among("ed", -1, 2),
    Among("id", -1, 2),
    Among("ase", -1, 2),
    Among("iese", -1, 2),
    Among("aste", -1, 2),
    Among("iste", -1, 2),
    Among("an", -1, 2),
    Among("aban", 16, 2),
    Among("aran", 16, 2),
    Among("ieran", 16, 2),
    Among("ían", 16, 2),
    Among("arían", 20, 2),
    Among("erían", 20, 2),
    Among("irían", 20, 2),
    Among("en", -1, 1),
    Among("asen", 24, 2),
    Among("iesen", 24, 2),
    Among("aron", -1, 2),
    Among("ieron", -1, 2),
    Among("arán", -1, 2),
    Among("erán", -1, 2),
    Among("irán", -1, 2),
    Among("ado", -1, 2),
    Among("ido", -1, 2),
    Among("ando", -1, 2),
    Among("iendo", -1, 2),
    Among("ar", -1, 2),
    Among("er", -1, 2),
    Among("ir", -1, 2),
    Among("as", -1, 2),
    Among("abas", 39, 2),
    Among("adas", 39, 2),
    Among("idas", 39, 2),
    Among("aras", 39, 2),
    Among("ieras", 39, 2),
    Among("ías", 39, 2),
    Among("arías", 45, 2),
    Among("erías", 45, 2),
    Among("irías", 45, 2),
    Among("es", -1, 1),
    Among("ases", 49, 2),
    Among("ieses", 49, 2),
    Among("abais", -1, 2),
    Among("arais", -1, 2),
    Among("ierais", -1, 2),
    Among("íais", -1, 2),
    Among("aríais", 55, 2),
    Among("eríais", 55, 2),
    Among("iríais", 55, 2),
    Among("aseis", -1, 2),
    Among("ieseis", -1, 2),
    Among("asteis", -1, 2),
    Among("isteis", -1, 2),
    Among("áis", -1, 2),
    Among("éis", -1, 1),
    Among("aréis", 64, 2),
    Among("eréis", 64, 2),
    Among("iréis", 64, 2),
    Among("ados", -1, 2),
    Among("idos", -1, 2),
    Among("amos", -1, 2),
    Among("ábamos", 70, 2),
    Among("áramos", 70, 2),
    Among("iéramos", 70, 2),
    Among("íamos", 70, 2),
    Among("aríamos", 74, 2),
    Among("eríamos", 74, 2),
    Among("iríamos", 74, 2),
    Among("emos", -1, 1),
    Among("aremos", 78, 2),
    Among("eremos", 78, 2),
    Among("iremos", 78, 2),
    Among("ásemos", 78, 2),
    Among("iésemos", 78, 2),
    Among("imos", -1, 2),
    Among("arás", -1, 2),
    Among("erás", -1, 2),
    Among("irás", -1, 2),
    Among("ís", -1, 2),
    Among("ará", -1, 2),
    Among("erá", -1, 2),
    Among("irá", -1, 2),
    Among("aré", -1, 2),
    Among("eré", -1, 2),
    Among("iré", -1, 2),
    Among("ió", -1, 2),
]
a_9 = [
    Among("a", -1, 1),
    Among("e", -1, 2),
    Among("o", -1, 1),
    Among("os", -1, 1),
    Among("á", -1, 1),
    Among("é", -1, 2),
    Among("í", -1, 1),
    Among("ó", -1, 1),
]
g_v = [
    17,
    65,
    16,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    17,
    4,
    10,
]

ORD_A = ord("a")
ORD_UD = ord("ü")


class Stemmer:
    I_p2: int
    I_p1: int
    I_pV: int

    def __init__(self):
        self.sbp = Snowball()

    def __call__(self, token, *args, **kw):
        self.set_current(token)
        self.stem()
        return self.get_current()

    def stem(self):
        v_1 = self.sbp.cursor
        self.r_mark_regions()
        self.sbp.limit_backward = v_1
        self.sbp.cursor = self.sbp.limit
        self.r_attached_pronoun()
        self.sbp.cursor = self.sbp.limit

        if not self.r_standard_suffix():
            self.sbp.cursor = self.sbp.limit
            if not self.r_y_verb_suffix():
                self.sbp.cursor = self.sbp.limit
                self.r_verb_suffix()

        self.sbp.cursor = self.sbp.limit
        self.r_residual_suffix()
        self.sbp.cursor = self.sbp.limit_backward
        self.r_postlude()

    def set_current(self, word):
        self.sbp.set_current(word)

    def get_current(self):
        return self.sbp.get_current()

    def habr1(self):
        if self.sbp.out_grouping(g_v, ORD_A, ORD_UD):
            while not self.sbp.in_grouping(g_v, ORD_A, ORD_UD):
                if self.sbp.cursor >= self.sbp.limit:
                    return True
                self.sbp.cursor += 1
            return False
        return True

    def habr2(self):
        if self.sbp.in_grouping(g_v, ORD_A, ORD_UD):
            v_1 = self.sbp.cursor
            if self.habr1():
                self.sbp.cursor = v_1
                if not self.sbp.in_grouping(g_v, ORD_A, ORD_UD):
                    return True
                while not self.sbp.out_grouping(g_v, ORD_A, ORD_UD):
                    if self.sbp.cursor >= self.sbp.limit:
                        return True
                    self.sbp.cursor += 1
            return False
        return True

    def habr3(self):
        v_1 = self.sbp.cursor
        if self.habr2():
            self.sbp.cursor = v_1
            if not self.sbp.out_grouping(g_v, ORD_A, ORD_UD):
                return
            v_2 = self.sbp.cursor
            if self.habr1():
                self.sbp.cursor = v_2
                if (
                    not self.sbp.in_grouping(g_v, ORD_A, ORD_UD)
                    or self.sbp.cursor >= self.sbp.limit
                ):
                    return
                self.sbp.cursor += 1
        self.I_pV
        self.I_pV = self.sbp.cursor

    def habr4(self):
        while not self.sbp.in_grouping(g_v, ORD_A, ORD_UD):
            if self.sbp.cursor >= self.sbp.limit:
                return False
            self.sbp.cursor += 1
        while not self.sbp.out_grouping(g_v, ORD_A, ORD_UD):
            if self.sbp.cursor >= self.sbp.limit:
                return False
            self.sbp.cursor += 1
        return True

    def r_mark_regions(self):
        v_1 = self.sbp.cursor
        self.I_pV = self.sbp.limit
        self.I_p1 = self.I_pV
        self.I_p2 = self.I_pV
        self.habr3()
        self.sbp.cursor = v_1
        if self.habr4():
            self.I_p1 = self.sbp.cursor
            if self.habr4():
                self.I_p2 = self.sbp.cursor

    def r_postlude(self):
        while True:
            self.sbp.bra = self.sbp.cursor
            among_var = self.sbp.find_among(a_0, v_size=6)
            if among_var:
                self.sbp.ket = self.sbp.cursor
                if among_var == 1:
                    self.sbp.slice_from("a")
                    continue
                elif among_var == 2:
                    self.sbp.slice_from("e")
                    continue
                elif among_var == 3:
                    self.sbp.slice_from("i")
                    continue
                elif among_var == 4:
                    self.sbp.slice_from("o")
                    continue
                elif among_var == 5:
                    self.sbp.slice_from("u")
                    continue
                elif among_var == 6 and self.sbp.cursor < self.sbp.limit:
                    self.sbp.cursor += 1
                    continue
            break

    def r_RV(self):
        return self.I_pV <= self.sbp.cursor

    def r_R1(self):
        return self.I_p1 <= self.sbp.cursor

    def r_R2(self):
        return self.I_p2 <= self.sbp.cursor

    def r_attached_pronoun(self):
        self.sbp.ket = self.sbp.cursor
        if self.sbp.find_among_b(a_1, v_size=13):
            self.sbp.bra = self.sbp.cursor
            among_var = self.sbp.find_among_b(a_2, v_size=11)
            if among_var and self.r_RV():
                actions = {
                    1: lambda: self.sbp.slice_from("iendo"),
                    2: lambda: self.sbp.slice_from("ando"),
                    3: lambda: self.sbp.slice_from("ar"),
                    4: lambda: self.sbp.slice_from("er"),
                    5: lambda: self.sbp.slice_from("ir"),
                    6: lambda: self.sbp.slice_del(),
                    7: lambda: self.sbp.slice_del()
                    if self.sbp.eq_s_b(1, "u")
                    else None,
                }
                if among_var in actions:
                    actions[among_var]()

    def habr5(self, a, n):
        if not self.r_R2():
            return True
        self.sbp.slice_del()
        self.sbp.ket = self.sbp.cursor
        among_var = self.sbp.find_among_b(a, n)
        if among_var == 1 and self.r_R2():
            self.sbp.bra = self.sbp.cursor
            self.sbp.slice_del()
        return False

    def habr6(self, c1):
        if not self.r_R2():
            return True
        self.sbp.slice_del()
        self.sbp.ket = self.sbp.cursor
        if self.sbp.eq_s_b(2, c1) and self.r_R2():
            self.sbp.bra = self.sbp.cursor
            self.sbp.slice_del()
        return False

    def r_standard_suffix(self):
        self.sbp.ket = self.sbp.cursor
        among_var = self.sbp.find_among_b(a_6, v_size=46)
        if among_var:
            self.sbp.bra = self.sbp.cursor
            if among_var == 1:
                if not self.r_R2():
                    return False
                self.sbp.slice_del()
            elif among_var == 2:
                if self.habr6("ic"):
                    return False
            elif among_var == 3:
                if not self.r_R2():
                    return False
                self.sbp.slice_from("log")
            elif among_var == 4:
                if not self.r_R2():
                    return False
                self.sbp.slice_from("u")
            elif among_var == 5:
                if not self.r_R2():
                    return False
                self.sbp.slice_from("ente")
            elif among_var == 6:
                if not self.r_R1():
                    return False
                self.sbp.slice_del()
                self.sbp.ket = self.sbp.cursor
                among_var = self.sbp.find_among_b(a_3, v_size=4)
                if among_var:
                    self.sbp.bra = self.sbp.cursor
                    if self.r_R2():
                        self.sbp.slice_del()
                        if among_var == 1:
                            self.sbp.ket = self.sbp.cursor
                            if self.sbp.eq_s_b(2, "at"):
                                self.sbp.bra = self.sbp.cursor
                                if self.r_R2():
                                    self.sbp.slice_del()
            elif among_var == 7:
                if self.habr5(a_4, 3):
                    return False
            elif among_var == 8:
                if self.habr5(a_5, 3):
                    return False
            elif among_var == 9:
                if self.habr6("at"):
                    return False
            return True
        return False

    def r_y_verb_suffix(self):
        if self.sbp.cursor >= self.I_pV:
            v_1 = self.sbp.limit_backward
            self.sbp.limit_backward = self.I_pV
            self.sbp.ket = self.sbp.cursor
            among_var = self.sbp.find_among_b(a_7, v_size=12)
            self.sbp.limit_backward = v_1
            if among_var:
                self.sbp.bra = self.sbp.cursor
                if among_var == 1:
                    if not self.sbp.eq_s_b(1, "u"):
                        return False
                    self.sbp.slice_del()
                return True
        return False

    def r_verb_suffix(self):
        if self.sbp.cursor >= self.I_pV:
            self.sbp.ket = self.sbp.cursor
            among_var = self.sbp.find_among_b(a_8, v_size=96)

            if among_var:
                self.sbp.bra = self.sbp.cursor
                if among_var == 1:
                    v_2 = self.sbp.limit - self.sbp.cursor
                    if self.sbp.eq_s_b(1, "u"):
                        v_3 = self.sbp.limit - self.sbp.cursor
                        if self.sbp.eq_s_b(1, "g"):
                            self.sbp.cursor = self.sbp.limit - v_3
                        else:
                            self.sbp.cursor = self.sbp.limit - v_2
                    else:
                        self.sbp.cursor = self.sbp.limit - v_2
                    self.sbp.bra = self.sbp.cursor
                if among_var == 2:
                    self.sbp.slice_del()

    def r_residual_suffix(self):
        among_var = self.sbp.find_among_b(a_9, 8)
        if among_var:
            self.sbp.bra = self.sbp.cursor
            if among_var == 1 and self.r_RV():
                self.sbp.slice_del()
            elif among_var == 2 and self.r_RV():
                self.sbp.slice_del()
                self.sbp.ket = self.sbp.cursor
                if self.sbp.eq_s_b(1, "u"):
                    self.sbp.bra = self.sbp.cursor
                    v_1 = self.sbp.limit - self.sbp.cursor
                    if self.sbp.eq_s_b(1, "g") and self.r_RV():
                        self.sbp.cursor = self.sbp.limit - v_1
                        self.sbp.slice_del()


trimmer = generate_trimmer(WORD_CHARACTERS)
stop_words_filter = generate_stop_word_filter(STOP_WORDS, LANG)
stemmer = Stemmer()
