# 如果初代宝可梦生活在真实世界

一部大约一分半的短纪录片。把十只最常被提起的初代宝可梦，设想成可能出现在野外的真实动物：保留轮廓、体色和标志特征，栖息地按自然纪录片来拍。每只配一句中文介绍，画面下方有名字和属性，并有中文旁白。

胖丁按初代图鉴记为**一般**属性，不是后来的妖精。

## 十种

| 顺序 | 名字 | 英文 | 属性 |
| --- | --- | --- | --- |
| 1 | 皮卡丘 | Pikachu | 电 |
| 2 | 喷火龙 | Charizard | 火 / 飞行 |
| 3 | 妙蛙种子 | Bulbasaur | 草 / 毒 |
| 4 | 杰尼龟 | Squirtle | 水 |
| 5 | 伊布 | Eevee | 一般 |
| 6 | 卡比兽 | Snorlax | 一般 |
| 7 | 耿鬼 | Gengar | 幽灵 / 毒 |
| 8 | 超梦 | Mewtwo | 超能力 |
| 9 | 胖丁 | Jigglypuff | 一般 |
| 10 | 暴鲤龙 | Gyarados | 水 / 飞行 |

介绍原文在 `data/creatures.json`。静帧在 `public/creatures/`，成片在 `public/pokemon-real-world.mp4`。

## 本地观看

需要 Node.js 18 以上。

```bash
npm install
npm run dev
```

开发服务器监听 `0.0.0.0:43123`。浏览器打开 [http://127.0.0.1:43123](http://127.0.0.1:43123)。页面上方是全屏区域里的播放器，下方按出场顺序列出十只的名字、属性和那句介绍。

## 重新生成视频

依赖：

- `ffmpeg`、`ffprobe`
- `fonts-noto-cjk`（简体中文，脚本使用 Noto Sans / Serif CJK SC）
- Python 3 与 Pillow（`python3-pil`）
- 可选旁白：`pip install edge-tts`，声音为 `zh-CN-YunyangNeural`

替换 `public/creatures/` 里对应的 jpg（16:9，文件名与 `id` 一致）后运行：

```bash
python3 scripts/build_video.py
```

脚本会按 `data/creatures.json` 生成字幕层、旁白和缓慢推拉的成片，输出到 `public/pokemon-real-world.mp4`，并尽量复制一份到 `/opt/cursor/artifacts/pokemon-real-world.mp4`。片长控制在 70–100 秒：片头约 4 秒，每只约 7–9 秒，片尾约 4 秒。

只想先看字幕叠在静帧上的效果，可以：

```bash
python3 scripts/build_video.py --overlays-only
```

预览图写在 `/tmp/pokemon-build/previews/`。

## 说明

画面是生成的写实设想，不是官方美术，也没有使用商标或图鉴原文。旁白和屏幕上的那一句介绍是同一句话。底下一层很轻的环境噪声，避免完全无声。若本机没有 `edge-tts`，需要先装上再跑合成脚本；现成的 mp4 已经包含旁白，直接播放即可。
