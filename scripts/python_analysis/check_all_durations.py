#!/usr/bin/env python3
"""
检查所有参考文件的时长，并生成正确的duration值
"""
import wave
from pathlib import Path
from collections import defaultdict

def get_wav_duration(filepath):
    """获取WAV文件时长（秒）"""
    with wave.open(str(filepath), 'rb') as w:
        frames = w.getnframes()
        rate = w.getframerate()
        duration = frames / float(rate)
        return duration

def main():
    fixtures_dir = Path("/home/aik/rustProjects/GensokyoDSP/tests/fixtures")
    
    # 按文件夹分组收集时长
    durations_by_folder = defaultdict(set)
    
    for folder in fixtures_dir.iterdir():
        if not folder.is_dir():
            continue
        
        for wav_file in folder.glob("*.wav"):
            duration = get_wav_duration(wav_file)
            durations_by_folder[folder.name].add(round(duration, 6))
    
    print("各测试类别的参考文件时长:")
    print("="*60)
    
    for folder_name in sorted(durations_by_folder.keys()):
        durations = sorted(durations_by_folder[folder_name])
        print(f"\n{folder_name}:")
        for dur in durations:
            count = len([f for f in (fixtures_dir / folder_name).glob("*.wav") 
                        if abs(get_wav_duration(f) - dur) < 0.0001])
            print(f"  {dur:.6f}s ({count} 文件)")
    
    # 生成建议的修正
    print("\n\n建议的duration修正:")
    print("="*60)
    
    corrections = {
        "a_color_tests": 7.019396,
        "a_freq_tests": 7.019396,
        "a_noise_tests": 7.239812,
        "b_freq_tests": 7.239812,
        "b_form_tests": 7.239812,
        "vol_sus_tests": 7.019396,
        "vol_atk_tests": 7.019396,
    }
    
    for folder, correct_dur in corrections.items():
        folder_path = fixtures_dir / folder
        if folder_path.exists():
            actual_durations = durations_by_folder.get(folder, set())
            if actual_durations:
                actual = list(actual_durations)[0]
                print(f"{folder}: {actual:.6f}s")

if __name__ == "__main__":
    main()
