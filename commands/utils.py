# -*- coding: utf8 -*-
import gettext
import json


def write_config(element, value, file='config.json'):
    with open(file, mode='r+', encoding='utf-8') as f:
        file = json.load(f)
        file[element] = value
        f.seek(0)
        f.write(json.dumps(file))
        f.truncate()


def load_language(locale):
    filename = "res/messages_%s.mo" % locale
    try:
        trans = gettext.GNUTranslations(open(filename, "rb"))
    except IOError:
        trans = gettext.NullTranslations()
    finally:
        trans.install()