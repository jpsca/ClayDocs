import re


def generate_trimmer(word_characters):
    start_regex = re.compile(f"^[^{word_characters}]+")
    end_regex = re.compile(f"[^{word_characters}]+$")

    def trimmer(token):
        return end_regex.sub("", start_regex.sub("", token))

    return trimmer


class Among:
    __slots__ = ("s_size", "s", "substring_i", "result", "method")

    s_size: int
    s: list[int]
    substring_i: int
    result: int
    method: int | None

    def __init__(
        self,
        s: str,
        substring_i: int,
        result: int,
        method: int | None = None,
    ):
        self.s_size = len(s)
        self.s = [ord(c) for c in s]
        self.substring_i = substring_i
        self.result = result
        self.method = method


class Snowball:
    __slots__ = ("bra", "ket", "limit", "cursor", "limit_backward", "current")

    bra: int = 0
    ket: int = 0
    limit: int = 0
    cursor: int = 0
    limit_backward: int = 0
    current: str = ""

    def set_current(self, word):
        self.current = word
        self.cursor = 0
        self.limit = len(word)
        self.limit_backward = 0
        self.bra = self.cursor
        self.ket = self.limit

    def get_current(self):
        result = self.current
        self.current = ""
        return result

    def in_grouping(self, s, min, max):
        if self.cursor < self.limit:
            ch = ord(self.current[self.cursor])
            if min <= ch <= max:
                ch -= min
                if s[ch >> 3] & (0x1 << (ch & 0x7)):
                    self.cursor += 1
                    return True
        return False

    def in_grouping_b(self, s, min, max):
        if self.cursor > self.limit_backward:
            ch = ord(self.current[self.cursor - 1])
            if min <= ch <= max:
                ch -= min
                if s[ch >> 3] & (0x1 << (ch & 0x7)):
                    self.cursor -= 1
                    return True
        return False

    def out_grouping(self, s, min, max):
        if self.cursor < self.limit:
            ch = ord(self.current[self.cursor])
            if ch < min or ch > max:
                self.cursor += 1
                return True
            ch -= min
            if not s[ch >> 3] & (0x1 << (ch & 0x7)):
                self.cursor += 1
                return True
        return False

    def out_grouping_b(self, s, min, max):
        if self.cursor > self.limit_backward:
            ch = ord(self.current[self.cursor - 1])
            if ch > max or ch < min:
                self.cursor -= 1
                return True
            ch -= min
            if not (s[ch >> 3] & (0x1 << (ch & 0x7))):
                self.cursor -= 1
                return True
        return False

    def eq_s(self, s_size, s):
        if self.limit - self.cursor < s_size:
            return False
        if self.current[self.cursor : self.cursor + s_size] != s:
            return False
        self.cursor += s_size
        return True

    def eq_s_b(self, s_size, s):
        if self.cursor - self.limit_backward < s_size:
            return False
        if self.current[self.cursor - s_size : self.cursor] != s:
            return False
        self.cursor -= s_size
        return True

    def find_among(self, v, v_size):
        i, j = 0, v_size
        cursor, limit = self.cursor, self.limit
        common_i = common_j = 0
        first_key_inspected = False

        while True:
            k = i + ((j - i) >> 1)
            diff = 0
            common = min(common_i, common_j)
            w = v[k]
            for i2 in range(common, w["s_size"]):
                if cursor + common == limit:
                    diff = -1
                    break
                diff = ord(self.current[cursor + common]) - w["s"][i2]
                if diff != 0:
                    break
                common += 1
            if diff < 0:
                j = k
                common_j = common
            else:
                i = k
                common_i = common
            if j - i <= 1:
                if i > 0 or j == i or first_key_inspected:
                    break
                first_key_inspected = True

        while True:
            w = v[i]
            if common_i >= w["s_size"]:
                self.cursor = cursor + w["s_size"]
                if not w.get("method"):
                    return w["result"]
                res = w["method"](self)
                self.cursor = cursor + w["s_size"]
                if res:
                    return w["result"]
            i = w["substring_i"]
            if i < 0:
                return 0

    def find_among_b(self, v, v_size):
        i, j = 0, v_size
        cursor, limit_backward = self.cursor, self.limit_backward
        common_i = common_j = 0
        first_key_inspected = False

        while True:
            k = i + ((j - i) >> 1)
            diff = 0
            common = min(common_i, common_j)
            w = v[k]
            for i2 in range(w["s_size"] - 1 - common, -1, -1):
                if cursor - 1 - common == limit_backward:
                    diff = -1
                    break
                diff = ord(self.current[cursor - 1 - common]) - w["s"][i2]
                if diff != 0:
                    break
                common += 1
            if diff < 0:
                j = k
                common_j = common
            else:
                i = k
                common_i = common
            if j - i <= 1:
                if i > 0 or j == i or first_key_inspected:
                    break
                first_key_inspected = True

        while True:
            w = v[i]
            if common_i >= w["s_size"]:
                self.cursor = cursor - w["s_size"]
                if not w.get("method"):
                    return w["result"]
                res = w["method"](self)
                self.cursor = cursor - w["s_size"]
                if res:
                    return w["result"]
            i = w["substring_i"]
            if i < 0:
                return 0

    def replace_s(self, c_bra, c_ket, s):
        adjustment = len(s) - (c_ket - c_bra)
        self.current = self.current[:c_bra] + s + self.current[c_ket:]
        self.limit += adjustment
        if self.cursor >= c_ket:
            self.cursor += adjustment
        elif self.cursor > c_bra:
            self.cursor = c_bra
        return adjustment

    def slice_check(self):
        if not (0 <= self.bra <= self.ket <= self.limit <= len(self.current)):
            raise Exception("faulty slice operation")

    def slice_from(self, s):
        self.slice_check()
        self.replace_s(self.bra, self.ket, s)

    def slice_del(self):
        self.slice_from("")

    def insert(self, c_bra, c_ket, s):
        adjustment = self.replace_s(c_bra, c_ket, s)
        if c_bra <= self.bra:
            self.bra += adjustment
        if c_bra <= self.ket:
            self.ket += adjustment

    def slice_to(self):
        self.slice_check()
        return self.current[self.bra : self.ket]

    def eq_v_b(self, s):
        return self.eq_s_b(len(s), s)
