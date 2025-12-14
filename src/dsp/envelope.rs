use fundsp::hacker::*;

pub fn create_envelope(
    vol_atk: f32, vol_dcy: f32, vol_sus: f32, env_time: f32,
) -> An<impl AudioNode<Inputs = U0, Outputs = U1>> {
    // Attack time mapping based on vol_atk
    // Empirically measured from reference files:
    // The curve is highly non-monotonic with multiple peaks and valleys
    let attack_time = if vol_atk < 0.001 {
        0.20  // vol_atk=0.0
    } else if vol_atk <= 0.0547 {
        // 0.0->0.20, 0.0547->0.08
        let t = (vol_atk as f64) / 0.0547;
        0.20 + t * (0.08 - 0.20)
    } else if vol_atk <= 0.1058 {
        // Linear interpolation: 0.0547->0.08, 0.1058->0.29
        let t = (vol_atk as f64 - 0.0547) / (0.1058 - 0.0547);
        0.08 + t * (0.29 - 0.08)
    } else if vol_atk <= 0.1496 {
        // 0.1058->0.29, 0.1496->0.47 (first peak)
        let t = (vol_atk as f64 - 0.1058) / (0.1496 - 0.1058);
        0.29 + t * (0.47 - 0.29)
    } else if vol_atk <= 0.2007 {
        // 0.1496->0.47, 0.2007->0.35 (descending)
        let t = (vol_atk as f64 - 0.1496) / (0.2007 - 0.1496);
        0.47 + t * (0.35 - 0.47)
    } else if vol_atk <= 0.2518 {
        // 0.2007->0.35, 0.2518->0.23
        let t = (vol_atk as f64 - 0.2007) / (0.2518 - 0.2007);
        0.35 + t * (0.23 - 0.35)
    } else if vol_atk <= 0.3102 {
        // 0.2518->0.23, 0.3102->0.12
        let t = (vol_atk as f64 - 0.2518) / (0.3102 - 0.2518);
        0.23 + t * (0.12 - 0.23)
    } else if vol_atk <= 0.5506 {
        // 0.3102->0.12, 0.3540~0.5506->0.0 (instant attack zone)
        let t = (vol_atk as f64 - 0.3102) / (0.5506 - 0.3102);
        0.12 * (1.0 - t)
    } else if vol_atk <= 0.6055 {
        // 0.5506->0.0, 0.6055->0.04 (starting to rise)
        let t = (vol_atk as f64 - 0.5506) / (0.6055 - 0.5506);
        0.0 + t * 0.04
    } else if vol_atk <= 0.6519 {
        // 0.6055->0.04, 0.6519->0.12
        let t = (vol_atk as f64 - 0.6055) / (0.6519 - 0.6055);
        0.04 + t * (0.12 - 0.04)
    } else if vol_atk <= 0.7025 {
        // 0.6519->0.12, 0.7025->0.21
        let t = (vol_atk as f64 - 0.6519) / (0.7025 - 0.6519);
        0.12 + t * (0.21 - 0.12)
    } else if vol_atk <= 0.7489 {
        // 0.7025->0.21, 0.7489->0.29
        let t = (vol_atk as f64 - 0.7025) / (0.7489 - 0.7025);
        0.21 + t * (0.29 - 0.21)
    } else if vol_atk <= 0.8080 {
        // 0.7489->0.29, 0.8080->0.38
        let t = (vol_atk as f64 - 0.7489) / (0.8080 - 0.7489);
        0.29 + t * (0.38 - 0.29)
    } else if vol_atk <= 0.8502 {
        // 0.8080->0.38, 0.8502->0.45 (second peak)
        let t = (vol_atk as f64 - 0.8080) / (0.8502 - 0.8080);
        0.38 + t * (0.45 - 0.38)
    } else if vol_atk <= 0.9051 {
        // 0.8502->0.45, 0.9051->0.33 (descending)
        let t = (vol_atk as f64 - 0.8502) / (0.9051 - 0.8502);
        0.45 + t * (0.33 - 0.45)
    } else if vol_atk <= 0.9515 {
        // 0.9051->0.33, 0.9515->0.22
        let t = (vol_atk as f64 - 0.9051) / (0.9515 - 0.9051);
        0.33 + t * (0.22 - 0.33)
    } else {
        // 0.9515->0.22, 1.0->0.1
        let t = (vol_atk as f64 - 0.9515) / (1.0 - 0.9515);
        0.22 + t * (0.10 - 0.22)
    };
    
    // Decay time influenced by vol_dcy and vol_sus
    // For vol_sus < 0.5: decay time to reach 10% is about 0.66s when vol_dcy=0.5
    let decay_time = if vol_sus < 0.5 {
        // Base decay time scaled by vol_dcy
        let base_time = 1.3;  // Time to reach ~10% for vol_dcy=0.5
        base_time * (0.2 + vol_dcy as f64 * 1.6)
    } else {
        // Longer decay for higher sustain
        let base = 0.4 + (vol_sus as f64 - 0.5) * 10.0;
        base * (0.5 + vol_dcy as f64)
    };
    
    // Decay curve shape
    // For no-sustain sounds, use exponential decay
    let decay_power = if vol_sus < 0.5 {
        // Exponential decay - power of about 1.5-2.0
        1.8
    } else if vol_dcy < 0.001 {
        10.0
    } else {
        // At vol_dcy=0.5, exponential curve (power ~2.5)
        2.5
    };
    
    // Sustain level - empirically measured
    // The curve starts around 0.4 and grows to 100% at 1.0
    let sustain_level = if vol_sus < 0.40 {
        0.0
    } else if vol_sus <= 0.4051 {
        // 0.40->0%, 0.4051->0.89%
        let t = (vol_sus as f64 - 0.40) / (0.4051 - 0.40);
        t * 0.0089
    } else if vol_sus <= 0.4536 {
        // 0.4051->0.89%, 0.4536->2.51%
        let t = (vol_sus as f64 - 0.4051) / (0.4536 - 0.4051);
        0.0089 + t * (0.0251 - 0.0089)
    } else if vol_sus <= 0.4958 {
        // 0.4536->2.51%, 0.4958->4.75%
        let t = (vol_sus as f64 - 0.4536) / (0.4958 - 0.4536);
        0.0251 + t * (0.0475 - 0.0251)
    } else if vol_sus <= 0.5506 {
        // 0.4958->4.75%, 0.5506->8.86%
        let t = (vol_sus as f64 - 0.4958) / (0.5506 - 0.4958);
        0.0475 + t * (0.0886 - 0.0475)
    } else if vol_sus <= 0.6055 {
        // 0.5506->8.86%, 0.6055->13.00%
        let t = (vol_sus as f64 - 0.5506) / (0.6055 - 0.5506);
        0.0886 + t * (0.1300 - 0.0886)
    } else if vol_sus <= 0.6519 {
        // 0.6055->13.00%, 0.6519->18.63%
        let t = (vol_sus as f64 - 0.6055) / (0.6519 - 0.6055);
        0.1300 + t * (0.1863 - 0.1300)
    } else if vol_sus <= 0.7025 {
        // 0.6519->18.63%, 0.7025->25.94%
        let t = (vol_sus as f64 - 0.6519) / (0.7025 - 0.6519);
        0.1863 + t * (0.2594 - 0.1863)
    } else if vol_sus <= 0.7489 {
        // 0.7025->25.94%, 0.7489->34.17%
        let t = (vol_sus as f64 - 0.7025) / (0.7489 - 0.7025);
        0.2594 + t * (0.3417 - 0.2594)
    } else if vol_sus <= 0.8080 {
        // 0.7489->34.17%, 0.8080->44.47%
        let t = (vol_sus as f64 - 0.7489) / (0.8080 - 0.7489);
        0.3417 + t * (0.4447 - 0.3417)
    } else if vol_sus <= 0.8502 {
        // 0.8080->44.47%, 0.8502->54.08%
        let t = (vol_sus as f64 - 0.8080) / (0.8502 - 0.8080);
        0.4447 + t * (0.5408 - 0.4447)
    } else if vol_sus <= 0.9051 {
        // 0.8502->54.08%, 0.9051->69.15%
        let t = (vol_sus as f64 - 0.8502) / (0.9051 - 0.8502);
        0.5408 + t * (0.6915 - 0.5408)
    } else if vol_sus <= 0.9515 {
        // 0.9051->69.15%, 0.9515->81.24%
        let t = (vol_sus as f64 - 0.9051) / (0.9515 - 0.9051);
        0.6915 + t * (0.8124 - 0.6915)
    } else {
        // 0.9515->81.24%, 1.0->100%
        let t = (vol_sus as f64 - 0.9515) / (1.0 - 0.9515);
        0.8124 + t * (1.0 - 0.8124)
    };

    // Total duration - controls when the envelope ends (for sounds without sustain)
    // For sounds with sustain (vol_sus >= 0.5), the envelope holds indefinitely
    let has_sustain = vol_sus >= 0.5;
    let total_duration = if env_time > 0.9 {
        1000.0
    } else {
        0.1 + (env_time as f64) * 10.0
    };

    // Attack curve power - empirically determined
    // Different vol_atk values produce different curve shapes
    let attack_power = if vol_atk <= 0.06 {
        0.93  // Nearly linear for very small values
    } else if vol_atk <= 0.35 {
        // Power increases with vol_atk, peaks around 3.0
        let t = (vol_atk as f64 - 0.06) / (0.35 - 0.06);
        0.93 + t * (3.0 - 0.93)
    } else if vol_atk <= 0.56 {
        // Instant attack zone - no curve needed
        1.0
    } else if vol_atk <= 0.62 {
        // Starts linear again
        let t = (vol_atk as f64 - 0.56) / (0.62 - 0.56);
        1.0 + t * 0.06
    } else {
        // Power increases again
        let t = (vol_atk as f64 - 0.62) / (1.0 - 0.62);
        1.06 + t * (3.0 - 1.06)
    };

    envelope(move |t| {
        if t < attack_time {
            // Attack phase
            let progress = t / attack_time;
            progress.powf(attack_power)
        } else if t < attack_time + decay_time {
            // Decay phase
            let phase = (t - attack_time) / decay_time;
            let decay_curve = (1.0 - phase).max(0.0).powf(decay_power);
            sustain_level + (1.0 - sustain_level) * decay_curve
        } else {
            // Sustain phase or end
            if has_sustain {
                // Hold sustain level indefinitely
                sustain_level
            } else {
                // For no-sustain sounds, check if we've exceeded total duration
                if t > total_duration {
                    0.0
                } else {
                    // Continue at decay curve tail
                    sustain_level
                }
            }
        }
    })
}
