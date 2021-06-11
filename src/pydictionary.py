from nltk.corpus import wordnet
from spellchecker import SpellChecker

dictionary = SpellChecker()


def checkWordExistsInDictionary(word):
    if wordnet.synsets(word):
        return True, word
    otherwords = [w for w in dictionary.candidates(word) if wordnet.synsets(w)]
    if otherwords:
        return False, otherwords[0]
    return False, None


def getRecordsFromDictionary(word, n):
    syn = wordnet.synsets(word)
    dform = {
        "n": "noun",
        "v": "verb",
        "a": "adjective",
        "r": "adverb",
        "s": "adjective satellite",
    }

    results = list()
    antonyms = list()

    for i in syn:
        definition, examples, form = i.definition(), i.examples(), i.pos()
        definition = definition.capitalize()
        examples = list(map(str.capitalize, examples))
        form = dform[form]
        results.append([definition, examples, form])
        for j in i.lemmas():
            try:
                antonyms.append(j.antonyms()[0].name())
            except IndexError:
                pass

    return results[:n], antonyms
