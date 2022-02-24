from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import pyttsx3
import moviepy.editor as mp
from moviepy.editor import VideoFileClip
import subprocess
import ffmpeg

## !!! Note, It will ask for confirmation on overwriting the existing file (video2.mp4 and output.mp4) in terminal after clicking on Merge Button !!!

#Declaration of Some global variable to use later
global finaltext , vduration , aduration, voicetype 

#Assigning Default values for the variable in case none assigned
voicetype = "m"
finaltext = " default"

#To view the Main HomePage(template of upload.html)
def index(request):
    return render(request , 'upload.html')

#This Function takes the text file Input or
#The text from TextBox Input and renders the Text on upload.html as "Your Text:- ---"
def upload(request):
    if request.method == "POST":
        if "text" in request.POST:
            text = request.POST['text']  #Takes Input text from TextBox and assigns its string value to "text" variable
            global finaltext
            finaltext = text
            txttovoice(text, "f") # text-to-voice function is called for the temporary audio.mp3 generation used in calculating the final audio duration
        
            return render(request, 'upload.html' , {'content_t' : "Your Text :- " +text})
        else:
            
            for file in request.FILES.getlist('file'):
                print(file)
                
            line = file.read() # Extracting the text out as string from text file
            
            finaltext = str(line,'utf-8') # Encoding of the bytes string to normal and assigning it to global "finaltext"
            
            fs = FileSystemStorage(location="files/") # Define location for saving the text file
            fs.delete("text")
            filename = fs.save("text",file) # Saving the text file
            
            txttovoice(line, "f") # text-to-voice function is called for the temporary audio.mp3 generation used in calculating the final audio duration

            return render(request, 'upload.html' , {'content_u' : "Your Text :- " + finaltext})

# Function for Conversion of text to voice (Temporary Audio)
def txttovoice(text , voiceType):
    if text == "":
        print("No text to speak")
    else:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        rate = engine.getProperty('rate')
        if voiceType == "m":
            engine.setProperty('voice', voices[0].id)
        else:
            engine.setProperty('voice', voices[1].id) 
        engine.setProperty('rate', 400)  
        engine.save_to_file(text, ("audio.mp3")) # Converts text to audio file (audio.mp3) and saves it
               
        engine.runAndWait()    
        engine.stop() 

# Function for Conversion of text to voice (Final Audio)
def txttovoicef(text , voiceType):
    if text == "":
        print("No text to speak")
    else:
        global vduration,aduration
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        rate = engine.getProperty('rate')
        if voiceType == "m":
            engine.setProperty('voice', voices[0].id)
        else:
            engine.setProperty('voice', voices[1].id) 
        engine.setProperty('rate', (400 * aduration)/vduration) # rate of final audio is calculated as product of rate of temporary audio and ratio of duration of temporary audio and video 
        engine.save_to_file(text, ("audiof.aac"))
        engine.say(text)    # Says the Audio out loud    
        engine.runAndWait()    
        engine.stop()

# Get the VoiceType selected from DropDown and assigns the value to global voicetype
def voice(request):
    global voicetype
    voicetype =  request.GET['dropdown'] # Gets the value from options (Male or Female)
    return render(request,"upload.html")

# Function for Input of Video file
def videoupload(request):  
    if request.method == 'POST':
        global vduration , aduration,finaltext

        for file in request.FILES.getlist("file"):
            print(file)
             
            fs = FileSystemStorage(location="files/") # Define location for saving the text file
            fs.delete("video.mp4")
            fs.save("video.mp4",file) # Saving the uploaded video "file" as video.mp4

        audio = mp.AudioFileClip("./audio.mp3")
        video = mp.VideoFileClip("./files/video.mp4")
        vduration = video.duration #Accessing the duration of Video
        aduration = audio.duration #Accessing the duration of Video
        txttovoicef(finaltext , voicetype)
        
        fsa = FileSystemStorage(location="") # Defining storage access for accessing the temporary audio file
        fsa.delete("audio.mp3") # Deleting the temporary Audio file

        print(voicetype)
        return render(request,"upload.html" , {'preview' : "Ready to Merge!   -->  "})

# Function for Stripping audio out of Video;
# Adding the Final audio on the Video;  (after clicking Merge Button)
# Previewing the Final Video(Spoken Tutorial) on another page (preview.html)
def preview(request):
    if request.method == 'POST':
        # Removing the already existed audio from video using ffmpeg
        subprocess.run("ffmpeg -i files/video.mp4 -vcodec copy -an ./files/video2.mp4") 
        
        # Merging the video with audio using ffmpeg , Into the final Spoken Tutorial
        subprocess.run("ffmpeg -i ./files/video2.mp4 -i audiof.aac -c:v copy -c:a aac -crf 28 ./files/output.mp4")

        fs = FileSystemStorage(location="files/")
        # We will have total 3 video files - Input Video, Temporary Audioless Video , Final Output Video
        fs.delete("video2.mp4") # Deleting the unneccasary temporary video file
        return render(request,"preview.html" )
