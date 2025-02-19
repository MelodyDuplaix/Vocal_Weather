import os
import azure.cognitiveservices.speech as speechsdk

def transcribe_from_microphone():
    SPEECH_KEY = os.environ.get('SPEECH_KEY')
    SPEECH_REGION = os.environ.get('SPEECH_REGION')
    
    # Configuration of the speech recognizer
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language="fr-FR"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Record of the audio
    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return {
            "text": speech_recognition_result.text,
            "status": "success"
        }
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        return {
            "text": None,
            "status": "speech could not be recognized"
        }
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            return {
                "text": None,
                "status": "Canceled: Error during speech recognition"
            }
        else:
            return {
                "text": None,
                "status": "Canceled: No speech input"
            }
    else:
        return {
            "text": None,
            "status": "Unknown error"
        }
        
        
if __name__ == "__main__":
    result = transcribe_from_microphone()
    if result["status"] == "success":
        print(result["text"])
    else:
        print(result["status"])
            
            