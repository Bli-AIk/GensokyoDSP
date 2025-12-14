use fundsp::hacker::*;

pub fn create_envelope(
    vol_atk: f32, vol_dcy: f32, vol_sus: f32, env_time: f32,
) -> An<impl AudioNode<Inputs = U0, Outputs = U1>> {
    // Attack time mapping based on vol_atk
    // The pattern is highly nonlinear and non-monotonic
    // Using interpolation of observed data points
    let attack_time = if vol_atk < 0.001 {
        0.20  // vol_atk=0
    } else if vol_atk < 0.11 {
        // 0.0547 -> 2.64s, 0.1058 -> 0.35s
        let t = (vol_atk as f64 - 0.0547) / (0.1058 - 0.0547);
        2.64 + t * (0.35 - 2.64)
    } else if vol_atk < 0.31 {
        // 0.1058 -> 0.35s, 0.3102 -> 0.13s
        let t = (vol_atk as f64 - 0.11) / (0.31 - 0.11);
        0.35 - t * 0.22
    } else if vol_atk < 0.50 {
        // 0.3102 -> 0.13s, approaching 0.5 -> 7s
        let t = (vol_atk as f64 - 0.31) / (0.50 - 0.31);
        0.13 + t * t * t * 18.0  // Cubic growth for smooth transition
    } else if vol_atk < 0.56 {
        // Sharp transition around 0.5: drops from ~7s to ~0.02s
        let t = (vol_atk as f64 - 0.50) / (0.56 - 0.50);
        7.0 - t * t * 6.98  // Quadratic drop
    } else {
        // 0.56+ : rises from 0.02s to ~0.4s
        let t = (vol_atk as f64 - 0.56) / (1.0 - 0.56);
        0.02 + t * 0.38
    };
    
    // Decay time influenced by vol_dcy and vol_sus
    // Observations: for vol_dcy=0.5, decay to 50% takes 0.25-0.27s when vol_sus < 0.5
    let decay_time = if vol_sus < 0.5 {
        0.25 + (vol_dcy as f64) * 0.5
    } else {
        // Longer decay for higher sustain
        let base = 0.4 + (vol_sus as f64 - 0.5) * 10.0;
        base * (0.5 + vol_dcy as f64)
    };
    
    // Decay curve shape
    let decay_power = if vol_dcy < 0.001 {
        10.0
    } else {
        // At vol_dcy=0.5, exponential curve (power ~2.5)
        2.5
    };
    
    // Sustain level
    // vol_sus < 0.5 -> 0.0
    // vol_sus >= 0.5 -> increases with vol_sus
    // Observations: vol_sus=0.75 -> ~4%, vol_sus=0.85 -> ~8%
    let sustain_level = if vol_sus < 0.5 {
        0.0
    } else {
        // Cubic growth: ((vol_sus - 0.5) * 2)^3 * 0.15
        let normalized = (vol_sus as f64 - 0.5) * 2.0;
        normalized.powf(3.0) * 0.15
    };

    // Total duration - controls when the envelope ends (for sounds without sustain)
    // For sounds with sustain (vol_sus >= 0.5), the envelope holds indefinitely
    let has_sustain = vol_sus >= 0.5;
    let total_duration = if env_time > 0.9 {
        1000.0
    } else {
        0.1 + (env_time as f64) * 10.0
    };

    envelope(move |t| {
        if t < attack_time {
            // Attack phase
            let progress = t / attack_time;
            if vol_atk < 0.5 {
                // Concave (slower start, faster end)
                let curve = 2.0 - vol_atk * 4.0;
                progress.powf(curve.max(1.0) as f64)
            } else {
                // Convex (faster start, slower end)
                let curve = (vol_atk - 0.5) * 4.0 + 1.0;
                progress.powf(1.0 / curve as f64)
            }
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
