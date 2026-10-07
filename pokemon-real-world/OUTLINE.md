# Outline

A short nature-documentary film and a page that plays it. Ten well-known Generation 1 Pokémon are treated as animals that could live in a real habitat. Each one gets a photoreal still, one original Chinese sentence, and a matching voiceover.

The film is about 91 seconds, 1920×1080, H.264 video with AAC audio. Jigglypuff is typed as Normal, the Generation 1 typing, not Fairy.

## What plays

1. Title card. 「如果初代宝可梦生活在真实世界」, with the subtitle 「十种最常见的宝可梦」.
2. Ten creatures, in this order:

   | Order | Name | Type | Still |
   | --- | --- | --- | --- |
   | 1 | 皮卡丘 Pikachu | 电 | meadow, yellow fur, charged cheek pouches, lightning tail |
   | 2 | 喷火龙 Charizard | 火 / 飞行 | lava cliff, orange scaled wings, flame at the tail |
   | 3 | 妙蛙种子 Bulbasaur | 草 / 毒 | stocky green reptile with a closed bud on its back |
   | 4 | 杰尼龟 Squirtle | 水 | small blue turtle on stream rocks |
   | 5 | 伊布 Eevee | 一般 | brown forest mammal with a cream ruff |
   | 6 | 卡比兽 Snorlax | 一般 | huge animal asleep on a meadow |
   | 7 | 耿鬼 Gengar | 幽灵 / 毒 | short-limbed purple-black animal in night fog |
   | 8 | 超梦 Mewtwo | 超能力 | lavender biped alone on a windy ridge |
   | 9 | 胖丁 Jigglypuff | 一般 | round pink animal in flowers |
   | 10 | 暴鲤龙 Gyarados | 水 / 飞行 | huge blue fish under a waterfall |

3. End card. 「它们只是想象中的邻居。」

The page puts the player on top and lists the same ten entries underneath. Names, types, and sentences all come from one file, `data/creatures.json`.

## How a frame becomes the film

```text
data/creatures.json          copy: name, type, one sentence
        │
public/creatures/<id>.jpg    one photoreal still per creature
        │
scripts/build_video.py
        ├─ Pillow            title card, end card, transparent lower-thirds
        ├─ edge-tts          one Chinese voice clip per segment
        └─ ffmpeg            Ken Burns move, mix voice with a quiet bed, join segments
        │
public/pokemon-real-world.mp4
        │
src/main.ts + Vite           page that plays the file and renders the roster
```

Segment timing follows the voice. Each creature stays on screen about 7.4–9.2 seconds, long enough for the sentence to finish. The title runs longer than four seconds because the spoken title has to finish. Fades are 0.4 seconds. Alternate creatures push in and pull out so the stills do not feel locked.

## Folder map

```text
pokemon-real-world/
  data/creatures.json          the only copy source
  public/creatures/*.jpg       generated stills
  public/pokemon-real-world.mp4
  public/poster.jpg            title card, used as the video poster
  scripts/build_video.py       stills → film
  src/main.ts                  page
  src/style.css
  index.html
  vite.config.ts
  README.md                    how to run and rebuild
  OUTLINE.md                   this file
```

## Key tools and techniques

**Image generation.** Each still is a generated wildlife photograph, not official art and not a cartoon frame. The prompt keeps the silhouette, colors, and signature feature, and places the animal in a habitat. No text or logos are baked into the pictures. Files are JPEGs named by `id`.

**Python 3 and Pillow.** `scripts/build_video.py` draws every card. Title and end cards are full 1920×1080 images. Each creature gets a transparent PNG: index, name, type, and the sentence over a dark gradient. Names get a soft shadow so they stay readable on bright fur. Lines wrap by measuring the font, not by character count.

**Noto CJK.** Chinese is set with Noto Serif CJK SC for titles and names, and Noto Sans CJK SC for body text. The script loads face index 2 from the TTC and checks that the face name contains `SC`.

**edge-tts.** Narration uses the voice `zh-CN-YunyangNeural` at a slightly slower rate (`-4%`). Each clip speaks the same sentence that is on screen: the name, then the line. Title and ending are separate clips.

**ffmpeg.** One encode per segment, then a concat copy.

- Scale and crop the still to 2304×1296, then `zoompan` down to 1920×1080 at 30 fps.
- Overlay the Pillow PNG.
- Delay speech by 0.42 seconds, pad it to the segment length, and mix it with quiet brown noise low-passed at 220 Hz.
- Limit the mix so the voice does not clip.
- Encode H.264 at CRF 19 and AAC at 48 kHz, 160 kbps, stereo.
- Concatenate with stream copy and `+faststart` so the page can start playback before the whole file downloads.

`python3 scripts/build_video.py --overlays-only` writes composited preview JPEGs and skips the encode.

**Vite 6 and TypeScript.** The page has no React and no component library. `src/main.ts` reads `data/creatures.json`, builds a `<video>` element, and builds one card per creature. `vite.config.ts` serves `0.0.0.0:43123`. `allowedHosts` is open so a tunnel hostname is not rejected.

**Cloudflare quick tunnel.** `127.0.0.1` only answers inside this machine. `cloudflared tunnel --url http://127.0.0.1:43123` publishes a temporary `trycloudflare.com` address for a normal browser. That address dies when this machine stops. The film file in `public/` does not.

## Run

From this folder:

```bash
npm install
npm run dev
```

Rebuild the film after replacing a still:

```bash
python3 scripts/build_video.py
```

Rebuild needs `ffmpeg`, `ffprobe`, `fonts-noto-cjk`, Python 3, Pillow, and `edge-tts`.
