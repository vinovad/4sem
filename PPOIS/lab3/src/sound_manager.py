import pygame
import numpy as np
import os


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.volume = 0.7
        self._generate_sounds()

    def _make_beep(self, frequency, duration, wave_type="sine", volume=0.5, sample_rate=44100):
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames, endpoint=False)
        if wave_type == "sine":
            wave = np.sin(2 * np.pi * frequency * t)
        elif wave_type == "square":
            wave = np.sign(np.sin(2 * np.pi * frequency * t))
        elif wave_type == "sawtooth":
            wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
        else:
            wave = np.sin(2 * np.pi * frequency * t)
        envelope = np.ones(frames)
        fade_samples = min(int(0.1 * sample_rate), frames // 4)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        envelope[:fade_samples // 2] = np.linspace(0, 1, fade_samples // 2)
        wave = (wave * envelope * volume * 32767).astype(np.int16)
        stereo = np.stack([wave, wave], axis=-1)
        return pygame.sndarray.make_sound(stereo)

    def _make_chord(self, freqs, duration, volume=0.4):
        sample_rate = 44100
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames, endpoint=False)
        wave = np.zeros(frames)
        for f in freqs:
            wave += np.sin(2 * np.pi * f * t)
        wave /= len(freqs)
        fade_samples = min(int(0.15 * sample_rate), frames // 3)
        envelope = np.ones(frames)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        wave = (wave * envelope * volume * 32767).astype(np.int16)
        stereo = np.stack([wave, wave], axis=-1)
        return pygame.sndarray.make_sound(stereo)

    def _generate_sounds(self):
        try:
            self.sounds["match"] = self._make_chord([523, 659, 784], 0.3, 0.5)
            self.sounds["combo"] = self._make_chord([659, 784, 988, 1047], 0.4, 0.5)
            self.sounds["error"] = self._make_beep(200, 0.2, "square", 0.3)
            self.sounds["bomb"] = self._make_beep(150, 0.4, "sawtooth", 0.5)
            self.sounds["lightning"] = self._make_beep(800, 0.15, "square", 0.4)
            self.sounds["star"] = self._make_chord([1047, 1319, 1568], 0.5, 0.45)
            self.sounds["level_up"] = self._make_chord([523, 659, 784, 1047], 0.8, 0.5)
            self.sounds["game_over"] = self._make_chord([392, 349, 330, 294], 1.0, 0.4)
            self.sounds["menu_select"] = self._make_beep(440, 0.1, "sine", 0.3)
            self.sounds["high_score"] = self._make_chord([784, 988, 1175, 1568], 1.2, 0.5)
           # self._generate_background_music()
        except Exception as e:
            print(f"Warning: could not create sounds: {e}")

    def _generate_background_music(self):
        sample_rate = 44100
        duration = 8.0
        frames = int(duration * sample_rate)
        notes = [261, 293, 329, 349, 392, 349, 329, 293]
        note_duration = duration / len(notes)
        melody = np.zeros(frames)
        for i, freq in enumerate(notes):
            start = int(i * note_duration * sample_rate)
            end = int((i + 1) * note_duration * sample_rate)
            segment_t = np.linspace(0, note_duration, end - start, endpoint=False)
            segment = np.sin(2 * np.pi * freq * segment_t) * 0.3
            segment += np.sin(2 * np.pi * freq * 1.5 * segment_t) * 0.15
            fade = int(0.05 * sample_rate)
            if len(segment) > 2 * fade:
                segment[:fade] *= np.linspace(0, 1, fade)
                segment[-fade:] *= np.linspace(1, 0, fade)
            melody[start:end] = segment
        melody = (melody * 0.4 * 32767).astype(np.int16)
        stereo = np.column_stack([melody, melody])
        import wave, io
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(stereo.tobytes())
        wav_buffer.seek(0)
        music_path = os.path.join(os.path.dirname(__file__), "..", "assets", "sounds", "bg_music.wav")
        os.makedirs(os.path.dirname(music_path), exist_ok=True)
        with open(music_path, 'wb') as f:
            f.write(wav_buffer.getvalue())
        self.music_path = music_path

    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].set_volume(self.volume)
            self.sounds[sound_name].play()

    def play_music(self):
        try:
            wav_path = os.path.join(os.path.dirname(__file__), "..", "assets", "sounds", "bg_music.wav")
            mp3_path = os.path.join(os.path.dirname(__file__), "..", "assets", "sounds", "bg_music.mp3")
            
            if os.path.exists(mp3_path):
                print("Загружаю MP3 файл")
                pygame.mixer.music.load(mp3_path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            elif os.path.exists(wav_path):
                print(" Загружаю WAV файл")
                pygame.mixer.music.load(wav_path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            else:
                print(" Файлы не найдены, создаю музыку...")
                self._generate_background_music()
                pygame.mixer.music.load(self.music_path)
                pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Ошибка загрузки музыки: {e}")
            print("Использую сгенерированную музыку...")
            self._generate_background_music()
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume * 0.5)
