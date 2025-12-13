pub mod audio_compare;
pub mod synplant;
pub mod synthesizer;

pub use audio_compare::{AudioComparisonResult, compare_wav_files};
pub use synplant::{SynplantGenome, SynplantPatch};
pub use synthesizer::SynplantSynthesizer;
