import azure.cognitiveservices.speech as speechsdk

def from_file():
    speech_config = speechsdk.SpeechConfig(subscription="YourSpeechKey", region="YourSpeechRegion")
    audio_config = speechsdk.AudioConfig(filename="your_file_name.wav")
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config,)

    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    print(speech_recognition_result.text)

from_file()