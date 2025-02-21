import os
import azure.cognitiveservices.speech as speechsdk

def transcribe_from_microphone(file_location = None):
    """
    Transcribe the speech from the microphone to text using Azure Speech Service.
    
    Returns:
        dict: dict with the text of the transcription, the status of the transcription, and the status code
    """  
    SPEECH_KEY: str | None = os.environ.get('SPEECH_KEY')
    SPEECH_REGION = os.environ.get('SPEECH_REGION')
    
    # Configuration of the speech recognizer
    speech_config = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
    speech_config.speech_recognition_language="fr-FR"
    if file_location:
        audio_config = speechsdk.audio.AudioConfig(filename=file_location)
    else:
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    # Record of the audio
    speech_recognition_result = speech_recognizer.recognize_once_async().get()
    
    # return result of the transcription according to the status of the recognition
    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return {
            "text": speech_recognition_result.text,
            "status": "success",
            "status_code": 200
        }
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        return {
            "text": None,
            "status": "speech could not be recognized",
            "status_code": 204
        }
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))
            return {
                "text": None,
                "status": "Canceled: Error during speech recognition",
                "status_code": 500
            }
        else:
            return {
                "text": None,
                "status": "Canceled: No speech input",
                "status_code": 400
            }
    else:
        return {
            "text": None,
            "status": "Unknown error",
            "status_code": 500
        }
        
        
if __name__ == "__main__":
    result = transcribe_from_microphone()
    if result["status"] == "success":
        print(result["text"])
    else:
        print(f"Status: {result['status']}, Status Code: {result['status_code']}")
