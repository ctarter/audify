#!/usr/bin/env python3

import csv
import os
import re
import shutil
import requests
import whisper

from collections import Counter
from pytube import YouTube
from pydub import AudioSegment
from pydub.silence import detect_silence
from df.enhance import enhance, init_df, load_audio, save_audio

TMP_DIR = './tmp'
TMP_INPUT = './tmp/input'
TMP_SEGMENTS = './tmp/segments'
TMP_DENOISE = './tmp/denoise'

def clear():
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)

def create_directories():
    directories = (TMP_INPUT, TMP_SEGMENTS, TMP_DENOISE)
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    return directories

def main():
    audio_file_path = directory_path = audio_url = list_path = youtube_url = None
    source_choice = denoise_choice = export_as = output_location_audio = None
    transcribe_choice = timestamps_choice = output_location_transcriptions = model_choice = None
    keywords_choice = output_location_keywords = num_keywords = None
    print("Audio Source:\n")
    source_choice = ["File", "Directory", "Link", "URL List", "YouTube"]
    for i, source_choice in enumerate(source_choice, 1):
        print(f"{i}. {source_choice}")
    source_choice = input("\nEnter your choice: ")

    if source_choice == '1':
        # Single File
        audio_file_path = input("\nSelect File: ")
        print(f"{audio_file_path}")

    elif source_choice == '2':
        # Directory
        directory_path = input("\nSelect Folder: ")

    elif source_choice == '3':
        # URL
        audio_url = input("\nLink: ")

    elif source_choice == '4':
        # List of URLs
        list_path = input("\nSelect File: ")

    elif source_choice == '5':
        # YouTube Link
        youtube_url = input("\nLink: ")

    # Denoise
    denoise_choice = input("\nDenoise? (Y/N): ")
    if denoise_choice.lower() == 'y':
        export_as = get_export_as_choice()
        output_location_audio = input("\nChoose Folder: ")

    else:
        export_as = get_export_as_choice()
        output_location_audio = input("\nChoose Folder: ")

    # Transcribe
    transcribe_choice = input("\nTranscribe? (Y/N): ")
    if transcribe_choice.lower() == 'y':
        # Choose Transcription Model
        print("\nChoose a transcription model:\n")
        model_options = ["tiny.en", "base.en", "small.en", "medium.en"]
        for i, option in enumerate(model_options, 1):
            print(f"{i}. {option}")
        model_choice = model_options[int(input("\nEnter your choice: ")) - 1]

        # Transcribe with timestamps
        timestamps_choice = input("\nTranscribe with timestamps? (Y/N): ")

        if timestamps_choice.lower() == 'y':
            output_location_transcriptions = input("\nChoose Folder: ")

        else:
            output_location_transcriptions = input("\nChoose Folder: ")

        # Generate Keywords
        keywords_choice = input("\nGenerate Keywords from transcription file? (Y/N): ")
        if keywords_choice.lower() == 'y':
            # Number of Keywords
            num_keywords = int(input("\nHow many keywords to generate? "))
            
            # Output Location
            output_location_keywords = input("\nChoose Folder: ")

    submit(source_choice, audio_file_path, directory_path, audio_url, list_path, youtube_url, 
           denoise_choice, export_as, output_location_audio, transcribe_choice, 
           timestamps_choice, output_location_transcriptions, model_choice, keywords_choice, 
           output_location_keywords, num_keywords, TMP_INPUT, TMP_SEGMENTS, TMP_DENOISE)

def submit(source_choice, audio_file_path, directory_path, audio_url, list_path, youtube_url, 
           denoise_choice, export_as, output_location_audio, transcribe_choice, 
           timestamps_choice, output_location_transcriptions, model_choice, keywords_choice, 
           output_location_keywords, num_keywords, TMP_INPUT, TMP_SEGMENTS, TMP_DENOISE):
    
    if source_choice == '1':
        download_file(audio_file_path, TMP_INPUT)
    elif source_choice == '2':
        download_directory(directory_path, TMP_INPUT)
    elif source_choice == '3':
        download_url(audio_url, TMP_INPUT)
    elif source_choice == '4':
        download_list(list_path, TMP_INPUT)
    elif source_choice == '5':
        download_youtube(youtube_url, TMP_INPUT)

    if denoise_choice.lower() == 'y':
        denoise(export_as, output_location_audio, TMP_INPUT, TMP_SEGMENTS, TMP_DENOISE)
    else:
        bypass_denoise(export_as, output_location_audio, TMP_INPUT)

    if transcribe_choice.lower() == 'y':
        if timestamps_choice.lower() == 'y':
            transcribe_timestamp(output_location_audio, output_location_transcriptions, model_choice, export_as)
        else:
            transcribe(output_location_audio, output_location_transcriptions, model_choice, export_as)

        if keywords_choice.lower() == 'y':
            keywords(output_location_keywords, output_location_transcriptions, num_keywords)

def get_export_as_choice():
    print("\nExport As:\n")
    export_as_options = ["mp3", "wav", "m4a"]
    for i, option in enumerate(export_as_options, 1):
        print(f"{i}. {option}")
    choice = int(input("\nEnter your choice: ")) - 1
    return export_as_options[choice]

def download_file(audio_file_path, TMP_INPUT):
    shutil.copy(audio_file_path, TMP_INPUT)

def download_directory(directory_path, TMP_INPUT):
    for filename in os.listdir(directory_path):
        if filename.endswith((".mp3", ".wav", ".m4a")):
            shutil.copy(os.path.join(directory_path, filename), os.path.join(TMP_INPUT, filename))

def download_url(audio_url, TMP_INPUT):
    response = requests.get(audio_url)
    if response.status_code == 200:
        filename = os.path.join(TMP_INPUT, os.path.basename(audio_url))
        with open(filename, 'wb') as file:
            file.write(response.content)

def download_list(list_path, TMP_INPUT):
    with open(list_path, 'r') as file:
        urls = file.read().splitlines()

    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            filename = os.path.join(TMP_INPUT, os.path.basename(url))
            with open(filename, 'wb') as audio_file:
                audio_file.write(response.content)

def download_youtube(youtube_url, TMP_INPUT):
    yt = YouTube(youtube_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    
    if audio_stream:
        output_path = os.path.join(TMP_INPUT, f"{yt.title}.mp3")
        audio_stream.download(output_path=output_path)

def denoise(export_as, output_location_audio, TMP_INPUT, TMP_SEGMENTS, TMP_DENOISE):
    for filename in os.listdir(TMP_INPUT):
        if filename.endswith(('.mp3', '.wav', '.m4a')):
            audio = AudioSegment.from_file(os.path.join(TMP_INPUT, filename))
            
            # Normalize the audio with headroom=1
            audio = audio.normalize(headroom=1)

            # Initialize segment start and end times (in milliseconds)
            start_time = 0
            end_time = 300000
            segment_counter = 1
            
            # Loop to create segments of 5 minutes
            while start_time < len(audio):
                segment = audio[start_time:end_time]
                segment_filename = f"{segment_counter}__{filename.split('.')[0]}.wav"
                segment.export(os.path.join(TMP_SEGMENTS, segment_filename), format="wav")
                
                # Update start and end times for next iteration
                start_time += 300000
                end_time += 300000
                segment_counter += 1
            
            model, df_state, _ = init_df()
            for segment_filename in os.listdir(TMP_SEGMENTS):
                    if segment_filename.endswith(".wav"):
                        segments = os.path.join(TMP_SEGMENTS, segment_filename)
                        save_path = os.path.join(TMP_DENOISE, segment_filename)
                        audio, _ = load_audio(segments, sr=df_state.sr())
                        enhanced = enhance(model, df_state, audio)
                        save_audio(save_path, enhanced, df_state.sr())
            
            combined = AudioSegment.empty()
            for i in range(1, segment_counter):
                segment_filename = f"{i}__{filename.split('.')[0]}.wav"
                segment = AudioSegment.from_file(os.path.join(TMP_DENOISE, segment_filename))
                combined += segment
            
            # Save the combined audio file
            combined.export(os.path.join(output_location_audio, f"{filename.split('.')[0]}.{export_as}"), format=export_as)

            # Delete all files in TMP_SEGMENTS and TMP_DENOISE
            for folder in [TMP_SEGMENTS, TMP_DENOISE]:
                for file in os.listdir(folder):
                    os.unlink(os.path.join(folder, file))

            # Delete current working file from TMP_INPUT
            os.unlink(os.path.join(TMP_INPUT, filename))

def bypass_denoise(export_as, output_location_audio, TMP_INPUT):
    for filename in os.listdir(TMP_INPUT):
        if filename.endswith(('.mp3', '.wav', '.m4a')):
            audio = AudioSegment.from_file(os.path.join(TMP_INPUT, filename))
            new_filename = f"{filename.split('.')[0]}.{export_as}"
            audio.export(os.path.join(output_location_audio, new_filename), format=export_as)

def transcribe_timestamp(output_location_audio, output_location_transcriptions, model_choice, export_as):
    model = whisper.load_model(model_choice)

    for file_name in os.listdir(output_location_audio):
        if file_name.endswith(tuple(export_as)):
            input_file_path = os.path.join(output_location_audio, file_name)
            audio = AudioSegment.from_file(input_file_path, format=file_name.split('.')[-1])
            output_file_path = os.path.join(output_location_transcriptions, f"{os.path.splitext(file_name)[0]}.txt")

            start_point = 0
            transcribed_text = ""

            while start_point < len(audio):
                tentative_end_point = start_point + 10 * 1000  # 10 seconds in milliseconds
                segment = audio[start_point:tentative_end_point]
                silence_ranges = detect_silence(segment, min_silence_len=100, silence_thresh=-40)
                
                end_point = tentative_end_point if not silence_ranges else start_point + silence_ranges[-1][1]
                
                start_time = int(start_point / 1000)
                end_time = int(end_point / 1000)
                
                segment.export("temp.wav", format="wav")
                result = model.transcribe("temp.wav")
                segment_text = f"{start_time} - {end_time}: {result['text']}\n"
                transcribed_text += segment_text

                with open(output_file_path, "a") as f:
                    f.write(segment_text)

                os.remove("temp.wav")
                start_point = end_point

def transcribe(output_location_audio, output_location_transcriptions, model_choice, export_as):
    model = whisper.load_model(model_choice)

    for file_name in os.listdir(output_location_audio):
        if file_name.endswith(tuple(export_as)):
            input_file_path = os.path.join(output_location_audio, file_name)
            output_file_path = os.path.join(output_location_transcriptions, f"{os.path.splitext(file_name)[0]}.txt")

            result = model.transcribe(input_file_path)
            transcribed_text = result["text"]

            with open(output_file_path, "w") as f:
                f.write(transcribed_text)

def keywords(output_location_keywords, output_location_transcriptions, num_keywords):
    exclude_words = []
    with open("/home/corey/projects/audify/exclude.csv") as f:
        reader = csv.reader(f)
        exclude_words = [word.lower() for row in reader for word in row]
    for filename in os.listdir(output_location_transcriptions):
        if filename.endswith(".txt"):
            with open(os.path.join(output_location_transcriptions, filename)) as f:
                words = re.findall(r'\b\w+\b', f.read().lower())
            word_counts = Counter(word for word in words if word not in exclude_words)
            with open(os.path.join(output_location_keywords, f"{filename}_keywords"), 'w') as f:
                for word, count in word_counts.most_common(num_keywords):
                    f.write(f"{word}: {count}\n")

if __name__ == "__main__":
    clear()
    create_directories()
    main()
    clear()
