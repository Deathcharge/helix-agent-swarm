# audio_generator.py – ψ-Linked Modulation Version (Browser Safe)
import numpy as np
import streamlit as st
import io
import soundfile as sf

class AudioEngine:
    def __init__(self, base_freq=136.1, harmonics=[432, 864]):
        self.base_freq = base_freq
        self.harmonics = harmonics
        self.sr = 44100  # Sample rate
        self.duration = 10  # Seconds
        self.volume = 0.4
        self.psi_mod = {"zoom": 1.0, "harmony": 0.5, "prana": 0.5}

    def set_modulation(self, zoom=1.0, harmony=0.5, prana=0.5):
        """Link ψ-field parameters to audio modulation."""
        self.psi_mod = {"zoom": zoom, "harmony": harmony, "prana": prana}

    def generate_wave(self, duration=None):
        if duration is None:
            duration = self.duration
        t = np.linspace(0, duration, int(self.sr * duration), False)

        # ψ-linked frequency modulation
        base = self.base_freq * (1 + 0.2 * (self.psi_mod["zoom"] - 1))
        harmony_factor = 1 + (self.psi_mod["harmony"] - 0.5)
        prana_factor = 1 + 0.3 * (self.psi_mod["prana"] - 0.5)

        wave = np.zeros_like(t)
        for f in [base * harmony_factor] + [h * prana_factor for h in self.harmonics]:
            wave += np.sin(2 * np.pi * f * t)

        # Normalize and apply volume
        wave = (wave / np.max(np.abs(wave))) * self.volume
        return wave

    def play_resonance(self, duration=10):
        """Generate and play ψ-modulated resonance tone."""
        wave = self.generate_wave(duration)
        buf = io.BytesIO()
        sf.write(buf, wave, self.sr, format='WAV')
        st.audio(buf.getvalue(), format="audio/wav")

    def stop(self):
        st.info("Audio playback stopped (browser controlled).")
