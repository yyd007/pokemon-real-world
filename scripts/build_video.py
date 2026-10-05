#!/usr/bin/env python3
"""Assemble the photoreal Gen-1 Pokémon short from stills in public/creatures."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "creatures.json"
STILLS = ROOT / "public" / "creatures"
OUT = ROOT / "public" / "pokemon-real-world.mp4"
POSTER = ROOT / "public" / "poster.jpg"
ARTIFACT = Path("/opt/cursor/artifacts/pokemon-real-world.mp4")
WORK = Path("/tmp/pokemon-build")

SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
SANS_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SERIF_B = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
FONT_INDEX = 2  # Noto CJK SC

W, H = 1920, 1080
FPS = 30
VOICE = "zh-CN-YunyangNeural"
VOICE_RATE = "-4%"

TITLE = "如果初代宝可梦生活在真实世界"
SUBTITLE = "十种最常见的宝可梦"
END = "它们只是想象中的邻居。"
END_SUB = "画面是设想中的野外记录，不是真实物种。"

os.environ["PATH"] = os.path.expanduser("~/.local/bin") + os.pathsep + os.environ.get("PATH", "")


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    face = ImageFont.truetype(path, size, index=FONT_INDEX)
    name = " ".join(face.getname())
    if "SC" not in name:
        raise SystemExit(f"expected a Simplified Chinese face, got {name} from {path}")
    return face


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for ch in text:
        trial = line + ch
        if draw.textlength(trial, font=face) <= max_w:
            line = trial
        else:
            if line:
                lines.append(line)
            line = ch
    if line:
        lines.append(line)
    return lines


def vertical_gradient(height: int, max_alpha: int = 228) -> Image.Image:
    img = Image.new("RGBA", (W, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        t = y / max(height - 1, 1)
        alpha = int(max_alpha * (t ** 1.15))
        draw.line([(0, y), (W - 1, y)], fill=(6, 8, 10, alpha))
    return img


def text_size(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=face)
    return box[2] - box[0], box[3] - box[1]


def draw_center(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, y: int, fill: tuple[int, int, int, int]) -> None:
    tw, _ = text_size(draw, text, face)
    x = (W - tw) / 2
    draw.text((x, y), text, font=face, fill=fill)


def card_background() -> Image.Image:
    img = Image.new("RGB", (W, H), (12, 13, 15))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(22 * (1 - t) + 8 * t)
        g = int(20 * (1 - t) + 10 * t)
        b = int(18 * (1 - t) + 12 * t)
        for x in range(0, W, 2):
            # slight vignette toward the corners
            nx = (x - W / 2) / (W / 2)
            ny = (y - H / 2) / (H / 2)
            v = 1 - 0.45 * min(1.0, (nx * nx + ny * ny) ** 0.5)
            px[x, y] = (int(r * v), int(g * v), int(b * v))
            if x + 1 < W:
                px[x + 1, y] = px[x, y]
    return img


def render_title(path: Path, headline: str, sub: str, kicker: str) -> None:
    img = card_background().convert("RGBA")
    draw = ImageDraw.Draw(img)
    kicker_f = font(SANS, 28)
    head_f = font(SERIF_B, 78)
    sub_f = font(SERIF, 40)
    gold = (206, 172, 112, 255)
    paper = (242, 236, 226, 255)
    muted = (196, 188, 174, 255)

    draw_center(draw, kicker, kicker_f, 390, gold)
    # hairline
    draw.rectangle([W // 2 - 36, 448, W // 2 + 36, 450], fill=gold)
    draw_center(draw, headline, head_f, 490, paper)
    draw_center(draw, sub, sub_f, 620, muted)
    img.convert("RGB").save(path, quality=95)


def render_lower_third(path: Path, index: int, total: int, name: str, kind: str, line: str) -> None:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad = vertical_gradient(560, 230)
    img.alpha_composite(grad, (0, H - 560))
    draw = ImageDraw.Draw(img)

    idx_f = font(SANS, 30)
    name_f = font(SERIF_B, 84)
    type_f = font(SANS, 34)
    body_f = font(SANS, 36)
    gold = (214, 184, 122, 255)
    paper = (248, 244, 236, 255)
    soft = (232, 226, 214, 255)

    label = f"{index:02d}  /  {total:02d}"
    draw.text((84, 64), label, font=idx_f, fill=(236, 228, 210, 210))

    body_lines = wrap_text(draw, line, body_f, 1680)
    cursor = H - 78
    for body_line in reversed(body_lines):
        _, bh = text_size(draw, body_line, body_f)
        cursor -= bh
        draw.text((88, cursor), body_line, font=body_f, fill=soft)
        cursor -= 10
    cursor -= 18
    draw.rectangle([88, cursor, 168, cursor + 2], fill=gold)
    cursor -= 22
    _, th = text_size(draw, kind, type_f)
    cursor -= th
    draw.text((88, cursor), kind, font=type_f, fill=gold)
    cursor -= 18
    _, nh = text_size(draw, name, name_f)
    cursor -= nh
    # soft shadow so the name stays readable on bright fur
    draw.text((90, cursor + 3), name, font=name_f, fill=(0, 0, 0, 140))
    draw.text((88, cursor), name, font=name_f, fill=paper)
    img.save(path)


def synthesize(text: str, path: Path) -> None:
    if shutil.which("edge-tts") is None:
        raise SystemExit("edge-tts is not on PATH")
    run(
        [
            "edge-tts",
            "--voice",
            VOICE,
            f"--rate={VOICE_RATE}",
            "--text",
            text,
            "--write-media",
            str(path),
        ]
    )


def encode_segment(
    still: Path,
    overlay: Path | None,
    voice: Path,
    dest: Path,
    min_seconds: float,
    max_seconds: float,
    zoom: str,
) -> float:
    voice_dur = probe_duration(voice)
    duration = min(max_seconds, max(min_seconds, voice_dur + 1.15))
    # Keep the last word from being trimmed.
    if voice_dur + 0.85 > duration:
        duration = min(max_seconds, voice_dur + 0.85)
    frames = max(int(round(duration * FPS)), 1)
    duration = frames / FPS
    fade = 0.4
    fade_out = max(duration - fade, 0)

    if overlay is None:
        video_filter = (
            f"scale={W}:{H}:flags=lanczos,format=yuv420p,"
            f"zoompan=z='1':x=0:y=0:d={frames}:s={W}x{H}:fps={FPS},"
            f"fade=t=in:st=0:d={fade},fade=t=out:st={fade_out}:d={fade},format=yuv420p"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(still),
            "-i",
            str(voice),
            "-f",
            "lavfi",
            "-t",
            f"{duration:.3f}",
            "-i",
            "anoisesrc=color=brown:sample_rate=48000:amplitude=0.18",
            "-filter_complex",
            (
                f"[0:v]{video_filter}[v];"
                f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"adelay=420|420,apad=whole_dur={duration:.3f},atrim=0:{duration:.3f},volume=1.15[speech];"
                f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"lowpass=f=220,volume=0.045,"
                f"afade=t=in:st=0:d=0.4,afade=t=out:st={fade_out:.3f}:d={fade}[bed];"
                f"[speech][bed]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95[a]"
            ),
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-frames:v",
            str(frames),
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-t",
            f"{duration:.3f}",
            str(dest),
        ]
    else:
        zexpr = zoom.format(last=max(frames - 1, 1))
        video_filter = (
            f"[0:v]scale=2304:1296:force_original_aspect_ratio=increase,crop=2304:1296,format=yuv420p,"
            f"zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}[bg];"
            f"[bg][1:v]overlay=0:0:format=auto,"
            f"fade=t=in:st=0:d={fade},fade=t=out:st={fade_out}:d={fade},format=yuv420p[v];"
            f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay=420|420,apad=whole_dur={duration:.3f},atrim=0:{duration:.3f},volume=1.15[speech];"
            f"[3:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"lowpass=f=220,volume=0.045,"
            f"afade=t=in:st=0:d=0.4,afade=t=out:st={fade_out:.3f}:d={fade}[bed];"
            f"[speech][bed]amix=inputs=2:duration=first:dropout_transition=0,alimiter=limit=0.95[a]"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(still),
            "-i",
            str(overlay),
            "-i",
            str(voice),
            "-f",
            "lavfi",
            "-t",
            f"{duration:.3f}",
            "-i",
            "anoisesrc=color=brown:sample_rate=48000:amplitude=0.18",
            "-filter_complex",
            video_filter,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-frames:v",
            str(frames),
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-t",
            f"{duration:.3f}",
            str(dest),
        ]
    run(cmd)
    return duration


def main() -> None:
    creatures = json.loads(DATA.read_text(encoding="utf-8"))
    if len(creatures) != 10:
        raise SystemExit(f"expected 10 creatures, found {len(creatures)}")
    for item in creatures:
        still = STILLS / f"{item['id']}.jpg"
        if not still.exists():
            raise SystemExit(f"missing still: {still}")

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    title_png = WORK / "title.png"
    end_png = WORK / "end.png"
    render_title(title_png, TITLE, SUBTITLE, "短纪录片")
    render_title(end_png, END, END_SUB, "终")
    # poster is the title card, without relying on the encoded video
    Image.open(title_png).convert("RGB").save(POSTER, quality=90)

    segments: list[tuple[Path, Path | None, Path, float, float, str]] = []
    title_voice = WORK / "voice-title.mp3"
    synthesize(f"{TITLE}。{SUBTITLE}。", title_voice)
    segments.append((title_png, None, title_voice, 4.2, 7.4, "1"))

    zooms = [
        "1+0.10*on/{last}",
        "1.10-0.10*on/{last}",
    ]
    for i, item in enumerate(creatures, start=1):
        overlay = WORK / f"overlay-{i:02d}.png"
        render_lower_third(overlay, i, len(creatures), item["name"], item["type"], item["line"])
        voice = WORK / f"voice-{i:02d}.mp3"
        synthesize(f"{item['name']}。{item['line']}", voice)
        segments.append(
            (
                STILLS / f"{item['id']}.jpg",
                overlay,
                voice,
                7.4,
                9.2,
                zooms[(i - 1) % 2],
            )
        )

    end_voice = WORK / "voice-end.mp3"
    synthesize(END, end_voice)
    segments.append((end_png, None, end_voice, 4.0, 6.0, "1"))

    # Previews of the lower thirds composited on the stills, for a quick look.
    preview_dir = WORK / "previews"
    preview_dir.mkdir()
    for i, item in enumerate(creatures, start=1):
        base = Image.open(STILLS / f"{item['id']}.jpg").convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
        over = Image.open(WORK / f"overlay-{i:02d}.png")
        base.alpha_composite(over)
        base.convert("RGB").save(preview_dir / f"{i:02d}-{item['id']}.jpg", quality=85)
    Image.open(title_png).save(preview_dir / "00-title.jpg", quality=85)
    Image.open(end_png).save(preview_dir / "99-end.jpg", quality=85)

    if "--overlays-only" in sys.argv:
        print(f"overlays written to {preview_dir}")
        return

    list_path = WORK / "concat.txt"
    durations: list[float] = []
    lines: list[str] = []
    for n, (still, overlay, voice, min_s, max_s, zoom) in enumerate(segments):
        dest = WORK / f"seg-{n:02d}.mp4"
        durations.append(encode_segment(still, overlay, voice, dest, min_s, max_s, zoom))
        lines.append(f"file '{dest}'")
    list_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    total = sum(durations)
    print(f"segment durations: {', '.join(f'{d:.2f}' for d in durations)}")
    print(f"total {total:.2f}s")
    if not 70 <= total <= 100:
        raise SystemExit(f"duration {total:.2f}s is outside 70–100s")

    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(OUT),
        ]
    )
    if ARTIFACT.parent.exists():
        shutil.copy2(OUT, ARTIFACT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
