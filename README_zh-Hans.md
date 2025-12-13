# GensokyoDSP

[![license](https://img.shields.io/badge/license-MIT%2FApache--2.0-blue)](LICENSE-APACHE) <img src="https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white" />

> 当前状态: 🚧 早期开发中 (Initial version in progress)

**GensokyoDSP** 是一个基于 Rust 的**程序化音频合成工具 (Procedural Audio Synthesis Tool)**，旨在通过代码实时重现《东方 Project》系列中经典的硬件音源听感（如 Roland SD-90 "Romantic Tp" / ZUN号）。

本项目不是一个“播放器”，而是一个**“虚拟乐器构造厂”**。

| English                | Simplified Chinese |
|------------------------|--------------------|
| [English](./README.md) | 简体中文               |

## 简介

### 这是什么？

想象一下，在一个东方 Project 同人游戏中，ZUN 号的音色在弹幕飞过时变得明亮，或者在角色被击中时音色迅速发生转变。这些是传统音频剪辑拼凑无法实现的绝妙效果。

**GensokyoDSP** 就是实现这一目标的工具。它不是播放静态的音频文件，而是通过代码即时生成原汁原味的声音，允许音乐与游戏逻辑深度融合。

### 核心理念：为什么不直接用 WAV？

在传统的游戏开发中，音乐通常以 `.wav` 或 `.mp3` 的形式存在。这就像是**“录像”**——内容是固定的，无法改变。

而 **GensokyoDSP** 采用的是**“实时渲染”**的方式。这就像是游戏里的 **3D 模型**——它是活的，可以根据游戏状态随意变形。

#### 传统音频 vs. 本项目 (DSP)

| 特性       | 传统音频 (WAV/MP3/SoundFont)                    | GensokyoDSP (程序化合成)                                   |
|:---------|:--------------------------------------------|:------------------------------------------------------|
| **本质**   | **静态录音 (Recording)**<br>就像一张照片，按下快门那一刻就定格了。 | **动态计算 (Computation)**<br>就像一段物理引擎代码，每一毫秒的声音都是现场算出来的。 |
| **互动性**  | **低**<br>只能做简单的音量调节或淡入淡出。                   | **极高 (Fully Interactive)**<br>可以改变演奏法、颤音速度、甚至改变旋律和调式。 |
| **存储体积** | **中/大**<br>即使是老式 SoundFont 也要数 MB 到数百 MB。   | **微小**<br>核心算法仅几十 KB。我们存的是“配方”，不是“成品菜”。               |
| **版权风险** | **高**<br>分发原厂采样数据（ROM）存在法律灰色地带。             | **无**<br>基于物理建模（Physical Modeling）重构，不包含任何原始采样。       |

> *注：虽然 DSP 会比直接播放采样消耗略多的 CPU 算力，但得益于 Rust 的零成本抽象与 `fundsp` 的高效实现，这种开销在现代硬件上是完全可控的。*

## 核心特性

*   **真正的“互动音乐” (Interactive Music)**:
    *   **状态联动**: 玩家残机（生命值）减少时，ZUN 号的吹奏力度可以变得更焦躁，颤音频率加快。
    *   **动态编曲**: 在 Boss 战阶段转换时，可以平滑地改变和声走向或 BGM 速度，甚至实时转调，而不需要硬切音频。

*   **ZUNpet 声学复刻**:
    *   我们通过**声学逆向工程**，在代码层面重构了 Roland "Romantic Tp" 的物理模型。
    *   **架构**: 双振荡器 FM 调制 + 动态低通滤波 + 空气噪音整形。
    *   **听感**: 完美还原了那标志性的“空气感”起音与 6Hz 的颤音细节。

*   **Bevy 引擎原生支持**:
    *   专为 ECS 架构设计，音频合成在独立的 Task Pool 中运行，不阻塞游戏主逻辑。
    *   提供简单的 API 接口，像生成实体一样生成声音。

## 快速开始

1.  **添加依赖**:
    
    ```toml
    [dependencies]
    gensokyo_dsp = "0.1"
    ```

2.  **未来计划：与 Bevy 集成**:

    *注：Bevy 集成目前正在设计中，以下 API 为假设性的。*

    ```rust
    // 计划中的 Bevy 系统用法
    fn spawn_bgm(mut commands: Commands, mut synth: ResMut<GensokyoSynth>) {
        // 启动 ZUNpet 乐器实例
        let zunpet_id = synth.spawn_instrument(InstrumentType::ZunPet);
        
        // 播放序列
        synth.play_sequence(zunpet_id, "assets/midi/bad_apple.mid");
    }
    ```

## 贡献指南

**致音乐人与扒谱师 (For Musicians & Arrangers)**

如果你是音乐人或扒谱师，并在协助本项目，请阅读以下说明：
**与程序贡献者的分工是：程序员负责制造“乐器”（代码），你负责编写“乐谱”（MIDI）。**

由于这是一个**程序化合成器**，它对 MIDI 数据的要求比传统 DAW 要更精细：

1.  **我们需要干净的数据**: 请提供标准的 MIDI 文件。
2.  **表情控制 (Expression)**:
    *   我们的合成器不只听音高，还听**参数**。
    *   请在 MIDI CC 通道（如 Mod Wheel / CC1）中画出**颤音曲线**。
    *   请利用 **Velocity (力度)** 来控制音色的明暗（Velocity > 100 会触发更亮的泛音）。
3.  **关于“还原度”**:
    *   这是一个基于物理规则的虚拟乐器，它会有自己的“脾气”。
    *   如果你发现某个音听起来不对（比如起音太慢），请告诉我，我去调整代码里的 **ADSR 包络参数**，而不是去修音频波形。

**致程序贡献者 (For Program Contributors)**

如果你是 Rust 开发者或 DSP 爱好者，欢迎参与贡献：

*   **DSP 优化**: 提高合成算法的效率（利用 `fundsp` 或 SIMD）。
*   **新乐器开发**: 协助逆向工程并实现更多东方风格的乐器（如 FM Bass, Synth Brass）。
*   **架构改进**: 改进与 Bevy 引擎的桥接和实时控制接口。

## 技术原理与合规性声明

本项目致力于通过**代码与数学公式**探索声音的物理本质。

1.  **声学逆向建模 (Acoustic Reverse Modeling)**:
    本项目使用了包括 **Sonic Charge Synplant 2** 在内的现代声学分析工具作为辅助，对参考音频进行频谱特征与物理参数估测（Parameter Estimation）。
2.  **净室设计 (Clean-room Design)**:
    *   所有的 `.rs` 源码均为手工编写或基于通用 DSP 算法生成。
    *   项目**不包含**任何来自 Roland、Yamaha 等硬件厂商的二进制数据（ROM/Samples）。
    *   项目**不包含**任何 Synplant 2 的专有格式文件。我们仅参考其分析出的通用物理参数（如频率比、调制指数）。
3.  **版权说明**:
    根据相关法律惯例，**声音的物理生成逻辑**（如“用正弦波 A 调制正弦波 B”）类似于菜谱或数学公式，不属于版权保护范围。本项目开源的是“生成声音的逻辑”，而非“声音录音本身”。

## 许可证 (License)

本项目采用以下任一许可证授权：

*   Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) 或 [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0))
*   MIT license ([LICENSE-MIT](LICENSE-MIT) 或 [http://opensource.org/licenses/MIT](http://opensource.org/licenses/MIT))

由你选择。

## 免责声明 (Disclaimer)

Synplant 是 Sonic Charge 的商标。本项目与 Sonic Charge 无关，也未获得其认可。
