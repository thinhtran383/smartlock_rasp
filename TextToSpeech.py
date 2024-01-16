import pyttsx3

def speakText(text, rate=150):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.setProperty('voice', 0)
    engine.say(text)
    engine.runAndWait()
    
    
text = 'hello from raspberry pi 3'

speakText(text,rate=135)