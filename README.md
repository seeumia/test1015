# 终端俄罗斯方块

一个基于 Python 的终端版俄罗斯方块实现，使用 `curses` 进行界面渲染。

## 运行方式

```bash
python -m tetris.engine
```

如果当前终端不支持 `curses`（例如在部分 IDE 或 CI 环境中），可以改用文本演示模式：

```bash
python -m tetris.engine --headless
```

### 操作说明

- ←/→：左右移动
- ↑：旋转方块
- ↓：快速下落一格
- 空格：硬降到最底部
- P：暂停/继续
- Q：退出游戏

## 测试

```bash
pytest
```
