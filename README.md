# Audify
![Python version support](https://img.shields.io/pypi/pyversions/audiomentations)

![audify](/assets/audify.svg)

## Description
Audify is an application designed to enhance audio quality and provide transcription services. By leveraging the power of DeepFilterNet and OpenAI Whisper, Audify ensures a streamlined experience for users looking to improve their audio files and obtain accurate transcriptions.

### Features
Audio Enhancement: Utilizes DeepFilterNet to significantly enhance the audio quality.
Transcription: Leverages OpenAI Whisper to provide accurate transcriptions of audio files.

### Integrated Technologies
[DeepFilterNet](https://github.com/Rikorose/DeepFilterNet): A deep learning model for audio enhancement.
[OpenAI Whisper](https://github.com/openai/whisper): An automatic speech recognition (ASR) system by OpenAI.

### Author
Corey Tarter

### Version
1.0

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ctarter/audify.git

2. Navigate to the cloned repository:
   ```bash
   cd audify

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

   Need a Pytorch-specific alternative with GPU support? Check out [torch-audiomentations](https://github.com/asteroid-team/torch-audiomentations)!

## Usage
   ```bash
   python audify.py

### Example
  ```bash
  Audio Source:

  1. File
  2. Directory
  3. Link
  4. URL List
  5. YouTube

  Enter your choice: 1

  Select File: /path/to/audio/file.wav

  Denoise? (Y/N): Y

  Export as: 
  1. WAV
  2. MP3
  3. FLAC
  Enter your choice: 2

  Choose Folder: /path/to/output/folder

  Transcribe? (Y/N): Y

  Choose a transcription model:
  1. tiny.en
  2. base.en
  3. small.en
  4. medium.en

  Enter your choice: 2

  Transcribe with timestamps? (Y/N): Y

  Choose Folder: /path/to/transcription/folder

  Generate Keywords from transcription file? (Y/N): Y

  How many keywords to generate? 10

  Choose Folder: /path/to/keywords/folder

## License

Audify is free and open source! All code in this repository is dual-licensed under either:

* MIT License ([LICENSE-MIT](LICENSE-MIT) or [http://opensource.org/licenses/MIT](http://opensource.org/licenses/MIT))
* Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0))

at your option. This means you can select the license you prefer!

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, as defined in the Apache-2.0 license, shall be dual licensed as above, without any additional terms or conditions.
