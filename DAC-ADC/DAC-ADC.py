import pyaudio
import struct
import sys
import threading
import keyboard

def read_wav(filename):
    try:
        with open(filename, 'rb') as f:
            # Read the RIFF header
            riff = f.read(12)
            if riff[:4] != b'RIFF' or riff[8:] != b'WAVE':
                raise ValueError("Invalid WAV file")

            # Read the chunks
            fmt = None
            data = None

            while True:
                chunk_header = f.read(8)
                if len(chunk_header) < 8:
                    break  # End of file reached
                chunk_type = chunk_header[:4]
                chunk_size = struct.unpack('<I', chunk_header[4:])[0]

                if chunk_type == b'fmt ':
                    fmt = f.read(chunk_size)
                elif chunk_type == b'data':
                    data = f.read(chunk_size)
                    break
                else:
                    f.seek(chunk_size, 1)  # Skip this chunk

            if fmt is None or data is None:
                raise ValueError("Missing fmt or data chunk")

            audio_format, num_channels, sample_rate, byte_rate, block_align, bits_per_sample = struct.unpack('<HHIIHH',
                                                                                                             fmt[:16])

            if bits_per_sample != 16:
                raise ValueError("Only 16-bit WAV files are supported.")

            num_samples = len(data) // 2
            samples = struct.unpack('<' + 'h' * num_samples, data)

            return sample_rate, num_channels, samples
    except Exception as e:
        print(f"Error reading WAV file: {e}")
        sys.exit(1)


def write_wav(filename, sample_rate, num_channels, samples):
    try:
        with open(filename, 'wb') as f:
            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + len(samples) * 2))
            f.write(b'WAVE')

            f.write(b'fmt ')
            f.write(struct.pack('<IHHIIHH', 16, 1, num_channels, sample_rate, sample_rate * num_channels * 2, num_channels * 2, 16))

            f.write(b'data')
            f.write(struct.pack('<I', len(samples) * 2))
            for sample in samples:
                f.write(struct.pack('<h', sample))
    except Exception as e:
        print(f"Error writing WAV file: {e}")
        sys.exit(1)


def record_audio(output_filename, sample_rate, channels, stop_event):
    p = pyaudio.PyAudio()

    # Check if the given number of channels is supported
    if channels not in (1, 2):
        print(f"Invalid number of channels: {channels}. Only 1 (mono) or 2 (stereo) are supported.")
        return

    try:
        stream = p.open(format=pyaudio.paInt16,  # 16-bit format
                        channels=channels,
                        rate=sample_rate,  
                        input=True,
                        frames_per_buffer=1024)
    except OSError as e:
        print(f"Error opening stream: {e}")
        p.terminate()
        return

    frames = []

    print("Recording... Press Escape to stop.")
    while not stop_event.is_set():
        data = stream.read(1024)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Convert frames to samples
    samples = []
    for frame in frames:
        samples.extend(struct.unpack('<' + 'h' * (len(frame) // 2), frame))

    write_wav(output_filename, sample_rate, channels, samples)


def play_audio(input_filename):
    sample_rate, channels, samples = read_wav(input_filename)

    p = pyaudio.PyAudio()

    try:
        stream = p.open(format=pyaudio.paInt16,
                        channels=channels,
                        rate=sample_rate,
                        output=True)

        print("Playing audio...")
        chunk_size = 1024
        for i in range(0, len(samples), chunk_size):
            chunk = samples[i:i + chunk_size]
            data = struct.pack('<' + 'h' * len(chunk), *chunk)
            stream.write(data)

        stream.stop_stream()
        stream.close()
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        p.terminate()

    print("Finished playing.")


def main():
    while True:
        print("Choose an option:")
        print("1. Record audio (analog to digital)")
        print("2. Play audio (digital to analog)")
        print("3. Exit")
        choice = input("Enter 1, 2 or 3: ")

        if choice == '1':
            output_filename = input("Enter the output file name (e.g., output.wav): ")
            try:
                sample_rate = int(input("Enter sample rate (e.g., 44100): "))
                channels = int(input("Enter number of channels (1 for mono, 2 for stereo): "))
            except ValueError:
                print("Invalid input. Please enter numeric values for sample rate and channels.")
                continue

            stop_event = threading.Event()
            record_thread = threading.Thread(target=record_audio,
                                             args=(output_filename, sample_rate, channels, stop_event))
            record_thread.start()

            keyboard.wait('esc')
            stop_event.set()
            record_thread.join()

        elif choice == '2':
            input_filename = input("Enter the input file name (e.g., input.wav): ")
            play_audio(input_filename)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2 or 3.")


if __name__ == "__main__":
    main()
