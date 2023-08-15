from speechkit import Session, SpeechSynthesis, ShortAudioRecognition
import yaml


class YandexSpeechKit:

    __api_key_session = Session

    def __init__(self):
        with open('config.yaml', encoding="utf8") as file:
            cfg = yaml.safe_load(file)
        self.__api_key_session = Session.from_api_key(cfg["SPEECH_KIT_API_KEY"], x_client_request_id_header=True, x_data_logging_enabled=True)

    async def text_to_speech(self, message_text, path='audio.ogg', person_voice='oksana', file_format='oggopus', rate='16000'):
        synthesize_audio = SpeechSynthesis(self.__api_key_session)
        synthesize_audio.synthesize(path,
                                    text=message_text,
                                    voice=person_voice,
                                    format=file_format,
                                    sampleRateHertz=rate)

    async def speech_to_text(self, file_path, file_format='oggopus', rate='16000'):
        recognize_short_audio = ShortAudioRecognition(self.__api_key_session)
        with open(file_path, "rb") as f:
            data = f.read()
        text = recognize_short_audio.recognize(data, format=file_format, sampleRateHertz=rate)
        return text
