# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.conf import settings
import indicoio

# ----- Text algorithms sitemap -----
class TextAlgorithms:
    """
    Class to define various text related AI algorithms.

    Currently, we are using **Indico.io** services that provides various text
    related ai algorithms. (https://indico.io/docs)

    **Authors**: Gagandeep Singh
    """

    # Algorithm keys
    SENTIMENT = 'text_sentiment'     # Quickly and efficiently determine if text is positive or negative.
    EMOTION   = 'text_emotion'       # Predicts the emotion expressed by an author in a sample of text (anger, fear, joy, sadness, surprise).
    PERSONALITY = 'text_personality' # Predicts the personality traits of a text's author. (extraversion, openness, agreeableness, conscientiousness)
    PERSONAS    = 'text_personas'    # Predicts the Myers Briggs persona of an author based on a sample of text. (https://www.16personalities.com/personality-types)

    # List of currently active algorithms.
    # In case you want to turn-off an algorithm, remove that enum from this list
    # Warning: Before removing, make sure all pending responses that are yet to be processed are
    # completed. Also make sure there must be no pending response in the devices that have not been submitted.
    active_algo_keys = [SENTIMENT, EMOTION, PERSONALITY, PERSONAS]

    # Mapping of indicoio services key to corresponding feedvay algorithm key for text analysis.
    mapping_feedvay_indicio = {
        SENTIMENT: "sentiment",
        EMOTION: "emotion",
        PERSONALITY: "personality",
        PERSONAS: "personas"
    }

    @staticmethod
    def get_mapping_indicio_feedvay():
        """
        Returns inverse mapping of ``mapping_feedvay_indicio`` dictionary.
        :return: Dict

        **Authors**: Gagandeep Singh
        """
        map_inv = {v:k for k,v in TextAlgorithms.mapping_feedvay_indicio.iteritems()}
        return map_inv


class TextSentimentAnalysis:
    """
    Analyse text for sentiments e.i. determines if text is positive or negative.

    Currently using Indico.io service.
    Docs: https://indico.io/docs#sentiment

    **Output**:

        Return a number between 0 and 1 which is a probability representing the likelihood
        that the analyzed text is positive or negative.
        Format:
        {
            "score": <score>,
            "sentiment": "negative/neutral/positive"
        }


    **Authors**: Gagandeep Singh
    """
    algo_key = TextAlgorithms.SENTIMENT

    # Parameters
    thres_max_neg = 0.4
    thres_max_neutral = 0.6

    # Enums
    SENTI_NEGATIVE = 'negative'
    SENTI_NEUTRAL = 'neutral'
    SENTI_POSITIVE = 'positive'

    @staticmethod
    def formalize_results(score):
        """
        Method to transform Indicoio result to Feedvay result.
        :param score: Indicoio sentiment output; probability
        :return: Feedvay json

        **Authors**: Gagandeep Singh
        """

        if score <= TextSentimentAnalysis.thres_max_neg:
            sentiment = TextSentimentAnalysis.SENTI_NEGATIVE
        elif TextSentimentAnalysis.thres_max_neg < score <= TextSentimentAnalysis.thres_max_neutral:
            sentiment = TextSentimentAnalysis.SENTI_NEUTRAL
        else:
            sentiment = TextSentimentAnalysis.SENTI_POSITIVE

        result_final = {
            "score": score,
            "sentiment": sentiment
        }
        return result_final


class TextEmotionAnalysis:
    """
    Predicts the emotion expressed in a sample of text.

    Currently using Indico.io service.
    Docs: https://indico.io/docs#emotion

    **Output**:

        Returns a dictionary that maps from 5 emotions; ``anger``, ``fear``, ``joy``, ``sadness``, ``surprise``
        to the probability that the author is expressing the respective emotion.
        Format:
        {
            'anger': 0.007581704296171665,
            'joy': 0.07016665488481522,
            'fear': 0.8000516295433044,
            'sadness': 0.02512381225824356,
            'surprise': 0.06534374748375202
        }

    **Authors**: Gagandeep Singh
    """
    algo_key = TextAlgorithms.EMOTION

    @staticmethod
    def formalize_results(result):
        """
        Method to transform Indicoio result to Feedvay result.
        :return: Feedvay result json

        Currently nothing to formalize. Simply returns the result untouched.

        **Authors**: Gagandeep Singh
        """
        return result


class TextPersonalityAnalysis:
    """
    Predicts the personality traits int the text.

    Currently using Indico.io service.
    Docs: https://indico.io/docs#personality

    **Output**:

        Returns a dictionary that maps the following personality traits to their likelihood of describing the author:
        ``extraversion``, ``openness``, ``agreeableness``, ``conscientiousness``. (These values are independent, meaning the probabilities
        don't effect each other.)
        Format:
        {
            'extraversion': 0.384...,
            'openness': 0.730...,
            'agreeableness': 0.439...,
            'conscientiousness': 0.103...
        }

    **Authors**: Gagandeep Singh
    """
    algo_key = TextAlgorithms.PERSONALITY

    @staticmethod
    def formalize_results(result):
        """
        Method to transform Indicoio result to Feedvay result.
        :return: Feedvay result json

        Currently nothing to formalize. Simply returns the result untouched.

        **Authors**: Gagandeep Singh
        """
        return result

class TextPersonasAnalysis:
    """
    Predicts the Myers Briggs persona (https://www.16personalities.com/personality-types)
    of an author based on a sample of text.

    There are 16 Myers Briggs personas:
        'executive', 'debater', 'mediator', 'consul',
        'advocate', 'adventurer', 'logistician', 'commander',
        'entrepreneur', 'logician', 'protagonist', 'architect',
        'campaigner', 'entertainer', 'defender', 'virtuoso'

    Currently using Indico.io service.
    Docs: https://indico.io/docs#personas

    **Output**:

        Returns a dictionary that maps from the 16 Myers Briggs personas to the probability
        that the author aligns with the respective persona.
        Format:
        {
            'advocate': 0.03894013672918785,
            'debator': 0.038705012628395506,
            'mediator': 0.036483237448904055,
            ... 12 personas omitted ...,
            'consul': 0.12134217481571341
        }


    **Authors**: Gagandeep Singh
    """
    algo_key = TextAlgorithms.PERSONAS

    @staticmethod
    def formalize_results(result):
        """
        Method to transform Indicoio result to Feedvay result.
        :return: Feedvay result json

        Currently nothing to formalize. Simply returns the result untouched.

        **Authors**: Gagandeep Singh
        """
        return result

def analyse_text(text, list_algo_fv):
    """
    Method that analyses a text based on given set of algorithms.
    :param text: Text to be analysed.
    :param list_algo_fv: List of 'feedvay' algorithms enums
    :return: Data dictionary containing algo_key as key and result as value.

    **Exceptions**: Throws ``KeyError`` exception if there are any invalid keys
     that do not match according to ``TextAlgorithms.mapping_feedvay_indicio``.

    **Authors**: Gagandeep Singh
    """

    # --- Validation ---
    # Validate text
    if not (isinstance(text, str) or isinstance(text, unicode)):
        raise TypeError("text must a string or unicode.")

    # Validate algo keys and transform to indicoio keys
    list_algo_keys = [TextAlgorithms.mapping_feedvay_indicio[algo_key_fv] for algo_key_fv in list_algo_fv]
    # --- /Validation ---

    # Call service in bulk
    result_indico = indicoio.analyze_text(text, apis=list_algo_keys, api_key=settings.INDICOIO_API_KEY)

    # Formalize results
    map_indicoio_feedvay = TextAlgorithms.get_mapping_indicio_feedvay()

    result = {}
    for key_indico, output in result_indico.iteritems():
        if key_indico == 'sentiment':
            output = TextSentimentAnalysis.formalize_results(output)

        result[map_indicoio_feedvay[key_indico]] = output

    return result

