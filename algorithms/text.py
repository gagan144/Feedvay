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


class TextSentimentAnalysis:
    """
    Algorithm class to analyse text for sentiments e.i. determines if text is positive or negative.

    Currently using Indico.io service.
    Docs: https://indico.io/docs#sentiment

    **Authors**: Gagandeep Singh
    """
    algo_key = 'text_sentiment'

    # Parameters
    thres_max_neg = 0.4
    thres_max_neutral = 0.6

    # Enums
    SENTI_NEGATIVE = 'negative'
    SENTI_NEUTRAL = 'neutral'
    SENTI_POSITIVE = 'positive'

    @staticmethod
    def formalize_results(probability):
        """
        Method to transform Indicoio result to Feedvay result.
        :param probability: Indicoio sentiment output; probability
        :return: Feedvay json

        **Authors**: Gagandeep Singh
        """

        if probability <= TextSentimentAnalysis.thres_max_neg:
            sentiment = TextSentimentAnalysis.SENTI_NEGATIVE
        elif TextSentimentAnalysis.thres_max_neutral < probability <= TextSentimentAnalysis.thres_max_neutral:
            sentiment = TextSentimentAnalysis.SENTI_NEUTRAL
        else:
            sentiment = TextSentimentAnalysis.SENTI_POSITIVE

        result_final = {
            "probability": probability,
            "sentiment": sentiment
        }
        return result_final



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
    result = indicoio.analyze_text(text, apis=list_algo_keys, api_key=settings.INDICOIO_API_KEY)

    # Formalize results


    return result

