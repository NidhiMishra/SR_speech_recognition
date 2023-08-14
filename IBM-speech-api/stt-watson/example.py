from stt_watson.SttWatson import SttWatson
from stt_watson.SttWatsonAbstractListener import SttWatsonAbstractListener

"""
Example of listener to use data given by stt-watson (stt-watson notify hypothesis to his listeners when he receive it)

Hypothesis format:
{
    'confidence': '0.1' // confidence of the sentence or words if exist
    'transcript': 'the transcription of your voice'
}
"""
class MyListener(SttWatsonAbstractListener):
    def __init__(self):
        pass
    """
    This give hypothesis from watson when your sentence is finished
    """
    def listenHypothesis(self, hypothesis):
        print "Hypothesis: {0}".format(hypothesis)

    """
    This give the json received from watson
    """
    def listenPayload(self, payload):
        print(u"Text message received: {0}".format(payload))
    """
    This give hypothesis from watson when your sentence is not finished
    """
    def listenInterimHypothesis(self, interimHypothesis):
        print "Interim hypothesis: {0}".format(interimHypothesis)


myListener = MyListener()
sttWatson = SttWatson('551b36c1-0b88-46a4-bd0e-436ffe83c141', 'E1p74QKa2Gyu')
sttWatson.addListener(myListener)
sttWatson.run()