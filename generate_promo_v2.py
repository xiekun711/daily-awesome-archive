"""
Daily Awesome Archive — 抖音宣传视频生成
30秒竖屏 (1080x1920)，适合抖音/视频号/小红书
用 imageio_ffmpeg 自带的 ffmpeg 编码
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os, subprocess, tempfile

OUTPUT = "/home/ubuntu/daily-awesome-archive/promo_video.mp4"
W, H = 1080, 1920
FPS = 24
DURATION = 30

# ============ 颜色方案 ============
BG_DARK = (10, 10, 35)
ACCENT_BLUE = (0, 150, 255)
ACCENT_PURPLE = (140, 60, 255)
ACCENT_CYAN = (0, 230, 230)
ACCENT_GOLD = (255, 200, 50)
WHITE = (255, 255, 255)
GRAY = (150, 150, 180)

# 找字体
import glob
font_bold = None
font_regular = None
for f in glob.glob("/usr/share/fonts/**/*.ttf", recursive=True):
    name = os.path.basename(f).lower()
    if font_bold is None and "bold" in name:
        font_bold = f
    if font_regular is None and ("regular" in name or "medium" in name):
        font_regular = f
if not font_bold:
    font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not font_regular:
    font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ffmpeg 路径
import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
print(f"FFmpeg: {FFMPEG}")
print(f"Font bold: {font_bold}")
print(f"Font regular: {font_regular}")


def draw_bg(draw, t=0):
    for y in range(H):
        ratio = y / H
        r = int(10 + 5 * ratio)
        g = int(10 + 15 * ratio)
        b = int(35 + 20 * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    np.random.seed(int(t * 10) % 1000)
    for _ in range(120):
        x, y = np.random.randint(0, W), np.random.randint(0, H)
        r = np.random.uniform(0.5, 2.0)
        a = int(np.random.uniform(60, 180))
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(a, a, a))

    for x in range(0, W, 100):
        draw.line([(x, 0), (x, H)], fill=(ACCENT_BLUE[0], ACCENT_BLUE[1], ACCENT_BLUE[2], 8))
    for y in range(0, H, 100):
        draw.line([(0, y), (W, y)], fill=(ACCENT_BLUE[0], ACCENT_BLUE[1], ACCENT_BLUE[2], 8))

    offset = int(t * 50) % (H + 200) - 100
    for i in range(3):
        y = offset + i * 300
        if 0 <= y < H:
            alpha = max(0, 60 - abs(y - H//2) // 10)
            draw.line([(0, y), (W, y)], fill=(ACCENT_BLUE[0], ACCENT_BLUE[1], ACCENT_BLUE[2], alpha))


def tw(draw, text, font):
    return draw.textbbox((0, 0), text, font=font)[2]


def make_frame(t):
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_bg(draw, t)

    if t < 7:
        _scene_title(draw)
    elif t < 15:
        _scene_howitworks(draw)
    elif t < 23:
        _scene_domains(draw)
    else:
        _scene_cta(draw)

    # 淡入淡出
    if t < 0.5:
        a = t / 0.5
        return (np.array(img) * a + np.zeros_like(np.array(img)) + np.array([10, 10, 35]) * (1 - a)).astype(np.uint8)
    if t > DURATION - 0.5:
        a = (DURATION - t) / 0.5
        return (np.array(img) * a + np.zeros_like(np.array(img)) + np.array([10, 10, 35]) * (1 - a)).astype(np.uint8)
    return np.array(img)


def _scene_title(draw):
    f1 = ImageFont.truetype(font_bold, 180)
    f2 = ImageFont.truetype(font_regular, 50)
    f3 = ImageFont.truetype(font_regular, 36)

    draw.rectangle([(100, 480), (980, 485)], fill=ACCENT_BLUE)

    y = 530
    for line in ["Daily", "Awesome", "Archive"]:
        w = tw(draw, line, f1)
        draw.text(((W-w)//2, y), line, font=f1, fill=WHITE)
        y += 175

    sub = "📅 每日 GitHub 优质项目精选归档"
    w = tw(draw, sub, f2)
    draw.text(((W-w)//2, y + 20), sub, font=f2, fill=GRAY)

    url = "github.com/xiekun711/daily-awesome-archive"
    w = tw(draw, url, f3)
    draw.text(((W-w)//2, 1450), url, font=f3, fill=ACCENT_CYAN)

    draw.rectangle([(100, 1520), (980, 1525)], fill=ACCENT_PURPLE)


def _scene_howitworks(draw):
    fb = ImageFont.truetype(font_bold, 68)
    fs = ImageFont.truetype(font_regular, 38)
    fd = ImageFont.truetype(font_regular, 30)
    fb2 = ImageFont.truetype(font_bold, 38)

    title = "⚙️ 全自动流程"
    w = tw(draw, title, fb)
    draw.text(((W-w)//2, 200), title, font=fb, fill=WHITE)

    steps = [
        ("08:00", "GitHub 搜索", "覆盖 5 大领域", ACCENT_BLUE),
        ("08:05", "AI 评分筛选", "多维评分 + 智能排序", ACCENT_CYAN),
        ("08:10", "自动归档", "Git commit → Push", ACCENT_PURPLE),
        ("每天", "飞书推送", "一眼看完今日精选", ACCENT_GOLD),
    ]

    y = 380
    for idx, (time_s, action, detail, color) in enumerate(steps):
        draw.text((150, y), time_s, font=fb2, fill=color)
        draw.text((340, y), "→", font=fs, fill=GRAY)
        draw.text((400, y), action, font=fs, fill=WHITE)
        draw.text((400, y + 50), detail, font=fd, fill=GRAY)
        if idx < 3:
            draw.line([(175, y + 55), (175, y + 125)], fill=color + (80,))
        y += 130

    tag = "🚀 每天自动执行，无需人工干预"
    w = tw(draw, tag, fs)
    draw.text(((W-w)//2, 1600), tag, font=fs, fill=ACCENT_GOLD)


def _scene_domains(draw):
    fb = ImageFont.truetype(font_bold, 68)
    fs = ImageFont.truetype(font_regular, 40)
    fe = ImageFont.truetype(font_regular, 55)
    fc = ImageFont.truetype(font_bold, 42)

    title = "🔍 每日搜索 5 大领域"
    w = tw(draw, title, fb)
    draw.text(((W-w)//2, 180), title, font=fb, fill=WHITE)

    domains = [
        ("🤖", "AI Agent / LLM 框架", ACCENT_BLUE),
        ("🧠", "AI 记忆 / 学习进化", ACCENT_CYAN),
        ("🔧", "开发工具 / 效率", ACCENT_PURPLE),
        ("⚡", "量化金融", ACCENT_GOLD),
        ("🔥", "新颖有趣", (255, 100, 100)),
    ]

    y = 300
    for emoji, name, color in domains:
        draw.text((180, y), emoji, font=fe, fill=color)
        draw.text((310, y + 5), name, font=fs, fill=WHITE)
        y += 120

    stats = "📊 每天精选 30+ 优质项目"
    w = tw(draw, stats, fc)
    draw.text(((W-w)//2, 1680), stats, font=fc, fill=ACCENT_GOLD)


def _scene_cta(draw):
    fn = ImageFont.truetype(font_bold, 100)
    fs = ImageFont.truetype(font_regular, 45)
    fm = ImageFont.truetype(font_regular, 38)
    fb = ImageFont.truetype(font_bold, 42)

    title = "🔥 开源免费"
    w = tw(draw, title, fn)
    draw.text(((W-w)//2, 350), title, font=fn, fill=ACCENT_GOLD)

    sub = "MIT License · 欢迎 Star & PR"
    w = tw(draw, sub, fs)
    draw.text(((W-w)//2, 500), sub, font=fs, fill=WHITE)

    url = "github.com/xiekun711/daily-awesome-archive"
    w = tw(draw, url, fm)
    draw.text(((W-w)//2, 750), url, font=fm, fill=ACCENT_CYAN)

    pages = "🌐 xiekun711.github.io/daily-awesome-archive"
    w = tw(draw, pages, fm)
    draw.text(((W-w)//2, 830), pages, font=fm, fill=ACCENT_CYAN)

    btn_w, btn_h = 520, 90
    btn_x = (W - btn_w) // 2
    btn_y = 1200
    draw.rounded_rectangle([(btn_x, btn_y), (btn_x+btn_w, btn_y+btn_h)], radius=30, fill=ACCENT_BLUE)
    btn_text = "⭐ 去 GitHub 点个 Star"
    w = tw(draw, btn_text, fb)
    draw.text(((W-w)//2, btn_y + 20), btn_text, font=fb, fill=WHITE)

    tag = "由 Hermes Agent 自动维护"
    w = tw(draw, tag, fm)
    draw.text(((W-w)//2, 1700), tag, font=fm, fill=GRAY)


# ============ 生成 ============
total_frames = int(DURATION * FPS)
print(f"Generating {total_frames} frames...")

frames = []
for i in range(total_frames):
    t = i / FPS
    frame = make_frame(t)
    frames.append(frame.tobytes())
    if (i + 1) % 120 == 0:
        print(f"  {i+1}/{total_frames} ({((i+1)/total_frames)*100:.0f}%)")

print("Encoding with ffmpeg...")

# 用 raw video 管道直接喂给 ffmpeg
cmd = [
    FFMPEG, '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{W}x{H}',
    '-pix_fmt', 'rgb24',
    '-r', str(FPS),
    '-i', '-',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-b:v', '4000k',
    '-pix_fmt', 'yuv420p',
    OUTPUT
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
for i, frame_bytes in enumerate(frames):
    proc.stdin.write(frame_bytes)
    if (i + 1) % 120 == 0:
        proc.stdin.flush()

proc.stdin.close()
proc.wait()

stderr = proc.stderr.read().decode()
size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
print(f"\n✅ Done! Video: {OUTPUT}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Duration: {DURATION}s @ {FPS}fps")
print(f"   FFmpeg exit code: {proc.returncode}")
if proc.returncode != 0:
    print(f"   Stderr: {stderr[:500]}")
