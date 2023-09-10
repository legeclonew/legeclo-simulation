import os
import sys
import shutil
import requests
import json
import errno
import threading
import string

############################################################################
# COMMON FUNCTIONS
############################################################################
def rmpath(path):
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
        
        
def isprintable(text):
    printset = set(string.printable)
    return set(text).issubset(printset)
    
    
def raw_unicode_escape(text):
    text = unicode(text)
    # remove the windows gremlins O^1
    cp1252 = {
        # from http://www.microsoft.com/typography/unicode/1252.htm
        u"\u20AC": u"\x80", # EURO SIGN
        u"\u201A": u"\x82", # SINGLE LOW-9 QUOTATION MARK
        u"\u0192": u"\x83", # LATIN SMALL LETTER F WITH HOOK
        u"\u201E": u"\x84", # DOUBLE LOW-9 QUOTATION MARK
        u"\u2026": u"\x85", # HORIZONTAL ELLIPSIS
        u"\u2020": u"\x86", # DAGGER
        u"\u2021": u"\x87", # DOUBLE DAGGER
        u"\u02C6": u"\x88", # MODIFIER LETTER CIRCUMFLEX ACCENT
        u"\u2030": u"\x89", # PER MILLE SIGN
        u"\u0160": u"\x8A", # LATIN CAPITAL LETTER S WITH CARON
        u"\u2039": u"\x8B", # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
        u"\u0152": u"\x8C", # LATIN CAPITAL LIGATURE OE
        u"\u017D": u"\x8E", # LATIN CAPITAL LETTER Z WITH CARON
        u"\u2018": u"\x91", # LEFT SINGLE QUOTATION MARK
        u"\u2019": u"\x92", # RIGHT SINGLE QUOTATION MARK
        u"\u201C": u"\x93", # LEFT DOUBLE QUOTATION MARK
        u"\u201D": u"\x94", # RIGHT DOUBLE QUOTATION MARK
        u"\u2022": u"\x95", # BULLET
        u"\u2013": u"\x96", # EN DASH
        u"\u2014": u"\x97", # EM DASH
        u"\u02DC": u"\x98", # SMALL TILDE
        u"\u2122": u"\x99", # TRADE MARK SIGN
        u"\u0161": u"\x9A", # LATIN SMALL LETTER S WITH CARON
        u"\u203A": u"\x9B", # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
        u"\u0153": u"\x9C", # LATIN SMALL LIGATURE OE
        u"\u017E": u"\x9E", # LATIN SMALL LETTER Z WITH CARON
        u"\u0178": u"\x9F", # LATIN CAPITAL LETTER Y WITH DIAERESIS
    }
    for src, dest in cp1252.items():
        text = text.replace(src, dest)
    text = text.encode('raw_unicode_escape')
    return text


def get_text_file(url, session=None):
    if session is None:
        r = requests.get(url)
    else:
        r = session.get(url)
    if r.status_code == 200:
        return r.text
    else:
        print('Failed to download file "%s"' % url.split('/')[-1])
        sys.exit()


def write_to_json_file(file_path, data, indent=None):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
    except:
        print('Failed to convert file "%s"' % file_path)
        sys.exit()
        
        
def deep_merge(base, nxt):
    # type conflict
    if not (isinstance(base, type(nxt)) or isinstance(nxt, type(base))):
        return nxt
        
    if isinstance(nxt, list):
        return base + nxt
    elif isinstance(nxt, set):
        return base | nxt
    elif isinstance(nxt, dict):
        for k, v in nxt.items():
            if k not in base:
                base[k] = v
            else:
                base[k] = deep_merge(base[k], v)
        return base
    
    # fallback
    return nxt


############################################################################
# SYNCHRONIZED PRINT FUNCTION
############################################################################
def synchronized(func):
    func.__lock__ = threading.Lock()
		
    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


@synchronized
def print_console(text):
    try:
        print(text)
    except:
        pass
        
        
############################################################################
# THREAD-SAFE FUNCTIONS
############################################################################
def thread_safe_makedirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
            