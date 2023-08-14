# Imports the Google Cloud client library
from google.cloud import translate
import mtranslate as free_translate

class Translator:
    def __init__(self):
        self.init_google_professional()

    def init_google_professional(self):
        # Your Translate API key
        api_key = ''
        # Instantiates a client
        self.translate_client = translate.Client(api_key)

    def google_translation(self,text,targetLanguage="fr"):
        # Translates some text into Russian
        try:
            google_translation = self.translate_client.translate(text, target_language=targetLanguage)
            res=google_translation['translatedText'].encode('utf-8')
            return res
        except:
            print "Error in Google Translation!!!"
            return ""

    def free_translation(self,text,targetLanguage="fr"):
        try:
            res=free_translate.translate(text,targetLanguage,"auto")
            res=str(res)
            return res
        except:
            print "Error in Free Translation!!!"
            return ""

    def translation(self,text,targetLanguage="fr",freeFlag=False):
        if freeFlag:
            return self.free_translation(text,targetLanguage)
        else:
            return self.google_translation(text,targetLanguage)


if __name__=="__main__":
    translator=Translator()
    while True:
        input=raw_input("Your sentence: ")
        free_trans=translator.translation(text=input,targetLanguage="fr",freeFlag=True)
        #google_trans=translator.translation(text=input,targetLanguage="fr",freeFlag=False)
        print "Free Translation: ",free_trans
        #print "Google Translation: ",google_trans
        # free_trans=translator.translation(text=free_trans,targetLanguage="en",freeFlag=True)
        # google_trans=translator.translation(text=google_trans,targetLanguage="en",freeFlag=False)
        # print "Free Translation: ",free_trans
        # print "Google Translation: ",google_trans
