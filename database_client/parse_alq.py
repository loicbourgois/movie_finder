from .utils import logging

def find_next(words, word_to_find):
    for i, word in enumerate(words):
        if word == word_to_find:
            return i


def parse_alq(text):
    text = "\n".join( [l for l in text.split("\n") if (l.strip() + " " )[0] != "#" ] ) 
    word = ""
    words = []
    keep_spaces = False
    for c in text:
        skips = ["'", " ", "\n"]
        if c == "'" and word == "":
            keep_spaces = True
        elif c == "'":
            keep_spaces = False
        if keep_spaces:
            skips = ["'"]
        if c not in skips:
            word += c
        if c in skips and word != "":
            words.append(word)
            word = ""
    if len(word) > 0:
        words.append(word)
    mode = ""
    alq = {
        'select': {},
        'select_keys': [],
        'where': [],
        'limit': None,
    }
    i = -1
    while i < len(words)-1:
        i+=1
        word = words[i]
        if word == "select":
            mode = "select"
        elif word == "where":
            mode = "where"
        elif word == "limit":
            mode = "limit"
        else:
            if mode == "limit":
                alq['limit'] = word
            if mode == 'where':
                alq['where'].append({
                    'field': words[i], 
                    'comparator': words[i+1], 
                    'value': words[i+2],
                })
                i+=2
            if mode == 'select':
                if words[i+1:i+3] == ['as', '(']:
                    i2 = find_next(words[i:], ")")
                    sub_words = words[i+3:i+i2]
                    alq['select'][word] = {
                        'kinds': { x:"" for x in sub_words if x != 'or' }
                    }
                    i += i2
                else:
                    splt = word.split(".")
                    alq['select'][word.replace(".", "_")] = {
                        'item': splt[-2],
                        'item_full': "_".join(splt[0:-1]),
                        'field': splt[-1],
                    }
                    if len(splt) > 2:
                        alq['select'][word.replace(".", "_")]['parent_item'] = splt[-3]
    import functools
    def compare(a, b):
        if a.startswith(b):
            return 1
        else:
            return -1
    alq['select_keys'] = sorted(list(alq['select'].keys()), key=functools.cmp_to_key(compare))
    return alq
