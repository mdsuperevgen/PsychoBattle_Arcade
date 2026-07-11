"""
Sound generation module for PsychoBattle Arcade.
Generates WAV audio files programmatically using sine waves — no external assets needed.
"""

import wave
import struct
import math
import os
import random
from typing import Optional

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

SAMPLE_RATE = 22050  # Lower sample rate = smaller files, fine for retro/game sounds
AMPLITUDE = 16000

# ── helpers ──────────────────────────────────────────────────────────


def _ensure_dir():
    os.makedirs(SOUNDS_DIR, exist_ok=True)


def _save_wav(filename: str, samples: list[int]):
    """Write a list of integer samples to a mono 16-bit WAV file."""
    _ensure_dir()
    path = os.path.join(SOUNDS_DIR, filename)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return path


def _sine_wave(freq: float, duration: float, amp: float = AMPLITUDE) -> list[int]:
    n = int(SAMPLE_RATE * duration)
    return [int(amp * math.sin(2 * math.pi * freq * t / SAMPLE_RATE)) for t in range(n)]


def _square_wave(freq: float, duration: float, amp: float = AMPLITUDE) -> list[int]:
    n = int(SAMPLE_RATE * duration)
    return [int(amp * (1 if math.sin(2 * math.pi * freq * t / SAMPLE_RATE) > 0 else -1)) for t in range(n)]


def _saw_wave(freq: float, duration: float, amp: float = AMPLITUDE) -> list[int]:
    """Sawtooth wave - rich in harmonics, good for bass."""
    n = int(SAMPLE_RATE * duration)
    return [int(amp * (2 * (freq * t / SAMPLE_RATE - math.floor(freq * t / SAMPLE_RATE + 0.5)))) for t in range(n)]


def _triangle_wave(freq: float, duration: float, amp: float = AMPLITUDE) -> list[int]:
    """Triangle wave - softer, hollow sound."""
    n = int(SAMPLE_RATE * duration)
    out = []
    for t in range(n):
        phase = (freq * t / SAMPLE_RATE) % 1.0
        val = 2 * abs(2 * phase - 1) - 1
        out.append(int(amp * val))
    return out


def _noise(duration: float, amp: float = AMPLITUDE) -> list[int]:
    n = int(SAMPLE_RATE * duration)
    return [int(random.uniform(-amp, amp)) for _ in range(n)]


def _envelope(samples: list[int], attack: float = 0.02, release: float = 0.05) -> list[int]:
    """Apply a simple ADSR-like envelope."""
    n = len(samples)
    a = int(SAMPLE_RATE * attack)
    r = int(SAMPLE_RATE * release)
    out = samples[:]
    for i in range(min(a, n)):
        out[i] = int(out[i] * (i / a))
    for i in range(max(0, n - r), n):
        out[i] = int(out[i] * ((n - i) / r))
    return out


def _mix(*tracks: list[int]) -> list[int]:
    """Sum multiple sample lists of the same length, clipped to 16-bit range."""
    length = max(len(t) for t in tracks) if tracks else 0
    result = [0] * length
    for track in tracks:
        for i, v in enumerate(track):
            result[i] += v
    return [max(-32768, min(32767, s)) for s in result]


def _make_loopable(samples: list[int], fade_ms: float = 20) -> list[int]:
    """Apply fade-in at start and fade-out at end so loop boundaries are seamless."""
    n = len(samples)
    fade_n = int(SAMPLE_RATE * fade_ms / 1000)
    fade_n = min(fade_n, n // 4)
    out = samples[:]
    for i in range(fade_n):
        out[i] = int(out[i] * (i / fade_n))
    for i in range(fade_n):
        out[n - 1 - i] = int(out[n - 1 - i] * (i / fade_n))
    return out


def _pad(samples: list[int], total_duration: float, side: str = "right") -> list[int]:
    """Pad samples with silence to reach total_duration seconds."""
    needed = int(SAMPLE_RATE * total_duration) - len(samples)
    if needed <= 0:
        return samples
    silence = [0] * needed
    if side == "right":
        return samples + silence
    else:
        return silence + samples


# ── musical helpers ──────────────────────────────────────────────────

NOTES = {
    'C2': 65, 'Cs2': 69, 'D2': 73, 'Ds2': 78, 'E2': 82, 'F2': 87, 'Fs2': 93, 'G2': 98, 'Gs2': 104, 'A2': 110, 'As2': 117, 'B2': 123,
    'C3': 131, 'Cs3': 139, 'D3': 147, 'Ds3': 156, 'E3': 165, 'F3': 175, 'Fs3': 185, 'G3': 196, 'Gs3': 208, 'A3': 220, 'As3': 233, 'B3': 247,
    'C4': 262, 'Cs4': 277, 'D4': 294, 'Ds4': 311, 'E4': 330, 'F4': 349, 'Fs4': 370, 'G4': 392, 'Gs4': 415, 'A4': 440, 'As4': 466, 'B4': 494,
    'C5': 523, 'Cs5': 554, 'D5': 587, 'Ds5': 622, 'E5': 659, 'F5': 698, 'Fs5': 740, 'G5': 784, 'Gs5': 831, 'A5': 880, 'As5': 932, 'B5': 988,
    'C6': 1047, 'Cs6': 1109, 'D6': 1175, 'Ds6': 1245, 'E6': 1319, 'F6': 1397, 'Fs6': 1480, 'G6': 1568, 'Gs6': 1661, 'A6': 1760, 'As6': 1865, 'B6': 1976,
}


def _chord(notes: list[float], duration: float, amp: float = AMPLITUDE, wave: str = 'sine') -> list[int]:
    """Generate a chord from a list of frequencies."""
    parts = []
    for f in notes:
        if wave == 'sine':
            parts.append(_sine_wave(f, duration, amp / len(notes)))
        elif wave == 'square':
            parts.append(_square_wave(f, duration, amp / len(notes)))
        elif wave == 'saw':
            parts.append(_saw_wave(f, duration, amp / len(notes)))
        elif wave == 'triangle':
            parts.append(_triangle_wave(f, duration, amp / len(notes)))
        else:
            parts.append(_sine_wave(f, duration, amp / len(notes)))
    return _mix(*parts) if parts else []


def _bass_line(notes: list[tuple[float, float]], amp: float = AMPLITUDE, wave: str = 'saw') -> list[int]:
    """Simple bass line from (freq, duration) pairs."""
    result = []
    for freq, dur in notes:
        b = _square_wave(freq, dur, amp) if wave == 'square' else _saw_wave(freq, dur, amp)
        b = _envelope(b, 0.02, 0.1)
        result.extend(b)
    return result


def _melody(notes: list[tuple[float, float]], amp: float = AMPLITUDE) -> list[int]:
    """Simple monophonic melody from (freq, duration) pairs."""
    result = []
    for freq, dur in notes:
        seg = _sine_wave(freq, dur, amp * 0.8)
        seg = _envelope(seg, 0.01, 0.08)
        result.extend(seg)
    return result


def _kick(dur: float = 0.2, amp: float = AMPLITUDE) -> list[int]:
    """808-style kick drum."""
    n = int(SAMPLE_RATE * dur)
    out = []
    for t in range(n):
        freq = 150 * (1 - t / n) + 40
        env = (1 - t / n) ** 2
        val = math.sin(2 * math.pi * freq * t / SAMPLE_RATE) * env
        out.append(int(amp * 0.8 * val))
    return out


def _snare(dur: float = 0.15, amp: float = AMPLITUDE) -> list[int]:
    """Snare drum - noise + tone."""
    n = int(SAMPLE_RATE * dur)
    noise_part = _noise(dur, amp * 0.6)
    tone_part = _sine_wave(200, dur, amp * 0.4)
    snare = _mix(noise_part, tone_part)
    return _envelope(snare, 0.002, 0.08)


def _hihat(dur: float = 0.05, amp: float = AMPLITUDE, closed: bool = True) -> list[int]:
    """Hi-hat from filtered noise."""
    hi = _noise(dur, amp * 0.5)
    hi = _envelope(hi, 0.001, 0.02 if closed else 0.06)
    return hi


def _drum_pattern(bpm: float, beats: int, pattern: list[str], amp: float = AMPLITUDE) -> list[int]:
    """Generate a drum pattern. K=kick, S=snare, H=hihat, h=open hihat, .=rest"""
    beat_samples = int(SAMPLE_RATE * 60.0 / bpm)
    result = [0] * (beat_samples * beats)
    for i, p in enumerate(pattern[:beats]):
        pos = i * beat_samples
        if p == 'K':
            k = _kick(0.2, amp)
            for j, v in enumerate(k):
                if pos + j < len(result):
                    result[pos + j] += v
        elif p == 'S':
            s = _snare(0.15, amp)
            for j, v in enumerate(s):
                if pos + j < len(result):
                    result[pos + j] += v
        elif p == 'H':
            h = _hihat(0.05, amp, True)
            for j, v in enumerate(h):
                if pos + j < len(result):
                    result[pos + j] += v
        elif p == 'h':
            h = _hihat(0.15, amp, False)
            for j, v in enumerate(h):
                if pos + j < len(result):
                    result[pos + j] += v
    return [max(-32768, min(32767, s)) for s in result]


def _pad_drone(notes: list[float], duration: float, amp: float = AMPLITUDE) -> list[int]:
    """Slow evolving pad with beating."""
    n = int(SAMPLE_RATE * duration)
    out = [0] * n
    for f in notes:
        for t in range(n):
            val = math.sin(2 * math.pi * f * t / SAMPLE_RATE)
            out[t] += int(amp / len(notes) * 0.6 * val)
    for t in range(n):
        lfo = 0.7 + 0.3 * math.sin(2 * math.pi * 0.25 * t / SAMPLE_RATE)
        out[t] = int(out[t] * lfo)
    return [max(-32768, min(32767, s)) for s in out]


def _arpeggio(notes: list[float], dur_per_note: float, total_dur: float, amp: float = AMPLITUDE) -> list[int]:
    """Rapid arpeggio sequence looping through notes."""
    result = []
    total_n = int(SAMPLE_RATE * total_dur)
    note_n = int(SAMPLE_RATE * dur_per_note)
    idx = 0
    while len(result) < total_n:
        f = notes[idx % len(notes)]
        seg = _sine_wave(f, dur_per_note, amp * 0.5)
        seg = _envelope(seg, 0.005, 0.02)
        for v in seg:
            if len(result) < total_n:
                result.append(v)
        idx += 1
    return result


# ── generated file paths ─────────────────────────────────────────────

ALL_FILES: dict[str, str] = {}


def _register(name: str, filename: str):
    ALL_FILES[name] = filename
    return filename


# ══════════════════════════════════════════════════════════════════════
#  MUSIC TRACKS  (16-20 second loops with melody, bass, rhythm, pads)
# ══════════════════════════════════════════════════════════════════════


def _gen_level1_zoo():
    """Gentle forest ambience — C major, calm melody, bird chirps."""
    bpm = 100
    beat = 60.0 / bpm
    total_beats = 32
    dur = total_beats * beat

    pad = _pad_drone([NOTES['C4'], NOTES['E4'], NOTES['G4'], NOTES['G3']], dur, AMPLITUDE * 0.5)
    bass = _bass_line([
        (NOTES['C3'], beat * 4), (NOTES['G2'], beat * 4),
        (NOTES['A2'], beat * 4), (NOTES['F2'], beat * 4),
        (NOTES['C3'], beat * 4), (NOTES['E2'], beat * 4),
        (NOTES['D3'], beat * 4), (NOTES['G2'], beat * 4),
    ], AMPLITUDE * 0.45, 'square')
    melody = _melody([
        (NOTES['E4'], beat * 1), (NOTES['G4'], beat * 1), (NOTES['A4'], beat * 2),
        (NOTES['G4'], beat * 1), (NOTES['E4'], beat * 1), (NOTES['D4'], beat * 2),
        (NOTES['C4'], beat * 2), (NOTES['D4'], beat * 1), (NOTES['E4'], beat * 1),
        (NOTES['G4'], beat * 2), (NOTES['A4'], beat * 2),
        (NOTES['G4'], beat * 1), (NOTES['E4'], beat * 1), (NOTES['D4'], beat * 1), (NOTES['C4'], beat * 1),
        (NOTES['E4'], beat * 1), (NOTES['G4'], beat * 1), (NOTES['A4'], beat * 2),
        (NOTES['C5'], beat * 1), (NOTES['A4'], beat * 1), (NOTES['G4'], beat * 2),
        (NOTES['E4'], beat * 2), (NOTES['D4'], beat * 2), (NOTES['C4'], beat * 2),
    ], AMPLITUDE * 0.35)
    drum = _drum_pattern(bpm, total_beats, ['K', '.', '.', '.', 'K', '.', '.', '.'] * 4, AMPLITUDE * 0.3)
    n = int(SAMPLE_RATE * dur)
    nature = [0] * n
    for _ in range(16):
        pos = random.randint(0, n - int(SAMPLE_RATE * 0.3))
        f = random.choice([880, 990, 1100, 1320])
        chirp = _sine_wave(f, 0.12, AMPLITUDE * 0.2)
        chirp = _envelope(chirp, 0.01, 0.06)
        for j, v in enumerate(chirp):
            if pos + j < n:
                nature[pos + j] += v
    return _save_wav(_register("level1", "level1_zoo.wav"), _make_loopable(_mix(pad, bass, melody, drum, nature)))


def _gen_level2_ocean():
    """Deep ocean ambient — slow evolving drone with water-like texture."""
    bpm = 70
    beat = 60.0 / bpm
    total_beats = 24
    dur = total_beats * beat

    drone = _pad_drone([NOTES['D2'], NOTES['A2'], NOTES['D3'], NOTES['F3']], dur, AMPLITUDE * 0.6)
    n = int(SAMPLE_RATE * dur)
    pulse = [0] * n
    for t in range(n):
        lfo = 0.5 + 0.5 * math.sin(2 * math.pi * 0.1 * t / SAMPLE_RATE)
        f = 55 + 10 * math.sin(2 * math.pi * 0.05 * t / SAMPLE_RATE)
        val = math.sin(2 * math.pi * f * t / SAMPLE_RATE) * lfo * 0.5
        pulse[t] = int(AMPLITUDE * 0.5 * val)
    water = [0] * n
    for _ in range(24):
        pos = random.randint(0, n - int(SAMPLE_RATE * 0.5))
        bw = _noise(0.4, AMPLITUDE * 0.15)
        bw = _envelope(bw, 0.05, 0.2)
        for j, v in enumerate(bw):
            if pos + j < n:
                water[pos + j] += v
    shimmer = [0] * n
    for _ in range(12):
        pos = random.randint(0, n - int(SAMPLE_RATE * 0.5))
        f = random.choice([1800, 2200, 2600])
        sh = _sine_wave(f, 0.3, AMPLITUDE * 0.1)
        sh = _envelope(sh, 0.1, 0.15)
        for j, v in enumerate(sh):
            if pos + j < n:
                shimmer[pos + j] += v
    return _save_wav(_register("level2", "level2_ocean.wav"), _make_loopable(_mix(drone, pulse, water, shimmer)))


def _gen_level3_medical():
    """Clinical tension — minor key, heartbeat rhythm, sterile beeps."""
    bpm = 80
    beat = 60.0 / bpm
    total_beats = 24
    dur = total_beats * beat

    pad = _pad_drone([NOTES['D3'], NOTES['F3'], NOTES['Gs3'], NOTES['C4']], dur, AMPLITUDE * 0.4)
    drum = _drum_pattern(bpm, total_beats, ['K', '.', '.', '.', 'K', '.', '.', '.'] * 3, AMPLITUDE * 0.5)
    n = int(SAMPLE_RATE * dur)
    beeps = [0] * n
    for bi in [0, 4, 8, 12, 16, 20]:
        for offset in [0, 0.5, 2, 2.5]:
            pos = int((bi + offset) * beat * SAMPLE_RATE)
            if pos >= n:
                continue
            f = random.choice([880, 1100, 1320])
            beep = _sine_wave(f, 0.06, AMPLITUDE * 0.3)
            beep = _envelope(beep, 0.005, 0.02)
            for j, v in enumerate(beep):
                if pos + j < n:
                    beeps[pos + j] += v
    rumble = [0] * n
    for t in range(n):
        f = 45 + 5 * math.sin(2 * math.pi * 0.3 * t / SAMPLE_RATE)
        val = math.sin(2 * math.pi * f * t / SAMPLE_RATE)
        env = 0.3 + 0.2 * math.sin(2 * math.pi * 0.15 * t / SAMPLE_RATE)
        rumble[t] = int(AMPLITUDE * 0.3 * val * env)
    return _save_wav(_register("level3", "level3_medical.wav"), _make_loopable(_mix(pad, drum, beeps, rumble)))


def _gen_level4_city():
    """Urban groove — steady beat, walking bass, city vibes."""
    bpm = 115
    beat = 60.0 / bpm
    total_beats = 32
    dur = total_beats * beat

    drums = _drum_pattern(bpm, total_beats, ['K', '.', 'S', '.', 'K', '.', 'S', '.'] * 4, AMPLITUDE * 0.6)
    hats = _drum_pattern(bpm, total_beats, ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'] * 4, AMPLITUDE * 0.2)
    bass = _bass_line([
        (NOTES['D2'], beat * 2), (NOTES['F2'], beat * 2),
        (NOTES['A2'], beat * 2), (NOTES['C3'], beat * 2),
        (NOTES['D3'], beat * 2), (NOTES['A2'], beat * 2),
        (NOTES['F2'], beat * 2), (NOTES['D2'], beat * 2),
        (NOTES['G2'], beat * 2), (NOTES['As2'], beat * 2),
        (NOTES['D3'], beat * 2), (NOTES['G2'], beat * 2),
        (NOTES['A2'], beat * 2), (NOTES['C3'], beat * 2),
        (NOTES['E3'], beat * 2), (NOTES['A2'], beat * 2),
    ], AMPLITUDE * 0.5)
    n = int(SAMPLE_RATE * dur)
    stabs = [0] * n
    for bi, chord_notes in [
        (0, [NOTES['D4'], NOTES['F4'], NOTES['A4']]),
        (8, [NOTES['D4'], NOTES['F4'], NOTES['A4']]),
        (16, [NOTES['G4'], NOTES['As4'], NOTES['D5']]),
        (24, [NOTES['D4'], NOTES['F4'], NOTES['A4']]),
    ]:
        pos = int(bi * beat * SAMPLE_RATE)
        c = _chord(chord_notes, beat * 2, AMPLITUDE * 0.25, 'triangle')
        for j, v in enumerate(c):
            if pos + j < n:
                stabs[pos + j] += v
    return _save_wav(_register("level4", "level4_city.wav"), _make_loopable(_mix(drums, hats, bass, stabs)))


def _gen_level5_abstract():
    """Anxious dissonance — unsettling but musical, minor seconds, tremolo."""
    bpm = 90
    beat = 60.0 / bpm
    total_beats = 24
    dur = total_beats * beat

    pad1 = _pad_drone([NOTES['C3'], NOTES['Cs3'], NOTES['G3'], NOTES['C4']], dur, AMPLITUDE * 0.35)
    pad2 = _pad_drone([NOTES['Fs3'], NOTES['A3'], NOTES['C4'], NOTES['Ds4']], dur / 2, AMPLITUDE * 0.3)
    pad2_full = pad2 + pad2
    n = int(SAMPLE_RATE * dur)
    trem = [0] * n
    for t in range(n):
        f = 130 + 10 * math.sin(2 * math.pi * 0.2 * t / SAMPLE_RATE)
        tremolo = 0.5 + 0.5 * math.sin(2 * math.pi * 6 * t / SAMPLE_RATE)
        val = math.sin(2 * math.pi * f * t / SAMPLE_RATE) * tremolo
        trem[t] = int(AMPLITUDE * 0.3 * val)
    glitch = [0] * n
    for _ in range(20):
        pos = random.randint(0, n - int(SAMPLE_RATE * 0.15))
        g = _noise(0.08, AMPLITUDE * 0.25)
        g = _envelope(g, 0.002, 0.04)
        for j, v in enumerate(g):
            if pos + j < n:
                glitch[pos + j] += v
    return _save_wav(_register("level5", "level5_abstract.wav"), _make_loopable(_mix(pad1, pad2_full, trem, glitch)))


def _gen_level6_void():
    """Empty sparse drone — long silences, lonely tones, wind."""
    bpm = 50
    beat = 60.0 / bpm
    total_beats = 20
    dur = total_beats * beat
    n = int(SAMPLE_RATE * dur)

    drone = [0] * n
    for t in range(n):
        f = 50 + 5 * math.sin(2 * math.pi * 0.03 * t / SAMPLE_RATE)
        amp_env = 0.3 + 0.2 * math.sin(2 * math.pi * 0.08 * t / SAMPLE_RATE)
        val = math.sin(2 * math.pi * f * t / SAMPLE_RATE) * amp_env
        drone[t] = int(AMPLITUDE * 0.3 * val)
    wind = _noise(dur, AMPLITUDE * 0.08)
    for t in range(n):
        wind[t] = int(wind[t] * (0.2 + 0.8 * (0.5 + 0.5 * math.sin(2 * math.pi * 0.05 * t / SAMPLE_RATE))))
    chimes = [0] * n
    for _ in range(6):
        pos = random.randint(0, n - int(SAMPLE_RATE * 1.0))
        f = random.choice([900, 1100, 1300, 1600])
        ch = _sine_wave(f, 0.5, AMPLITUDE * 0.08)
        ch = _envelope(ch, 0.1, 0.3)
        for j, v in enumerate(ch):
            if pos + j < n:
                chimes[pos + j] += v
    return _save_wav(_register("level6", "level6_void.wav"), _make_loopable(_mix(drone, wind, chimes)))


def _gen_level7_tech():
    """Electronic sci-fi — arpeggios, digital bass, robotic rhythm."""
    bpm = 132
    beat = 60.0 / bpm
    total_beats = 32
    dur = total_beats * beat

    drums = _drum_pattern(bpm, total_beats,
                          ['K', '.', '.', '.', 'K', '.', '.', '.',
                           'K', '.', 'S', '.', 'K', '.', 'S', '.'] * 2, AMPLITUDE * 0.5)
    hats = _drum_pattern(bpm, total_beats, ['H', '.', 'H', '.', 'H', '.', 'H', '.'] * 4, AMPLITUDE * 0.15)
    bass = _bass_line([
        (NOTES['E2'], beat * 4), (NOTES['G2'], beat * 2), (NOTES['A2'], beat * 2),
        (NOTES['B2'], beat * 4), (NOTES['A2'], beat * 2), (NOTES['G2'], beat * 2),
        (NOTES['E2'], beat * 4), (NOTES['G2'], beat * 2), (NOTES['A2'], beat * 2),
        (NOTES['B2'], beat * 4), (NOTES['E3'], beat * 4),
    ], AMPLITUDE * 0.45)
    arp = _arpeggio([NOTES['E4'], NOTES['G4'], NOTES['A4'], NOTES['B4'], NOTES['D5']],
                    0.06, dur, AMPLITUDE * 0.25)
    n = int(SAMPLE_RATE * dur)
    beeps = [0] * n
    for i in range(16):
        pos = int(i * 2 * beat * SAMPLE_RATE)
        if pos >= n:
            continue
        f = random.choice([440, 660, 880, 1100, 1320])
        beep = _sine_wave(f, 0.05, AMPLITUDE * 0.2)
        beep = _envelope(beep, 0.002, 0.01)
        for j, v in enumerate(beep):
            if pos + j < n:
                beeps[pos + j] += v
    return _save_wav(_register("level7", "level7_tech.wav"), _make_loopable(_mix(drums, hats, bass, arp, beeps)))


def _gen_level8_cosmic():
    """Ethereal space — swirling pads, twinkling stars, wonder."""
    bpm = 60
    beat = 60.0 / bpm
    total_beats = 16
    dur = total_beats * beat

    pad = _pad_drone([NOTES['C3'], NOTES['E3'], NOTES['G3'], NOTES['B3'], NOTES['D4']], dur, AMPLITUDE * 0.5)
    n = int(SAMPLE_RATE * dur)
    pad2_data = _pad_drone([NOTES['Cs4'], NOTES['F4'], NOTES['Gs4']], dur, AMPLITUDE * 0.25)
    stars = [0] * n
    for _ in range(20):
        pos = random.randint(0, n - int(SAMPLE_RATE * 0.5))
        f = random.choice([1200, 1500, 1800, 2200, 2600, 3000])
        star = _sine_wave(f, 0.2, AMPLITUDE * 0.12)
        star = _envelope(star, 0.02, 0.1)
        for j, v in enumerate(star):
            if pos + j < n:
                stars[pos + j] += v
    whoosh = _noise(dur, AMPLITUDE * 0.06)
    for t in range(n):
        lfo = 0.5 * (0.5 + 0.5 * math.sin(2 * math.pi * 0.08 * t / SAMPLE_RATE))
        whoosh[t] = int(whoosh[t] * lfo)
    return _save_wav(_register("level8", "level8_cosmic.wav"), _make_loopable(_mix(pad, pad2_data, stars, whoosh)))


def _gen_level9_myth():
    """Epic ancient — brass-like tones, powerful drums, heroic."""
    bpm = 80
    beat = 60.0 / bpm
    total_beats = 32
    dur = total_beats * beat

    drums = _drum_pattern(bpm, total_beats,
                          ['K', '.', 'S', '.', 'K', '.', 'S', '.',
                           'K', '.', 'S', '.', 'K', '.', 'K', '.'] * 2, AMPLITUDE * 0.7)
    brass = _pad_drone([NOTES['D2'], NOTES['A2'], NOTES['D3'], NOTES['F3']], dur, AMPLITUDE * 0.45)
    melody = _melody([
        (NOTES['D4'], beat * 2), (NOTES['F4'], beat * 1), (NOTES['G4'], beat * 1),
        (NOTES['A4'], beat * 2), (NOTES['G4'], beat * 1), (NOTES['F4'], beat * 1),
        (NOTES['D4'], beat * 2), (NOTES['A3'], beat * 2),
        (NOTES['C4'], beat * 2), (NOTES['D4'], beat * 1), (NOTES['E4'], beat * 1),
        (NOTES['F4'], beat * 2), (NOTES['G4'], beat * 2),
        (NOTES['A4'], beat * 2), (NOTES['G4'], beat * 1), (NOTES['F4'], beat * 1),
        (NOTES['E4'], beat * 2), (NOTES['D4'], beat * 2),
    ], AMPLITUDE * 0.35)
    n = int(SAMPLE_RATE * dur)
    taiko = [0] * n
    for bi in [0, 4, 8, 12, 16, 20, 24, 28]:
        pos = int(bi * beat * SAMPLE_RATE)
        t = _sine_wave(70, 0.3, AMPLITUDE * 0.3)
        t = _envelope(t, 0.01, 0.2)
        for j, v in enumerate(t):
            if pos + j < n:
                taiko[pos + j] += v
    return _save_wav(_register("level9", "level9_myth.wav"), _make_loopable(_mix(drums, brass, melody, taiko)))


def _gen_level10_xeno():
    """Alien eerie — microtonal, glissandos, strange beauty."""
    bpm = 72
    beat = 60.0 / bpm
    total_beats = 24
    dur = total_beats * beat
    n = int(SAMPLE_RATE * dur)

    pad = [0] * n
    for t in range(n):
        f1 = 180 + 20 * math.sin(2 * math.pi * 0.12 * t / SAMPLE_RATE)
        f2 = 225 + 15 * math.sin(2 * math.pi * 0.08 * t / SAMPLE_RATE)
        f3 = 270 + 25 * math.sin(2 * math.pi * 0.1 * t / SAMPLE_RATE)
        val = (math.sin(2 * math.pi * f1 * t / SAMPLE_RATE) * 0.4 +
               math.sin(2 * math.pi * f2 * t / SAMPLE_RATE) * 0.3 +
               math.sin(2 * math.pi * f3 * t / SAMPLE_RATE) * 0.3)
        pad[t] = int(AMPLITUDE * 0.35 * val)

    gliss = [0] * n
    for _ in range(8):
        pos = random.randint(0, n - int(SAMPLE_RATE * 1.5))
        start_f = random.choice([200, 300, 400, 600])
        end_f = start_f * random.choice([1.5, 2.0, 0.5, 0.75])
        sweep_n = min(int(SAMPLE_RATE * random.uniform(0.5, 1.2)), n - pos)
        for i in range(sweep_n):
            frac = i / sweep_n
            f = start_f + (end_f - start_f) * frac
            env = math.sin(math.pi * frac)
            val = math.sin(2 * math.pi * f * i / SAMPLE_RATE) * env
            if pos + i < n:
                gliss[pos + i] += int(AMPLITUDE * 0.15 * val)

    pings = [0] * n
    for _ in range(16):
        pos = random.randint(0, n - int(SAMPLE_RATE * 0.3))
        f = random.choice([600, 800, 1100, 1400, 1700, 2100])
        p = _sine_wave(f, 0.12, AMPLITUDE * 0.2)
        p = _envelope(p, 0.01, 0.06)
        for j, v in enumerate(p):
            if pos + j < n:
                pings[pos + j] += v

    pulse = [0] * n
    for t in range(n):
        p = 0.5 + 0.5 * math.sin(2 * math.pi * 1.5 * t / SAMPLE_RATE)
        f = 40 + 10 * math.sin(2 * math.pi * 0.2 * t / SAMPLE_RATE)
        val = math.sin(2 * math.pi * f * t / SAMPLE_RATE) * p
        pulse[t] = int(AMPLITUDE * 0.3 * val)
    return _save_wav(_register("level10", "level10_xeno.wav"), _make_loopable(_mix(pad, gliss, pings, pulse)))


# ── SFX ──────────────────────────────────────────────────────────────


def _gen_shoot():
    """Short subdued pew — quick sine burst with fast decay."""
    dur = 0.1
    s = _sine_wave(600, dur, AMPLITUDE * 0.9)
    s = _envelope(s, 0.002, 0.05)
    return _save_wav(_register("shoot", "shoot.wav"), s)


def _gen_laser():
    """Laser beam zing."""
    dur = 0.15
    n = int(SAMPLE_RATE * dur)
    s = []
    for t in range(n):
        freq = 800 + 4000 * (t / n)
        val = math.sin(2 * math.pi * freq * t / SAMPLE_RATE)
        s.append(int(AMPLITUDE * 0.9 * (1 - t / n)))
    return _save_wav(_register("laser", "laser.wav"), s)


def _gen_hit():
    """Short impact thud."""
    dur = 0.12
    n = int(SAMPLE_RATE * dur)
    s = []
    for t in range(n):
        val = (math.sin(2 * math.pi * 100 * t / SAMPLE_RATE) +
               random.uniform(-0.3, 0.3)) * (1 - t / n)
        s.append(int(AMPLITUDE * 0.9 * val))
    return _save_wav(_register("hit", "hit.wav"), s)


def _gen_explosion():
    """Boom / explosion."""
    dur = 0.4
    n = int(SAMPLE_RATE * dur)
    s = []
    for t in range(n):
        val = (math.sin(2 * math.pi * 50 * t / SAMPLE_RATE) +
               random.uniform(-0.5, 0.5) * (1 - t / n * 0.5)) * (1 - t / n)
        s.append(int(AMPLITUDE * 0.95 * val))
    return _save_wav(_register("explosion", "explosion.wav"), s)


def _gen_powerup():
    """Cheerful ascending tone."""
    dur = 0.3
    n = int(SAMPLE_RATE * dur)
    s = []
    for t in range(n):
        freq = 400 + 800 * (t / n)
        val = math.sin(2 * math.pi * freq * t / SAMPLE_RATE)
        s.append(int(AMPLITUDE * 0.9 * (1 - t / n)))
    return _save_wav(_register("powerup", "powerup.wav"), s)


def _gen_boss_warning():
    """Low ominous rumble."""
    dur = 1.0
    n = int(SAMPLE_RATE * dur)
    s = []
    for t in range(n):
        f = 60 + 20 * math.sin(2 * math.pi * 4 * t / SAMPLE_RATE)
        val = math.sin(2 * math.pi * f * t / SAMPLE_RATE) * (0.5 + 0.5 * math.sin(2 * math.pi * 2 * t / SAMPLE_RATE))
        s.append(int(AMPLITUDE * 0.8 * val))
    return _save_wav(_register("boss_warning", "boss_warning.wav"), s)


def _gen_victory():
    """Fanfare."""
    dur = 1.5
    n = int(SAMPLE_RATE * dur)
    s = []
    notes = [440, 554, 659, 880]
    note_len = n // len(notes)
    for i, f in enumerate(notes):
        for t in range(note_len):
            idx = i * note_len + t
            if idx >= n:
                break
            env = t / note_len if t < note_len * 0.1 else (1 - t / note_len) if t > note_len * 0.8 else 1.0
            val = math.sin(2 * math.pi * f * t / SAMPLE_RATE) * env
            s.append(int(AMPLITUDE * 0.9 * val))
    while len(s) < n:
        s.append(0)
    return _save_wav(_register("victory", "victory.wav"), s)


# ══════════════════════════════════════════════════════════════════════
#  GENERATE ALL
# ══════════════════════════════════════════════════════════════════════

_LEVEL_GENERATORS = [
    _gen_level1_zoo,
    _gen_level2_ocean,
    _gen_level3_medical,
    _gen_level4_city,
    _gen_level5_abstract,
    _gen_level6_void,
    _gen_level7_tech,
    _gen_level8_cosmic,
    _gen_level9_myth,
    _gen_level10_xeno,
]

_SFX_GENERATORS = [
    _gen_shoot,
    _gen_laser,
    _gen_hit,
    _gen_explosion,
    _gen_powerup,
    _gen_boss_warning,
    _gen_victory,
]


def generate_all():
    """Generate all sound files. Safe to call multiple times."""
    for gen in _LEVEL_GENERATORS:
        gen()
    for gen in _SFX_GENERATORS:
        gen()


def get_path(name: str) -> str:
    """Get the full path to a named sound file."""
    if name in ALL_FILES:
        return os.path.join(SOUNDS_DIR, ALL_FILES[name])
    return ""


# ── auto-generate on import ──────────────────────────────────────────
# Sounds are generated explicitly via generate_all() in main.py
# Module-level generation disabled for pygbag compatibility
