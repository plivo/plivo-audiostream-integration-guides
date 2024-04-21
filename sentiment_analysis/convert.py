from pydub import AudioSegment


def convert_audio(file_name):
    # Load the audio
    audio_path = file_name
    audio = AudioSegment.from_file(audio_path, format="raw", frame_rate=16000, channels=1, sample_width=2)

    # Export to WAV
    output_path = f"{file_name.split('.')[0]}.wav"
    audio.export(output_path, format="wav")

    print("Conversion completed successfully.")
    return output_path
