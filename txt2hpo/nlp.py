import spacy
from gensim.parsing.preprocessing import remove_stopwords
from txt2hpo.config import logger
from txt2hpo.util import hpo_network
from nltk.stem import RegexpStemmer

try:
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
except OSError:
    logger.info('Performing a one-time download of an English language model for the spaCy POS tagger\n')
    from spacy.cli import download
    download('en')
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])


# these are used in hpo as part of phenotype definition, should block from filtering
remove_from_stops = "first second third fourth fifth under over front back behind ca below without no not "
remove_from_stops += "out up side right left more less during than take move full"
for not_a_stop in remove_from_stops.split(" "):
    nlp.vocab[not_a_stop].is_stop = False
    nlp.vocab[not_a_stop.capitalize()].is_stop = False

st = RegexpStemmer('ing$|e$|able$|ic$|ia$|ity$|al$|ly$', min=7)


def similarity_term_to_context(term, context, model):
    """
    Score similarity (term|context)
    :param term: hpo term
    :param context: context of term
    :param model: doc2vec model used to score term given context
    :return: float
    """
    def remove_out_of_vocab(tokens):
        return [x for x in tokens if x in model.vocab]

    hpo_term = hpo_network.nodes[term]
    hpo_term_definition = hpo_term['name']
    term_tokens = remove_out_of_vocab(remove_stopwords(hpo_term_definition).split())
    context_tokens = remove_out_of_vocab(remove_stopwords(context).split())
    if term_tokens and context_tokens:
        sim = model.n_similarity(term_tokens, context_tokens)
    else:
        sim = -0.999
    return sim
