from digitalio import DigitalInOut
from audioio import AudioOut
from audiomixer import Mixer

class AudioManager:
    """Manage audio output using a mixer."""

    def __init__(self, board, voice_count=3):
        # Enable the PyBadge speaker
        speaker_enable = DigitalInOut(board.SPEAKER_ENABLE)
        speaker_enable.switch_to_output(value=True)

        # Create audio output object
        self.audio = AudioOut(board.SPEAKER, quiescent_value=0)

        # Create audio mixer object
        self.voice_count = voice_count
        self.mixer = Mixer(
            voice_count=self.voice_count,
            sample_rate=22050,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True,
            buffer_size=6144,
        )
        self.audio.play(self.mixer)
        self.sounds = {}

    def load_sounds(self, sounds):
        """Store a dictionary mapping names to (voice_index, WaveFile)."""
        self.sounds = sounds

    def set_volume(self, volume):
        """Set mixer channel levels from 0-100 volume."""
        for i in range(self.voice_count):
            self.mixer.voice[i].level = volume / 100.0

    def play_sound(self, sound_name, loop=False):
        """Play a sound by name."""
        voice_index, sound_wav = self.sounds[sound_name]
        self.mixer.voice[voice_index].play(sound_wav, loop=loop)

    def stop_sound(self, sound_name):
        """Stop playback of a sound by name."""
        voice_index, _ = self.sounds[sound_name]
        self.mixer.voice[voice_index].stop()

    def end_sound(self, sound_name):
        """End playback of a looping sound by name."""
        voice_index, _ = self.sounds[sound_name]
        self.mixer.voice[voice_index].end()
