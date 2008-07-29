#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import local
from magicbullet.modeling import DictWrapper

_thread_data = local()
_undefined = object()

def get_language():
    return getattr(_thread_data, "language", None)

def set_language(language):
    setattr(_thread_data, "language", language)


class TranslationsRepository(DictWrapper):

    def __init__(self):
        self.__translations = {}
        DictWrapper.__init__(self, self.__translations)

    def __setitem__(self, language, translation):
        self.__translations[language] = translation  

    def define(self, key, **strings):

        for language, string in strings.iteritems():
            translation = self.__translations.get(language)

            if translation is None:
                translation = Translation()
                self.__translations[language] = translation
            
            translation[key] = string

    def __call__(self, key, *args, **kwargs):
        
        language = get_language()
        translation = self.__translations.get(language, _undefined)

        if translation is _undefined:
            raise KeyError("Can't find a translation for %s" % key)
        
        return translation(key, *args, **kwargs)

    def request(self, key, *args, **kwargs):
        
        language = get_language()
        translation = self.__translations.get(language, _undefined)

        if translation is _undefined:
            return key
        else:
            return translation.request(key, *args, **kwargs)


class Translation(DictWrapper):
    
    fallback = None

    def __init__(self):
        self.__strings = {}
        DictWrapper(self.__strings)

    def __setitem__(self, key, string):
        self.__strings[key] = string

    def _get_with_fallback(self, key, default = None):
        
        string = self.__strings.get(key, _undefined)

        if string is _undefined:
            if self.fallback:
                for fallback in self.fallback:
                    string = fallback._get_with_fallback(key)
                    if string is not _undefined:
                        break
                else:
                    string = default

        return string

    def __call__(self, key, *args, **kwargs):
        
        string = self._get_with_fallback(key, _undefined)

        if string is _undefined:
            raise KeyError("Can't find a translation for %s" % key)
             
        # Custom python expression
        if callable(string):
            string = string(self, *args, **kwargs)

        # String formatting
        elif args or kwargs:

            if args and kwargs:
                raise ValueError("Can't inject both positional and keyword "
                    "arguments into a translation")

            string = string % (args or kwargs)

        return string

    def request(self, key, *args, **kwargs):
        try:
            return self(key, *args, **kwargs)
        except KeyError:
            return key

