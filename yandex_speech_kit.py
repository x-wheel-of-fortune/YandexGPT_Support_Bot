from speechkit import Session, SpeechSynthesis, ShortAudioRecognition


class YandexSpeechKit:
    def __init__(self, api_key: str):
        self._session = Session.from_api_key(
            api_key,
            x_client_request_id_header=True,
            x_data_logging_enabled=True,
        )
        self._synthesize_audio = SpeechSynthesis(self._session)
        self._recognize_short_audio = ShortAudioRecognition(self._session)

    async def text_to_speech(
            self,
            message_text: str,
            path: str = 'audio.ogg',
            person_voice: str = 'oksana',
            file_format: str = 'oggopus',
            rate: str = '16000',
    ):
        self._synthesize_audio.synthesize(
            path,
            text=message_text,
            voice=person_voice,
            format=file_format,
            sampleRateHertz=rate,
        )

    async def speech_to_text(
            self,
            file_path: str,
            file_format: str = 'oggopus',
            rate: str = '16000',
    ):
        with open(file_path, 'rb') as f:
            data = f.read()
        return self._recognize_short_audio.recognize(
            data,
            format=file_format,
            sampleRateHertz=rate,
        )
