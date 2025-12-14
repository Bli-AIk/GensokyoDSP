use gensokyo_dsp::*;

#[test]
fn test_envelope_sustain() {
    // Test that vol_sus=0.7489 produces non-zero sustain
    let genome = synplant::SynplantGenome {
        a_form: 0.0,
        a_noise: 0.0,
        a_mod: 0.5,
        a_color: 0.5,
        a_freq: 0.5,
        b_form: 0.5,
        b_noise: 0.0,
        b_mod: 0.5,
        b_freq: 0.6875,
        b_sh: 0.5,
        fm_mod: 0.5,
        fm_amt: 0.5,
        mix_mod: 0.5,
        osc_mix: 0.0,
        sub_am: 0.0,
        env_time: 0.5,
        env_loop: 0.5,
        env_tilt: 0.5,
        env_kf: 0.5,
        vol_atk: 0.0,
        vol_dcy: 0.5,
        vol_sus: 0.7489,
        vol_fade: 0.0,
        mod_atk: 0.5,
        mod_dcy: 0.5,
        mod_sh: 0.5,
        mod_vel: 0.5,
        lfo_rate: 0.0,
        lfo_amt: 0.5,
        lfo_bal: 0.5,
        lfo_dly: 0.5,
        flt_type: 0.6666667,
        flt_q: 0.5,
        flt_mod: 0.5,
        flt_sep: 0.5,
        flt_freq: 1.0,
        flt_kf: 0.0,
        saturate: 0.0,
        rvb_mix: 0.0,
        rvb_atk: 0.5,
        rvb_len: 0.5,
        rvb_damp: 0.5,
        rvb_chor: 0.0,
        rvb_size: 0.5,
        adj_bass: 0.5,
        adj_treb: 0.5,
        adj_pan: 0.5,
        adj_clip: 0.0,
    };
    
    let synth = synthesizer::SynplantSynthesizer::new(genome);
    let wave = synth.synthesize(10.0);
    
    // Check last 1 second RMS
    let sr = 48000;
    let last_sec = &wave.channel(0)[wave.length() - sr..];
    let rms = (last_sec.iter().map(|x| x * x).sum::<f32>() / last_sec.len() as f32).sqrt();
    
    println!("Sustain RMS: {:.6}", rms);
    
    assert!(rms > 0.001, "Sustain level should be non-zero for vol_sus=0.7489, got {}", rms);
}
