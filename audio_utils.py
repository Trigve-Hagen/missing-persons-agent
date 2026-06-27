import os
from pydub import AudioSegment

def prepare_audio_for_lfm(input_path: str, output_path: str = None) -> str:
    """
    Converts and resamples an incoming audio file to standard 16kHz mono WAV format
    required by local models like LFM2.5-Audio-1.5B.
    """
    # 1. Automatically determine output path if none is provided
    if not output_path:
        base_name, _ = os.path.splitext(input_path)
        output_path = f"{base_name}_lfm_ready.wav"

    # 2. Extract format extension to assist pydub's decoder
    file_extension = os.path.splitext(input_path)[1].lower().replace('.', '')

    print(f"Processing audio: {input_path} (Format: {file_extension})")

    try:
        # 3. Load the source audio file
        audio = AudioSegment.from_file(input_path, format=file_extension)

        # 4. Standardize settings (16000Hz frame rate, 1 channel/mono, 16-bit depth)
        processed_audio = (
            audio.set_frame_rate(16000)
                 .set_channels(1)
                 .set_sample_width(2) # 2 bytes = 16-bit depth
        )

        # 5. Export to pure WAV container
        processed_audio.export(output_path, format="wav")
        print(f"Successfully exported LFM-compliant audio to: {output_path}")

        return output_path

    except Exception as e:
        raise RuntimeError(f"Failed to process audio file: {str(e)}")

# --- Usage Example ---
if __name__ == "__main__":
    # Example converting a variable format file (e.g., iPhone voice memo format)
    raw_recording = "./interview.m4a"

    # Preprocess the file
    ready_wav_path = prepare_audio_for_lfm(raw_recording)

    # Ready to be used as graph inputs!
    # inputs = {"audio_path": ready_wav_path}
