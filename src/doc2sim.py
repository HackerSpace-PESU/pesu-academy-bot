import docx
import PyPDF2
from pathlib import Path
import numpy as np
from gensim.models.phrases import Phrases, ENGLISH_CONNECTOR_WORDS
from gensim.models.doc2vec import Doc2Vec
from nltk.tokenize import word_tokenize, sent_tokenize


def cosineSimilarity(A, B):
    return np.dot(A, B)/(np.linalg.norm(A)*np.linalg.norm(B))


def phraseTransform(sentences):
    words = list(map(word_tokenize, sentences))
    phrase_model = Phrases(words, min_count=5, threshold=0.5,
                           connector_words=ENGLISH_CONNECTOR_WORDS)
    converted_words = [phrase_model[sent] for sent in words]
    converted_sentences = [" ".join(w) for w in converted_words]
    return converted_sentences


def readDocx(document):
    document = docx.Document(document)
    paragraphs = [para.text.lower() for para in document.paragraphs]
    sentences = list()
    for p in paragraphs:
        sentences.extend(sent_tokenize(p))
    return sentences


def readPDF(document):
    pdfFileObj = open(document, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pages = [pdfReader.getPage(page).extractText().lower()
             for page in range(pdfReader.numPages)]
    sentences = list()
    for p in pages:
        sentences.extend(sent_tokenize(p))
    return sentences


def readOther(document):
    with open(document) as f:
        content = f.read().lower().strip()
    sentences = sent_tokenize(content)
    return sentences


def getText(document):
    p = Path(document)
    extension = p.suffix
    if extension == ".docx":
        return readDocx(document)
    elif extension == ".pdf":
        return readPDF(document)
    else:
        return readOther(document)


def createDoc2VecModel(train_text, phrase=False):
    model = Doc2Vec(vector_size=300, window=2, epochs=20, min_count=1, seed=0)
    model.build_vocab(train_text)
    model.train(train_text, total_examples=model.corpus_count, epochs=50)
    return model