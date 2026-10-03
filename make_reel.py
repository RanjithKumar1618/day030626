from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


WIDTH, HEIGHT, FPS = 720, 1280, 24
AUDIO = Path(__file__).with_name("EvaruEvaro.mp3")
OUTPUT = Path(__file__).with_name("EvaruEvaro_reel.mp4")
STORYBOARD = Path(__file__).with_name("EvaruEvaro_storyboard.jpg")
SCENE_COUNT = 6
LYRIC_CUES: list[tuple[float, float, tuple[str, ...]]] = [
    (0.2, 3.6, ("Emo chestunnano",)),
    (3.68, 6.35, ("Emem inka chestano",)),
    (6.8, 9.15, ("Chestu emaina pothano",)),
    (9.35, 12.0, ("Mari chestu emaina pothano",)),
    (12.5, 15.5, ("Emo marevaro evaro", "chestu pothano")),
    (15.5, 17.1, ("Edurina",)),
    (18.2, 20.6, ("Nuvvu kalisake",)),
    (21.75, 24.34, ("Modalaindey",)),
]
LYRIC_COLORS = (
    (87, 218, 255),
    (255, 139, 167),
    (255, 209, 102),
    (136, 229, 200),
    (198, 160, 255),
)
CAMERA_KEYFRAMES = (
    (0.0, 1.02, 0, 0),
    (0.24, 1.10, 10, -5),
    (0.5, 1.14, -10, 8),
    (0.76, 1.045, 12, 0),
    (1.0, 1.11, 0, -6),
)



def font(size: int, italic: bool = False) -> ImageFont.FreeTypeFont:
    name = "georgiai.ttf" if italic else "georgia.ttf"
    path = Path(r"C:\Windows\Fonts") / name
    if not path.exists():
        path = Path(r"C:\Windows\Fonts\georgia.ttf")
    return ImageFont.truetype(str(path), size=size)


def gradient(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        blend = y / (HEIGHT - 1)
        color = tuple(round(top[i] * (1 - blend) + bottom[i] * blend) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=color)
    return image


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: tuple[int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=8, fill=fill)


def woman(draw: ImageDraw.ImageDraw, x: int, feet: int, scale: float = 1.0, color: tuple[int, int, int] = (35, 37, 48), facing: int = 1) -> None:
    head = 46 * scale
    draw.ellipse((x - head * 0.36, feet - 220 * scale, x + head * 0.36, feet - 220 * scale + head), fill=color)
    draw.polygon([
        (x - 24 * scale, feet - 179 * scale), (x + 23 * scale, feet - 179 * scale),
        (x + 42 * scale, feet - 90 * scale), (x + 29 * scale, feet),
        (x - 32 * scale, feet), (x - 43 * scale, feet - 91 * scale),
    ], fill=color)
    draw.polygon([
        (x - 17 * scale, feet - 176 * scale),
        (x + facing * 48 * scale, feet - 87 * scale),
        (x + facing * 34 * scale, feet - 24 * scale),
        (x + facing * 9 * scale, feet - 107 * scale),
        (x - 29 * scale, feet - 161 * scale),
    ], fill=(130, 92, 100))
    draw.line((x + facing * 23 * scale, feet - 158 * scale, x + facing * 61 * scale, feet - 94 * scale), fill=color, width=max(3, round(10 * scale)))
    draw.line((x - 12 * scale, feet - 101 * scale, x - 15 * scale, feet), fill=color, width=max(4, round(12 * scale)))
    draw.line((x + 13 * scale, feet - 101 * scale, x + 18 * scale, feet), fill=color, width=max(4, round(12 * scale)))
    draw.arc((x - 42 * scale, feet - 236 * scale, x + 48 * scale, feet - 136 * scale), 190, 345, fill=(25, 26, 37), width=max(3, round(8 * scale)))

def man(draw: ImageDraw.ImageDraw, x: int, feet: int, scale: float = 1.0, color: tuple[int, int, int] = (32, 34, 45), facing: int = 1) -> None:
    head = 46 * scale
    draw.ellipse((x - head * 0.36, feet - 220 * scale, x + head * 0.36, feet - 220 * scale + head), fill=color)
    draw.polygon([
        (x - 24 * scale, feet - 178 * scale), (x + 24 * scale, feet - 178 * scale),
        (x + 37 * scale, feet - 93 * scale), (x + 29 * scale, feet - 80 * scale),
        (x - 30 * scale, feet - 80 * scale), (x - 39 * scale, feet - 94 * scale),
    ], fill=color)
    draw.line((x - 26 * scale, feet - 167 * scale, x + facing * 38 * scale, feet - 104 * scale), fill=color, width=max(3, round(12 * scale)))
    draw.line((x + 26 * scale, feet - 164 * scale, x - facing * 27 * scale, feet - 103 * scale), fill=color, width=max(3, round(12 * scale)))
    draw.line((x - 12 * scale, feet - 86 * scale, x - 18 * scale, feet), fill=color, width=max(4, round(15 * scale)))
    draw.line((x + 13 * scale, feet - 86 * scale, x + 19 * scale, feet), fill=color, width=max(4, round(15 * scale)))


def make_scenes() -> list[Image.Image]:
    scenes: list[Image.Image] = []

    # 1. A rainy window, and one person awake after the house has gone quiet.
    image = gradient((20, 38, 54), (115, 73, 65))
    draw = ImageDraw.Draw(image)
    draw.rectangle((66, 170, 654, 809), fill=(17, 34, 48), outline=(192, 150, 124), width=8)
    draw.rectangle((83, 188, 637, 791), fill=(48, 79, 91))
    draw.rectangle((83, 596, 637, 791), fill=(195, 120, 83))
    draw.rectangle((345, 188, 356, 791), fill=(186, 146, 118))
    draw.rectangle((83, 485, 637, 496), fill=(186, 146, 118))
    draw.rectangle((42, 126, 76, 862), fill=(77, 45, 55))
    draw.rectangle((644, 126, 679, 862), fill=(77, 45, 55))
    for x in (116, 198, 286, 403, 501, 592):
        draw.line((x, 210, x - 22, 448), fill=(191, 210, 212), width=3)
        draw.line((x + 18, 520, x + 2, 699), fill=(191, 210, 212), width=2)
    draw.ellipse((445, 657, 492, 704), fill=(247, 190, 129))
    woman(draw, 393, 1000, 1.27, (27, 34, 45), facing=-1)
    draw.rectangle((0, 1000, WIDTH, HEIGHT), fill=(30, 33, 41))
    rounded_panel(draw, (26, 1044, 212, 1164), (66, 48, 49))
    draw.line((586, 866, 551, 998), fill=(60, 81, 69), width=9)
    for x, y in ((555, 875), (589, 902), (541, 936), (608, 952), (572, 972)):
        draw.ellipse((x - 23, y - 11, x + 22, y + 13), fill=(79, 104, 77))
    scenes.append(image)

    # 2. A warm memory of the two of them walking home together.
    image = gradient((69, 81, 112), (218, 144, 96))
    draw = ImageDraw.Draw(image)
    draw.ellipse((424, 270, 636, 483), fill=(250, 196, 137))
    draw.polygon([(0, 806), (168, 710), (286, 808), (424, 701), (720, 815), (720, 1280), (0, 1280)], fill=(68, 67, 81))
    draw.polygon([(318, 742), (382, 742), (579, 1280), (112, 1280)], fill=(179, 126, 106))
    for x, top in ((0, 433), (82, 503), (550, 439), (641, 499)):
        draw.rectangle((x, top, x + 103, 855), fill=(107, 73, 77))
        draw.rectangle((x + 15, top + 30, x + 86, top + 160), fill=(203, 150, 115))
        draw.rectangle((x + 14, top + 205, x + 87, top + 333), fill=(40, 56, 69))
    for x in (110, 602):
        draw.line((x, 725, x, 953), fill=(37, 44, 54), width=8)
        draw.ellipse((x - 20, 707, x + 20, 747), fill=(247, 199, 137))
    woman(draw, 317, 1100, 1.35, (55, 43, 54), facing=1)
    man(draw, 406, 1100, 1.35, (43, 46, 58), facing=-1)
    draw.line((349, 872, 374, 889), fill=(166, 101, 90), width=11)
    scenes.append(image)

    # 3. A shared table with too much space between two chairs.
    image = gradient((24, 34, 49), (75, 49, 53))
    draw = ImageDraw.Draw(image)
    draw.rectangle((75, 236, 645, 603), fill=(39, 51, 59))
    draw.rectangle((108, 267, 610, 579), fill=(72, 81, 79))
    draw.rectangle((122, 312, 596, 579), fill=(123, 85, 76))
    draw.rectangle((0, 788, WIDTH, 826), fill=(151, 100, 68))
    draw.polygon([(0, 826), (720, 826), (720, 1280), (0, 1280)], fill=(48, 39, 43))
    draw.ellipse((305, 661, 427, 730), fill=(255, 202, 127))
    draw.line((365, 524, 365, 679), fill=(198, 145, 98), width=8)
    draw.polygon([(365, 530), (319, 680), (412, 680)], fill=(206, 143, 91))
    woman(draw, 179, 983, 1.25, (27, 31, 42), facing=1)
    man(draw, 548, 983, 1.25, (24, 29, 40), facing=-1)
    draw.rectangle((93, 857, 629, 906), fill=(93, 61, 53))
    draw.rectangle((138, 902, 151, 1064), fill=(46, 39, 42))
    draw.rectangle((571, 902, 584, 1064), fill=(46, 39, 42))
    for x in (219, 495):
        draw.ellipse((x - 19, 802, x + 19, 840), fill=(198, 183, 154))
        draw.rectangle((x - 16, 820, x + 16, 857), fill=(198, 183, 154))
    scenes.append(image)

    # 4. The small things left behind: rings, a letter, and a gap.
    image = gradient((48, 52, 65), (100, 63, 56))
    draw = ImageDraw.Draw(image)
    draw.polygon([(0, 696), (720, 655), (720, 1280), (0, 1280)], fill=(115, 77, 61))
    draw.line((0, 721, 720, 678), fill=(189, 134, 96), width=6)
    draw.polygon([(223, 854), (489, 827), (547, 1058), (175, 1082)], fill=(217, 203, 178))
    draw.line((257, 906, 455, 885), fill=(152, 121, 107), width=4)
    draw.line((261, 942, 442, 923), fill=(152, 121, 107), width=3)
    draw.ellipse((303, 758, 357, 811), outline=(237, 201, 131), width=8)
    draw.ellipse((378, 746, 432, 799), outline=(204, 207, 203), width=8)
    draw.line((48, 805, 224, 869), fill=(37, 36, 43), width=34)
    draw.ellipse((24, 779, 91, 846), fill=(37, 36, 43))
    draw.line((668, 810, 499, 872), fill=(33, 35, 44), width=34)
    draw.ellipse((632, 778, 697, 844), fill=(33, 35, 44))
    scenes.append(image)

    # 5. Two backs turning toward opposite ends of one corridor.
    image = gradient((34, 43, 60), (118, 77, 68))
    draw = ImageDraw.Draw(image)
    draw.polygon([(0, 378), (290, 472), (290, 844), (0, 1011)], fill=(52, 53, 66))
    draw.polygon([(720, 378), (430, 472), (430, 844), (720, 1011)], fill=(43, 47, 60))
    draw.polygon([(290, 472), (430, 472), (720, 1280), (0, 1280)], fill=(105, 78, 70))
    draw.rectangle((295, 356, 425, 784), fill=(204, 137, 99))
    draw.rectangle((313, 373, 407, 765), fill=(42, 56, 67))
    draw.ellipse((382, 561, 390, 569), fill=(235, 183, 115))
    woman(draw, 147, 1130, 1.29, (28, 35, 48), facing=-1)
    man(draw, 559, 1130, 1.29, (28, 33, 45), facing=1)
    draw.polygon([(0, 1160), (270, 1076), (298, 1280), (0, 1280)], fill=(47, 43, 51))
    draw.polygon([(720, 1160), (445, 1076), (421, 1280), (720, 1280)], fill=(37, 41, 52))
    scenes.append(image)

    # 6. Morning light finds the room they no longer share.
    image = gradient((50, 71, 96), (219, 154, 111))
    draw = ImageDraw.Draw(image)
    draw.rectangle((382, 185, 672, 751), fill=(27, 47, 62), outline=(171, 136, 116), width=8)
    draw.rectangle((401, 207, 653, 729), fill=(209, 155, 114))
    draw.rectangle((414, 418, 641, 729), fill=(230, 180, 127))
    draw.ellipse((489, 309, 566, 386), fill=(249, 210, 155))
    draw.rectangle((0, 946, WIDTH, HEIGHT), fill=(51, 49, 56))
    draw.rectangle((60, 689, 91, 1048), fill=(72, 49, 53))
    draw.rectangle((91, 711, 265, 1048), fill=(90, 58, 57))
    draw.polygon([(91, 711), (260, 739), (260, 1048), (91, 1048)], fill=(44, 50, 62))
    draw.line((264, 751, 264, 1050), fill=(207, 153, 109), width=6)
    draw.rectangle((362, 944, 648, 972), fill=(100, 67, 59))
    draw.rectangle((388, 971, 407, 1105), fill=(64, 51, 54))
    draw.rectangle((604, 971, 623, 1105), fill=(64, 51, 54))
    woman(draw, 510, 1039, 0.93, (42, 46, 55), facing=1)
    scenes.append(image)

    return scenes


def make_photo_scenes(warm: bool = False) -> list[Image.Image]:
    photo_directory = Path(__file__).with_name("reel_photos")
    image = ImageOps.fit(
        Image.open(photo_directory / "window.jpg").convert("RGB"),
        (WIDTH, HEIGHT),
        method=Image.Resampling.LANCZOS,
    )
    luminance = ImageOps.grayscale(image)
    cinematic_tones = ImageOps.colorize(
        luminance,
        black=(25, 12, 27) if warm else (3, 12, 28),
        white=(248, 205, 158) if warm else (183, 215, 226),
        blackpoint=8,
        whitepoint=238,
    )
    image = Image.blend(image, cinematic_tones, 0.9)
    image = ImageEnhance.Color(image).enhance(0.9 if warm else 0.72)
    image = ImageEnhance.Contrast(image).enhance(1.18 if warm else 1.3)
    image = ImageEnhance.Brightness(image).enhance(0.94 if warm else 0.84)
    return [image] * SCENE_COUNT


def make_vignette() -> Image.Image:
    mask = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((-245, -145, WIDTH + 245, HEIGHT + 220), fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(106))
    darkness = Image.eval(mask, lambda value: round(value * 0.46))
    shade = Image.new("RGB", (WIDTH, HEIGHT), (7, 11, 19))
    shade.putalpha(darkness)
    return shade


def caption_layer(
    cue: tuple[float, float, tuple[str, ...]] | None, elapsed: float
) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    if cue is None:
        return layer
    start, end, lines = cue
    fade = min(1.0, (elapsed - start) / 0.18, (end - elapsed) / 0.18)
    alpha = round(255 * max(0.0, fade))
    draw = ImageDraw.Draw(layer)
    title_font = font(44, italic=True)
    detail_font = font(31)
    title_y = 963 if len(lines) == 1 else 925
    for line_number, line in enumerate(lines):
        line_font = title_font if line_number == 0 else detail_font
        bbox = draw.textbbox((0, 0), line, font=line_font, stroke_width=1)
        x = (WIDTH - (bbox[2] - bbox[0])) // 2
        y = title_y + line_number * 63
        draw.text((x, y + 3), line, font=line_font, fill=(4, 8, 14, round(alpha * 0.85)), stroke_width=2, stroke_fill=(4, 8, 14, alpha))
        color = LYRIC_COLORS[(LYRIC_CUES.index(cue) + line_number) % len(LYRIC_COLORS)]
        draw.text(
            (x, y),
            line,
            font=line_font,
            fill=(*color, alpha),
            stroke_width=2,
            stroke_fill=(7, 12, 24, alpha),
        )
    return layer


def brand_layer(elapsed: float, duration: float) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    fade = min(1.0, elapsed / 0.65, (duration - elapsed) / 0.65)
    alpha = round(178 * max(0.0, fade))
    draw = ImageDraw.Draw(layer)
    brand_font = font(36, italic=True)
    support_font = font(15)
    brand = "RaaHa"
    support = "FOLLOW & SUPPORT"
    brand_width = draw.textbbox((0, 0), brand, font=brand_font)[2]
    support_width = draw.textbbox((0, 0), support, font=support_font)[2]
    draw.text(
        ((WIDTH - brand_width) // 2, 38),
        brand,
        font=brand_font,
        fill=(246, 219, 183, alpha),
        stroke_width=2,
        stroke_fill=(8, 17, 29, round(alpha * 0.8)),
    )
    draw.line((WIDTH // 2 - 44, 86, WIDTH // 2 + 44, 86), fill=(232, 192, 143, round(alpha * 0.68)), width=1)
    draw.text(
        ((WIDTH - support_width) // 2, 94),
        support,
        font=support_font,
        fill=(239, 226, 209, alpha),
        stroke_width=1,
        stroke_fill=(8, 17, 29, alpha),
    )
    return layer


def camera_state(progress: float) -> tuple[float, float, float]:
    for keyframe_index in range(len(CAMERA_KEYFRAMES) - 1):
        start = CAMERA_KEYFRAMES[keyframe_index]
        end = CAMERA_KEYFRAMES[keyframe_index + 1]
        if progress <= end[0]:
            segment_progress = (progress - start[0]) / (end[0] - start[0])
            eased_progress = segment_progress * segment_progress * (3 - 2 * segment_progress)
            zoom = start[1] + (end[1] - start[1]) * eased_progress
            pan_x = start[2] + (end[2] - start[2]) * eased_progress
            pan_y = start[3] + (end[3] - start[3]) * eased_progress
            return zoom, pan_x, pan_y
    return CAMERA_KEYFRAMES[-1][1:]


def rain_layer(frame_index: int) -> Image.Image:
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for drop_index in range(24):
        speed = 0.45 + (drop_index % 4) * 0.11
        drift = math.sin(frame_index * 0.015 + drop_index) * 3
        x = round((drop_index * 137 + frame_index * 0.1 + drift) % WIDTH)
        y = round((drop_index * 211 + frame_index * speed) % HEIGHT)
        length = 18 + (drop_index % 5) * 4
        opacity = 16 + (drop_index % 3) * 5
        draw.line((x, y, x - 2, y + length), fill=(190, 225, 245, opacity), width=1)
    return layer.filter(ImageFilter.GaussianBlur(0.65))


def main() -> None:
    if not AUDIO.exists():
        raise FileNotFoundError(f"Song not found: {AUDIO}")

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    probe = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(AUDIO)], capture_output=True, text=True
    )
    metadata = probe.stderr
    marker = "Duration: "
    if marker not in metadata:
        raise RuntimeError("Could not read the song duration from FFmpeg.")
    stamp = metadata.split(marker, 1)[1].split(",", 1)[0]
    hours, minutes, seconds = stamp.split(":")
    duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    scene_duration = duration / SCENE_COUNT
    total_frames = round(duration * FPS)
    scenes = make_photo_scenes()
    warm_scenes = make_photo_scenes(warm=True)
    vignette = make_vignette()
    grain = Image.effect_noise((WIDTH, HEIGHT), 24).convert("L")
    grain_layer = Image.new("RGB", (WIDTH, HEIGHT), (214, 198, 177))
    grain_alpha = Image.eval(grain, lambda value: max(0, min(13, round((value - 96) * 0.16))))
    grain_layer.putalpha(grain_alpha)
    previews: list[Image.Image] = []

    command = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", f"{WIDTH}x{HEIGHT}",
        "-framerate", str(FPS), "-i", "-", "-i", str(AUDIO),
        "-map", "0:v:0", "-map", "1:a:0", "-t", f"{duration:.3f}",
        "-vf", "fade=t=in:st=0:d=0.7", "-af", f"afade=t=out:st={duration - 0.8:.3f}:d=0.7",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(OUTPUT),
    ]
    encoder = subprocess.Popen(command, stdin=subprocess.PIPE)

    try:
        assert encoder.stdin is not None
        for frame_index in range(total_frames):
            time = frame_index / FPS
            scene_index = min(SCENE_COUNT - 1, int(time / scene_duration))
            progress = time / duration
            warm_progress = min(1.0, max(0.0, (progress - 0.52) / 0.44))
            warm_progress = warm_progress * warm_progress * (3 - 2 * warm_progress)
            zoom, pan_x, pan_y = camera_state(progress)
            frame_width, frame_height = round(WIDTH * zoom), round(HEIGHT * zoom)
            background = Image.blend(
                scenes[scene_index], warm_scenes[scene_index], warm_progress
            ).resize((frame_width, frame_height), Image.Resampling.LANCZOS)
            left = max(0, min(frame_width - WIDTH, (frame_width - WIDTH) // 2 + round(pan_x)))
            top = max(0, min(frame_height - HEIGHT, (frame_height - HEIGHT) // 2 + round(pan_y)))
            frame = background.crop((left, top, left + WIDTH, top + HEIGHT)).convert("RGBA")

            frame.alpha_composite(rain_layer(frame_index))
            frame.alpha_composite(vignette)
            frame.alpha_composite(grain_layer)
            lyric_cue = next(
                (cue for cue in LYRIC_CUES if cue[0] <= time < cue[1]), None
            )
            frame.alpha_composite(caption_layer(lyric_cue, time))
            frame.alpha_composite(brand_layer(time, duration))
            rgb = frame.convert("RGB")
            encoder.stdin.write(rgb.tobytes())
            if frame_index in {round((i + 0.5) * scene_duration * FPS) for i in range(SCENE_COUNT)}:
                previews.append(rgb.copy().resize((180, 320), Image.Resampling.LANCZOS))
    except BrokenPipeError:
        pass
    finally:
        if encoder.stdin:
            encoder.stdin.close()
    return_code = encoder.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)

    sheet = Image.new("RGB", (180 * 3, 320 * 2), (18, 23, 32))
    for index, preview in enumerate(previews):
        sheet.paste(preview, ((index % 3) * 180, (index // 3) * 320))
    sheet.save(STORYBOARD, quality=88)
    print(f"Created {OUTPUT.name} ({duration:.2f}s, {WIDTH}x{HEIGHT}, {FPS} fps)")
    print(f"Created {STORYBOARD.name} for review")


if __name__ == "__main__":
    main()
