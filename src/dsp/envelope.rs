use fundsp::hacker::*;

pub fn create_envelope(
    vol_atk: f32, vol_dcy: f32, vol_sus: f32,
) -> An<impl AudioNode<Inputs = U0, Outputs = U1>> {
    let attack_time = 0.01; 
    
    // Decay time: vol_dcy=0.5 -> ~0.5ms.
    // Try: 0.0001 + vol_dcy^2 * 0.002
    // 0.5 -> 0.0001 + 0.25 * 0.002 = 0.0006s.
    let decay_time = 0.0001 + (vol_dcy as f64).powi(2) * 0.002;
    
    // Sustain level: vol_sus=0.5 -> ~0.015 (RMS match suggests pow 6).
    let sustain_level = (vol_sus as f64).powi(6);
    
    envelope(move |t| {
        if t < attack_time {
             let progress = t / attack_time;
             if vol_atk < 0.5 {
                let curve = 2.0 - vol_atk * 4.0; 
                progress.powf(curve.max(1.0) as f64)
             } else {
                let curve = (vol_atk - 0.5) * 4.0 + 1.0; 
                progress.powf(1.0 / curve as f64)
             }
        } else if t < attack_time + decay_time {
            let phase = (t - attack_time) / decay_time;
            // Exponential-like decay (concave)
            let decay_curve = (1.0 - phase).max(0.0).powi(2);
            sustain_level + (1.0 - sustain_level) * decay_curve
        } else {
            sustain_level
        }
    })
}
