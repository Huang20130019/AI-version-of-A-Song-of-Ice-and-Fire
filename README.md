冰与火之歌 - AI角色扮演游戏
基于本地Ollama AI的《冰与火之歌》世界角色扮演游戏。支持Python桌面版和纯HTML网页版。

✨ 特性
🎮 真实的RPG体验 - 基于乔治·R·R·马丁原著世界观
🤖 本地AI驱动 - 使用Ollama运行，数据完全私密
💾 完整存档系统 - 随时保存和读取游戏进度
🎨 中世纪主题UI - 沉浸式视觉体验
📱 双版本支持 - Python桌面版 + HTML网页版
🎯 游戏特点
真实的状态系统
无游戏化数值（HP/MP）
身体状态：健康/疲惫/轻伤/重伤/濒死
精神状态：平静/紧张/恐惧/愤怒/绝望
饥饿/疲劳系统
经济系统
金龙、银鹿、铜星货币
真实的汇率（1金龙=210银鹿=11760铜星）
AI生成内容
随机角色身份（史塔克家族、私生子、自由城邦等）
动态故事发展
真实后果系统（可能受伤或死亡）
📋 系统要求
Python桌面版
Python 3.12+
Windows/macOS/Linux
Ollama（本地AI服务）
网页版
现代浏览器（Chrome/Firefox/Edge）
Ollama运行在localhost:11434
🚀 快速开始
1. 安装Ollama
访问 Ollama官网 下载安装。

2. 下载AI模型
推荐模型（选一个） ollama pull qwen3:8b # 8B参数，速度快 ollama pull qwen2.5:14b # 14B参数，效果好 ollama pull llama3:8b # Llama3系列

3. 启动Ollama服务
ollama serve

4A. 运行Python版
安装依赖 pip install -r requirements.txt

运行游戏 python asoiaf_game.py

4B. 运行网页版
直接在浏览器中打开 index.html 文件即可。

🎮 游戏玩法
选择AI模型 - 从下拉菜单选择已安装的模型
开始新游戏 - AI将为你创建随机角色
输入行动 - 在输入框输入你的行动或对话
观察反馈 - AI会根据你的行动更新世界状态
保存进度 - 随时保存游戏进度
控制说明
Enter - 发送行动
Shift+Enter - 换行
保存游戏 - 保存当前进度
读取存档 - 加载之前的存档
⚙️ 配置说明
速度优化
如果AI响应太慢，可以调整以下参数：

Python版 (asoiaf_game.py) 'options': { 'temperature': 0.5, # 降低随机性 'num_predict': 150 # 限制输出长度 }

text

网页版 (index.html) options: { temperature: 0.7, top_p: 0.9 }

text

📁 项目结构
asoiaf-ai-rpg/ ├── asoiaf_game.py # Python桌面版主程序 ├── index.html # 网页版（单文件） ├── requirements.txt # Python依赖列表 ├── README.md # 本文件 ├── saves/ # 存档目录（自动创建）

text

🐛 常见问题
Q: 提示"无法连接Ollama"
A: 确保Ollama服务正在运行：ollama serve

Q: AI响应很慢怎么办？
A: 1. 使用更小的模型（如qwen3:8b） 2. 调整temperature参数到0.5 3. 限制num_predict到100-150

Q: 如何更换AI模型？
A: 在模型下拉菜单中选择其他已安装的模型即可

Q: 存档保存在哪里？
A: - Python版：saves/ 目录（JSON格式） - 网页版：浏览器LocalStorage

🤝 贡献
欢迎提交Issue和Pull Request！

开发计划
[ ] 支持更多AI模型（Claude、GPT等）
[ ] 多语言支持
[ ] 更丰富的游戏机制
[ ] 角色成长系统
[ ] 多结局系统
📜 许可证
MIT License - 详见 LICENSE 文件

👏 致谢
乔治·R·R·马丁 - 《冰与火之歌》原著
Ollama - 本地AI运行环境
Qwen团队 - 优秀的开源AI模型
注意：本项目仅供学习交流使用，不涉及任何商业用途。《冰与火之歌》相关版权归原作者所有。

⚠️ 使用说明
关于性能
本项目使用本地AI模型，响应速度取决于： - 硬件配置（推荐8GB+ RAM） - 模型大小（8B参数模型较快） - 提示词长度

预期响应时间：10-60秒/回合

适合人群
AI技术爱好者
《冰与火之歌》粉丝
本地AI应用开发者
隐私注重用户
不适合场景
需要快速响应的游戏体验
低配置设备
没有安装Ollama环境
建议体验在线版AI RPG游戏以获得更流畅的体验。
