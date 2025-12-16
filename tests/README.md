# 单元测试说明

## 测试结构

```
tests/
├── fixtures/           # 测试样板文件
│   ├── *.ron          # 配置文件
│   └── *.wav          # 参考音频（期望输出）
└── synthesis_tests.rs  # 测试代码
```

## 添加新测试

1. 准备两个文件：
   - `{name}.ron` - Synplant配置文件
   - `{name}.wav` - 该配置应该生成的参考音频

2. 将这两个文件放入 `tests/fixtures/` 目录

3. 在 `synthesis_tests.rs` 中添加新的测试函数：

```rust
#[test]
fn test_{name}_synthesis() {
    let test = TestCase {
        name: "{name}",
        config_file: "{name}.ron",
        reference_file: "{name}.wav",
        duration: 7.24,  // 根据实际音频长度调整
        similarity_threshold: 99.0,
    };
    
    test.run().expect("{name}音色合成测试失败");
}
```

## 相似度阈值

- 目标阈值：**99.0%**
- 当前实现尚未达到目标，随着合成器功能的完善会逐步提高

## 运行测试

```bash
# 运行所有测试
cargo test

# 运行特定测试
cargo test test_default_synthesis

# 显示详细输出
cargo test -- --nocapture

# 列出可用的测试样例
cargo test list_available_tests -- --ignored --nocapture
```

## 注意事项

- 测试生成的临时文件会保存在 `target/test_{name}.wav`
- 测试完成后会自动清理临时文件
- 如果测试失败，可以手动检查临时文件来调试问题
