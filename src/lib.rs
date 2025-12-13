pub mod synplant;
pub mod synthesizer;
pub mod audio_compare;

pub use synplant::{SynplantPatch, SynplantGenome};
pub use synthesizer::SynplantSynthesizer;
pub use audio_compare::{compare_wav_files, AudioComparisonResult};
