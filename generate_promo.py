"""
Daily Awesome Archive — 抖音宣传视频生成
30秒竖屏 (1080x1920)，适合抖音/视频号/小红书
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import moviepy as mp
import os

OUTPUT = "/home/ubuntu/daily-awesome-archive/promo_video.mp4"
W, H = 1080, 1920  # 竖屏
FPS = 24
DURATION = 30  # 30 秒

# ============ 颜色方案 ============
BG_DARK = (10, 10, 35)
ACCENT_BLUE = (0, 150, 255)
ACCENT_PURPLE = (140, 60, 255)
ACCENT_CYAN = (0, 230, 230)
ACCENT_GOLD = (255, 200, 50)
WHITE = (255, 255, 255)
GRAY = (150, 150, 180)

# 找字体
font_bold = None
font_regular = None
for root, dirs, files in os.walk("/usr/share/fonts"):
    for f in files:
        if f.endswith(".ttf"):
            path = os.path.join(root, f)
            if font_bold is None and ("bold" in f.lower() or "Bold" in f):
                font_bold = path
            if font_regular is None and ("regular" in f.lower() or "Regular" in f):
                font_regular = path
if not font_bold:
    font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not font_regular:
    font_regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def make_frame(t):
    """核心：根据时间 t 生成一帧 RGB 图像"""
    # 第几幕
    if t < 7:
        return scene_title(t)
    elif t < 15:
        return scene_howitworks(t - 7)
    elif t < 23:
        return scene_domains(t - 15)
    else:
        return scene_cta(t - 23)


def draw_bg(draw, w=W, h=H, t=0):
    """背景：渐变 + 星星 + 网格 + 线条"""
    # 渐变
    for y in range(h):
        ratio = y / h
        r = int(10 + 5 * ratio)
        g = int(10 + 15 * ratio)
        b = int(35 + 20 * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # 星星
    np.random.seed(int(t * 10) % 1000)
    for _ in range(120):
        x = np.random.randint(0, w)
        y = np.random.randint(0, h)
        r = np.random.uniform(0.5, 2.0)
        a = int(np.random.uniform(60, 180))
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(a, a, a))

    # 网格线
    for x in range(0, w, 100):
        draw.line([(x, 0), (x, h)], fill=(ACCENT_BLUE[0], ACCENT_BLUE[1], ACCENT_BLUE[2], 8))
    for y in range(0, h, 100):
        draw.line([(0, y), (w, y)], fill=(ACCENT_BLUE[0], ACCENT_BLUE[1], ACCENT_BLUE[2], 8))

    # 动感线条
    offset = int(t * 50) % (h + 200) - 100
    for i in range(3):
        y = offset + i * 300
        if 0 <= y < h:
            alpha = max(0, 60 - abs(y - h//2) // 10)
            for dx in range(-2, 3, 1):
                draw.line([(0, y + dx), (w, y + dx)], fill=(ACCENT_BLUE[0], ACCENT_BLUE[1], ACCENT_BLUE[2], alpha))


def tw(draw, text, font):
    """文本宽度"""
    return draw.textbbox((0, 0), text, font=font)[2]


def scene_title(t):
    """开场：标题"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_bg(draw, t=t)

    f1 = ImageFont.truetype(font_bold, 180)
    f2 = ImageFont.truetype(font_regular, 50)
    f3 = ImageFont.truetype(font_regular, 36)

    # 上横线
    draw.rectangle([(100, 480), (980, 485)], fill=ACCENT_BLUE)

    # 主标题
    title_lines = ["Daily", "Awesome", "Archive"]
    y = 530
    for line in title_lines:
        w = tw(draw, line, f1)
        draw.text(((W-w)//2, y), line, font=f1, fill=WHITE)
        y += 175

    # 副标题
    sub = "📅 每日 GitHub 优质项目精选归档"
    w = tw(draw, sub, f2)
    draw.text(((W-w)//2, y + 20), sub, font=f2, fill=GRAY)

    # GitHub 地址
    url = "github.com/xiekun711/daily-awesome-archive"
    w = tw(draw, url, f3)
    draw.text(((W-w)//2, 1450), url, font=f3, fill=ACCENT_CYAN)

    # 下横线
    draw.rectangle([(100, 1520), (980, 1525)], fill=ACCENT_PURPLE)

    return np.array(img)


def scene_howitworks(t):
    """工作原理"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_bg(draw, t=t)

    fb = ImageFont.truetype(font_bold, 70)
    fs = ImageFont.truetype(font_regular, 38)
    fd = ImageFont.truetype(font_regular, 30)

    # 标题
    title = "⚙️ 全自动流程"
    w = tw(draw, title, fb)
    draw.text(((W-w)//2, 200), title, font=fb, fill=WHITE)

    # 步骤
    steps = [
        ("08:00", "GitHub 搜索", "覆盖 5 大领域", ACCENT_BLUE),
        ("08:05", "AI 评分筛选", "多维评分 + 智能排序", ACCENT_CYAN),
        ("08:10", "自动归档", "Git commit → Push", ACCENT_PURPLE),
        ("每天", "飞书推送", "一眼看完今日精选", ACCENT_GOLD),
    ]

    y = 380
    for time_s, action, detail, color in steps:
        # 时间
        draw.text((150, y), time_s, font=ImageFont.truetype(font_bold, 38), fill=color)
        # 箭头
        draw.text((340, y), "→", font=fs, fill=GRAY)
        # 动作
        draw.text((400, y), action, font=fs, fill=WHITE)
        # 详情
        draw.text((400, y + 50), detail, font=fd, fill=GRAY)
        # 竖线
        if steps.index((time_s, action, detail, color)) < 3:
            draw.line([(175, y + 55), (175, y + 125)], fill=color + (80,))
        y += 130

    # 底部
    tag = "🚀 每天自动执行，无需人工干预"
    w = tw(draw, tag, fs)
    draw.text(((W-w)//2, 1600), tag, font=fs, fill=ACCENT_GOLD)

    return np.array(img)


def scene_domains(t):
    """搜索领域"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_bg(draw, t=t)

    fb = ImageFont.truetype(font_bold, 70)
    fs = ImageFont.truetype(font_regular, 40)
    fd = ImageFont.truetype(font_regular, 32)

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

    fe = ImageFont.truetype(font_regular, 55)
    y = 300
    for emoji, name, color in domains:
        draw.text((180, y), emoji, font=fe, fill=color)
        draw.text((310, y + 5), name, font=fs, fill=WHITE)
        y += 120

    # 统计
    fc = ImageFont.truetype(font_bold, 42)
    stats = "📊 每天精选 30+ 优质项目"
    w = tw(draw, stats, fc)
    draw.text(((W-w)//2, 1680), stats, font=fc, fill=ACCENT_GOLD)

    return np.array(img)


def scene_cta(t):
    """结尾：行动号召"""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)
    draw_bg(draw, t=t)

    fn = ImageFont.truetype(font_bold, 100)
    fs = ImageFont.truetype(font_regular, 45)
    fm = ImageFont.truetype(font_regular, 38)

    # 标题
    title = "🔥 开源免费"
    w = tw(draw, title, fn)
    draw.text(((W-w)//2, 350), title, font=fn, fill=ACCENT_GOLD)

    # MIT
    sub = "MIT License · 欢迎 Star & PR"
    w = tw(draw, sub, fs)
    draw.text(((W-w)//2, 500), sub, font=fs, fill=WHITE)

    # GitHub URL
    url = "github.com/xiekun711/daily-awesome-archive"
    w = tw(draw, url, fm)
    draw.text(((W-w)//2, 750), url, font=fm, fill=ACCENT_CYAN)

    # 在线预览
    pages = "🌐 xiekun711.github.io/daily-awesome-archive"
    w = tw(draw, pages, fm)
    draw.text(((W-w)//2, 830), pages, font=fm, fill=ACCENT_CYAN)

    # 按钮
    btn_w, btn_h = 520, 90
    btn_x = (W - btn_w) // 2
    btn_y = 1200
    draw.rounded_rectangle([(btn_x, btn_y), (btn_x+btn_w, btn_y+btn_h)], radius=30, fill=ACCENT_BLUE)
    btn_text = "⭐ 去 GitHub 点个 Star"
    fb = ImageFont.truetype(font_bold, 42)
    w = tw(draw, btn_text, fb)
    draw.text(((W-w)//2, btn_y + 20), btn_text, font=fb, fill=WHITE)

    # 署名
    tag = "由 Hermes Agent 自动维护"
    w = tw(draw, tag, fm)
    draw.text(((W-w)//2, 1700), tag, font=fm, fill=GRAY)

    return np.array(img)


# ============ 生成视频 ============
print(f"Generating video: {DURATION}s @ {FPS}fps, {W}x{H}")
print(f"Fonts: bold={font_bold}, regular={font_regular}")

# 先生成所有帧，避免 MoviePy 的 frame 方向问题
print("Pre-generating frames...")
frames = []
total_frames = int(DURATION * FPS)
for i in range(total_frames):
    t = i / FPS
    frame = make_frame(t)
    frames.append(frame)
    if (i + 1) % 120 == 0:
        print(f"  {i+1}/{total_frames} frames... ({((i+1)/total_frames)*100:.0f}%)")

print("Creating video from frames...")
clip = mp.ImageSequenceClip(frames, fps=FPS)

print("Writing MP4...")
clip.write_videofile(
    OUTPUT,
    fps=FPS,
    codec="libx264",
    audio=False,
    preset="fast",
    bitrate="4000k",
    threads=4,
)

size_mb = os.path.getsize(OUTPUT) / 1024 / 1024
print(f"\n✅ Done! Video saved to: {OUTPUT}")
print(f"   Size: {size_mb:.1f} MB")
print(f"   Duration: {DURATION}s")
print(f"   Resolution: {W}x{H}")
