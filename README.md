# GensokyoDSP

[![license](https://img.shields.io/badge/license-MIT%2FApache--2.0-blue)](LICENSE-APACHE) <img src="https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white" />

> Current Status: 🚧 Early Development (Initial version in progress)

**GensokyoDSP** is a Rust-based **Procedural Audio Synthesis Tool**, designed to recreate the classic hardware sound sensations of the *Touhou Project* series (e.g., Roland SD-90 "Romantic Tp" / ZUNpet) in real-time via code.

This project is not a "player", but a **"Virtual Instrument Factory"**.

| English | Simplified Chinese          |
|---------|-----------------------------|
| English | [简体中文](./README_zh-Hans.md) |

## Introduction

### What is this?

Imagine a Touhou fan game where the ZUNpet timbre becomes brighter as a wave of bullets flies by, or rapidly shifts in texture the moment your character is hit. These are dynamic effects that are impossible to achieve by simply splicing static audio files.

**GensokyoDSP** is the tool that makes this possible. Instead of playing back static audio files, it generates authentic sounds on the fly using code, allowing for deep integration with game logic.

### Core Philosophy: Why not directly use WAV?

In traditional game development, music usually exists in the form of `.wav` or `.mp3`. This is like a **"Recording"** — the content is fixed and cannot be changed.

**GensokyoDSP** adopts a **"Real-time Rendering"** approach. This is like a **3D Model** in a game — it is alive and can deform at will according to the game state.

#### Traditional Audio vs. GensokyoDSP

| Feature           | Traditional Audio (WAV/MP3/SoundFont)                                             | GensokyoDSP (Procedural Synthesis)                                                                        |
|:------------------|:----------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------|
| **Essence**       | **Static Recording**<br>Like a photo, frozen the moment the shutter is pressed.   | **Dynamic Computation**<br>Like physics engine code, every millisecond of sound is calculated on the fly. |
| **Interactivity** | **Low**<br>Can only do simple volume adjustment or fade in/out.                   | **Fully Interactive**<br>Can change playing style, vibrato speed, or even melody and mode in real-time.   |
| **Storage**       | **Medium/Large**<br>Even old SoundFonts take MBs to hundreds of MBs.              | **Tiny**<br>Core algorithms are only a few KBs. We store the "Recipe", not the "Dish".                    |
| **Copyright**     | **High Risk**<br>Distributing original sample data (ROM) is in a legal gray area. | **None**<br>Reconstructed based on Physical Modeling, containing no original samples.                     |

> *Note: Although DSP consumes slightly more CPU power than playing samples directly, thanks to Rust's zero-cost abstractions and the efficient implementation of `fundsp`, this overhead is completely controllable on modern hardware.*

## Features

*   **True "Interactive Music"**: 
    *   **State Linkage**: When player lives decrease, the ZUNpet's blowing intensity can become more anxious, and the vibrato frequency can speed up.
    *   **Dynamic Arrangement**: Smoothly change harmony progression or BGM speed, or even modulate in real-time during Boss phase transitions, without hard-cutting audio.

*   **ZUNpet Acoustic Recreation**:
    *   We reconstructed the physical model of the Roland "Romantic Tp" via **Acoustic Reverse Engineering**.
    *   **Architecture**: Dual oscillator FM modulation + Dynamic Low Pass Filter + Air noise shaping.
    *   **Sound**: Perfectly restores the iconic "airy" attack and 6Hz vibrato details.

*   **Bevy Engine Native Support**:
    *   Designed for ECS architecture, audio synthesis runs in an independent Task Pool, not blocking the main game logic.
    *   Provides a simple API interface to spawn sounds just like spawning entities.

## How to Use

1.  **Add Dependency**:
    
    ```toml
    [dependencies]
    gensokyo_dsp = "0.1"
    ```

2.  **Future Plans: Bevy Integration**:

    *Note: The Bevy integration is currently under design and the following API is hypothetical.*

    ```rust
    // Planned Usage in a Bevy system
    fn spawn_bgm(mut commands: Commands, mut synth: ResMut<GensokyoSynth>) {
        // Start a ZUNpet instrument instance
        let zunpet_id = synth.spawn_instrument(InstrumentType::ZunPet);
        
        // Play a sequence
        synth.play_sequence(zunpet_id, "assets/midi/bad_apple.mid");
    }
    ```

## Contributing

**For Musicians & Arrangers**

If you are a musician or transcriber assisting this project, please note:
**The division of labor with program contributors is: Programmers build the "Instrument" (Code), and you write the "Score" (MIDI).**

Since this is a **Procedural Synthesizer**, it requires more precise MIDI data than a traditional DAW:

1.  **Clean Data**: Please provide standard MIDI files.
2.  **Expression Control**:
    *   Our synthesizer listens not only to pitch but also to **parameters**.
    *   Please draw **vibrato curves** in MIDI CC channels (e.g., Mod Wheel / CC1).
    *   Use **Velocity** to control the brightness of the timbre (Velocity > 100 triggers brighter overtones).
3.  **About "Fidelity"**:
    *   This is a virtual instrument based on physical rules; it has its own "temperament".
    *   If a note sounds wrong (e.g., attack is too slow), please tell me to adjust the **ADSR envelope parameters** in the code, rather than fixing the audio waveform.

**For Program Contributors**

If you are a Rust developer or DSP enthusiast, your contributions are welcome:

*   **DSP Optimization**: Improve the efficiency of the synthesis algorithms (utilizing `fundsp` or SIMD).
*   **New Instruments**: Help us reverse-engineer and implement more Touhou-style instruments (e.g., FM Bass, Synth Brass).
*   **Architecture**: Improve the bridging and real-time control interface with the Bevy engine.

## Tech Principles & Compliance

This project explores the physical essence of sound through **Code and Mathematical Formulas**.

1.  **Acoustic Reverse Modeling**:
    This project uses modern acoustic analysis tools (including **Sonic Charge Synplant 2**) as aids to estimate spectral characteristics and physical parameters (Parameter Estimation) from reference audio.
2.  **Clean-room Design**:
    *   All `.rs` source code is hand-written or generated based on general DSP algorithms.
    *   The project **does not contain** any binary data (ROM/Samples) from hardware manufacturers like Roland or Yamaha.
    *   The project **does not contain** any proprietary format files from Synplant 2. We only refer to the general physical parameters analyzed (e.g., frequency ratios, modulation indices).
3.  **Copyright Notice**:
    According to relevant legal conventions, the **logic of generating sound** (e.g., "Modulate Sine Wave B with Sine Wave A") is similar to a recipe or mathematical formula and does not fall under copyright protection. What this project open-sources is the "logic to generate sound", not the "sound recording itself".

## License

This project is licensed under either of

*   Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0))
*   MIT license ([LICENSE-MIT](LICENSE-MIT) or [http://opensource.org/licenses/MIT](http://opensource.org/licenses/MIT))

at your option.