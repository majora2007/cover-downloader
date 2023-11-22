import re

Number = "\d+(\.\d)?"
NumberRange = Number + "(-" + Number + ")?"

MangaVolumeRegex = [
    # Dance in the Vampire Bund v16-17
    re.compile(r'(?P<Series>.*)(\b|_)v(?P<Volume>\d+-?\d+)( |_)', re.IGNORECASE),
    # NEEDLESS_Vol.4_-Simeon_6_v2[SugoiSugoi].rar
    re.compile(r'(?P<Series>.*)(\b|_)(?!\[)(vol\.?)(?P<Volume>\d+(-\d+)?)', re.IGNORECASE),
    # Historys Strongest Disciple Kenichi_v11_c90-98.zip or Dance in the Vampire Bund v16-17
    re.compile(r'(?P<Series>.*)(\b|_)(?!\[)v(?P<Volume>' + NumberRange + r')(?!\])', re.IGNORECASE),
    # Kodomo no Jikan vol. 10, [dmntsf.net] One Piece - Digital Colored Comics Vol. 20.5-21.5 Ch. 177
    re.compile(r'(?P<Series>.*)(\b|_)(vol\.? ?)(?P<Volume>\d+(\.\d)?(-\d+(\.\d)?)?)', re.IGNORECASE),
    # Killing Bites Vol. 0001 Ch. 0001 - Galactica Scanlations (gb)
    re.compile(r'(vol\.? ?)(?P<Volume>\d+(\.\d)?)', re.IGNORECASE),
    # Tonikaku Cawaii [Volume 11].cbz
    re.compile(r'(volume )(?P<Volume>\d+(\.\d)?)', re.IGNORECASE),
    # Tower Of God S01 014 (CBT) (digital).cbz
    re.compile(r'(?P<Series>.*)(\b|_|)(S(?P<Volume>\d+))', re.IGNORECASE),
    # vol_001-1.cbz for MangaPy default naming convention
    re.compile(r'(vol_)(?P<Volume>\d+(\.\d)?)', re.IGNORECASE),
    # Chinese Volume: 第n卷 -> Volume n, 第n册 -> Volume n, 幽游白书完全版 第03卷 天下 or 阿衰online 第1册
    re.compile(r'第(?P<Volume>\d+)(卷|册)', re.IGNORECASE),
    # Chinese Volume: 卷n -> Volume n, 册n -> Volume n
    re.compile(r'(卷|册)(?P<Volume>\d+)', re.IGNORECASE),
    # Korean Volume: 제n화|권|회|장 -> Volume n, n화|권|회|장 -> Volume n, 63권#200.zip -> Volume 63 (no chapter, #200 is just files inside)
    re.compile(r'제?(?P<Volume>\d+(\.\d)?)(권|회|화|장)', re.IGNORECASE),
    # Korean Season: 시즌n -> Season n,
    re.compile(r'시즌(?P<Volume>\d+\-?\d+)', re.IGNORECASE),
    # Korean Season: 시즌n -> Season n, n시즌 -> season n
    re.compile(r'(?P<Volume>\d+(\-|~)?\d+?)시즌', re.IGNORECASE),
    # Korean Season: 시즌n -> Season n, n시즌 -> season n
    re.compile(r'시즌(?P<Volume>\d+(\-|~)?\d+?)', re.IGNORECASE),
    # Japanese Volume: n巻 -> Volume n
    re.compile(r'(?P<Volume>\d+(\-)?\d?)巻', re.IGNORECASE),
    # Russian Volume: Том n -> Volume n, Тома n -> Volume
    re.compile(r'Том(а?)(\.?)(\s|_)?(?P<Volume>\d+(\-)?\d?)', re.IGNORECASE),
    # Russian Volume: n Том -> Volume n
    re.compile(r'(\s|_)?(?P<Volume>\d+(\-)?\d?)(\s|_)Том(а?)', re.IGNORECASE),
]


def parse_volume(filename):
    for regex in MangaVolumeRegex:
        matches = regex.finditer(filename)
        for match in matches:
            group = match.groupdict()
            if not group["Volume"] or group["Volume"] == "":
                continue
            value = group["Volume"]
            has_part = "Part" in group and group["Part"]
            return format_value(value, has_part)

    return None


def format_value(value, has_part):
    def remove_leading_zeroes(title):
        ret = title.lstrip('0')
        return '0' if ret == '' else ret

    def add_chapter_part(value):
        if '.' in value:
            return value

        return f"{value}.5"

    if '-' not in value:
        return remove_leading_zeroes(add_chapter_part(value) if has_part else value)

    tokens = value.split("-")
    from_value = remove_leading_zeroes(tokens[0])

    if len(tokens) != 2:
        return from_value

    to_value = remove_leading_zeroes(add_chapter_part(tokens[1]) if has_part else tokens[1])
    return f"{from_value}-{to_value}"
