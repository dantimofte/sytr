"""
    Developer Accused of Unreadable Code Refuses To Comment
"""
import time
import os

import google
import pyasn1
from google.cloud import translate
from threading import Thread
import logging

LOG = logging.getLogger("sytr.translate_manager")
LOG.propagate = True

ERRORS = {
    "ERR_GTM_0001": "QUERIES_PER_SEC is invalid, it should be a integer number higher than 0",
    "ERR_GTM_0002": "GOOGLE_PROJECT_ID env variable is missing",
    "ERR_GTM_0003": "GOOGLE_APPLICATION_CREDENTIALS env variable is missing",
    "ERR_GTM_0004": "file specified in GOOGLE_APPLICATION_CREDENTIALS does not exist / is not readable",
    "ERR_GTM_0005": "Google Key is invalid",
    "ERR_GTM_0006": "Google authentication failed",
}


class SentenceObj:
    def __init__(self, text, target_language):
        self.text = text
        self.translation = "None"
        self.ready = False
        self.target_language = target_language

    def __str__(self):
        return self.translation


class GoogleTranslateManager:

    def __init__(self):
        self._error_codes = {code: False for code in ERRORS.keys()}

        self._project_id = os.environ.get("GOOGLE_PROJECT_ID", None)  # "plasma-system-296217"
        self._client = None
        try:
            self._client = translate.TranslationServiceClient()
        except (google.auth.exceptions.DefaultCredentialsError, pyasn1.error.PyAsn1Error) as e:
            self._error_codes["ERR_GTM_0005"] = True
            LOG.error(ERRORS["ERR_GTM_0005"])

        self._location = "global"
        self._parent = f"projects/{self._project_id}/locations/{self._location}"
        self._qps = os.environ.get("QUERIES_PER_SEC", 10)
        self._check_for_errors()
        LOG.info(f"Startup sanity check: {self._error_codes}")

    def _check_for_errors(self):
        # check if QUERIES_PER_SEC env is an integer higher than 0
        if not self._qps:
            self._error_codes["ERR_GTM_0001"] = True
            LOG.error(ERRORS["ERR_GTM_0001"])
        else:
            val = 0
            try:
                val = int(self._qps)
            except ValueError:
                self._error_codes["ERR_GTM_0001"] = True
                LOG.error(ERRORS["ERR_GTM_0001"])
            finally:
                if val < 1:
                    self._error_codes["ERR_GTM_0001"] = True
                    LOG.error(ERRORS["ERR_GTM_0001"])

        # check if GOOGLE_PROJECT_ID env variable is missing
        if not self._project_id:
            self._error_codes["ERR_GTM_0002"] = True
            LOG.error(ERRORS["ERR_GTM_0002"])

        # check if GOOGLE_APPLICATION_CREDENTIALS env is set and the file exist and is readable
        gac_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None)
        if not gac_file:
            self._error_codes["ERR_GTM_0003"] = True
            LOG.error(ERRORS["ERR_GTM_0003"])
        else:
            if not os.access(gac_file, os.R_OK):
                self._error_codes["ERR_GTM_0004"] = True
                LOG.error(ERRORS["ERR_GTM_0004"])

        if self._client:
            test_sentence = SentenceObj("hello world", "de")
            try:
                self.translate_request(test_sentence)
            except google.api_core.exceptions.ServiceUnavailable as e:
                self._error_codes["ERR_GTM_0006"] = True
                LOG.error(ERRORS["ERR_GTM_0006"])

    def translate_text_batch(self, text_data, target_language):
        if any(self._error_codes.values()):
            return {"ok": False, "errors": [err for err in self._error_codes.keys() if self._error_codes[err]]}

        sentences = tuple(SentenceObj(text, target_language) for text in text_data)
        LOG.info('translating new batch of sentences')
        remaining_sentences = [*sentences, ]
        threads = []
        while remaining_sentences:
            sentences_to_process = remaining_sentences[:self._qps]
            remaining_sentences = remaining_sentences[self._qps:]

            for sentence in sentences_to_process:
                translator = Thread(target=self.translate_request,
                                    args=(sentence,),
                                    daemon=True)
                threads.append(translator)
                translator.start()
            if remaining_sentences:
                time.sleep(1)
        for t in threads:
            t.join()
        return {"ok": True, "translations": [sentence.translation for sentence in sentences]}

    def translate_request(self, sentence):
        # Details on supported types can be found here:
        # https://cloud.google.com/translate/docs/supported-formats
        translate_req = translate.TranslateTextRequest(
            {
                "parent": self._parent,
                "contents": (sentence.text,),
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "target_language_code": sentence.target_language,
            }
        )
        response = self._client.translate_text(request=translate_req)

        sentence.translation = response.translations[0].translated_text
        sentence.ready = True


def main():
    LOG.info("start translating")
    gtm = GoogleTranslateManager()
    result = gtm.translate_text_batch(text_data=("i am hungry", "imi este foame", "j'ai faim",), target_language="it")
    if result.get("ok", False):
        for translation in result.get("translations"):
            LOG.info(f"translation is {translation}")
    else:
        LOG.info(f"errors encountered : {' '.join(result.get('errors'))}")


if __name__ == "__main__":
    main()
