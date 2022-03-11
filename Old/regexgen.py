# coding: utf-8
import re,json
import logging

wordlist = ['nigg', 'faggot']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('regex-gen.log', mode='w')
formatter = logging.Formatter('''%(asctime)s -
                              %(name)s - %(levelname)s - %(message)s''')

try:
    MANGLED_LETTERS = {
	"a": r'([aA])',
        "b": r'([bB])',
        "c": r'([cC])',
        "d": r'([dD])',
        "e": r'([eE])',
        "f": r'([fF])',
        "g": r'([gG₲ğｇģƃĝ6ƃ96]|TriHard|DrinkPurple|LUL|HYPERBRUH)',
        "h": r'([hH])',
        "i": r'([7ɪ1ｉiᴉįιl『』!îí\\/]|HYPERBRUH)',
        "j": r'([jJ])',
        "k": r'([kK])',
        "l": r'([lL])',
        "m": r'([mM])',
        "n": r'([nNИɴnℕИＮuᴎη₦ñm])',
        "o": r'([oO])',
        "p": r'([pP])',
        "q": r'([qQ])',
        "r": r'([rRЯｒ])',
        "s": r'([sS])',
        "t": r'([tT])',
        "u": r'([uU])',
        "v": r'([vV])',
        "w": r'([wW])',
        "x": r'([xX])',
        "y": r'([yY])',
        "z": r'([zZ])'
    }
    def get_regexes(word_list):
        word_regexes = {}
        for word in word_list:
            word_regexes[word] = gen_regex(word)
        return word_regexes

    def gen_regex(word):
        out_r = r'(?i)'
        interletter_pattern = r'[\W_\s]?'
        for letter in word:
            out_r += interletter_pattern + mangle(letter) + '+'
        r = re.compile(out_r)
        return r

    def mangle(letter):
        if letter in MANGLED_LETTERS.keys():
            return MANGLED_LETTERS[letter]
        else:
            return letter

    regexdic = get_regexes(wordlist)
except:
    logger.exception('exception: ')
