"""
Daily Awesome Archive — 宣传视频
快编版：20秒 @ 15fps, 720x1280
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os, subprocess

OUTPUT = "/home/ubuntu/daily-awesome-archive/promo_video.mp4"
W, H = 720, 1280
FPS = 15
DURATION = 20

ACCENT_BLUE = (0, 150, 255)
ACCENT_PURPLE = (140, 60, 255)
ACCENT_CYAN = (0, 230, 230)
ACCENT_GOLD = (255, 200, 50)
WHITE = (255, 255, 255)
GRAY = (150, 150, 180)

import glob
font_b = None; font_r = None
for f in glob.glob("/usr/share/fonts/**/*.ttf", recursive=True):
    n = os.path.basename(f).lower()
    if font_b is None and "bold" in n: font_b = f
    if font_r is None and ("regular" in n or "medium" in n): font_r = f
if not font_b: font_b = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if not font_r: font_r = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

import imageio_ffmpeg
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
print(f"FFmpeg: {FFMPEG}")


def bg(draw, t):
    for y in range(H):
        r = int(10 + 5*y/H); g = int(10 + 15*y/H); b = int(35 + 20*y/H)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    np.random.seed(int(t*10)%997)
    for _ in range(80):
        x,y = np.random.randint(0,W), np.random.randint(0,H)
        r = np.random.uniform(0.5,1.5)
        draw.ellipse([x-r,y-r,x+r,y+r], fill=(60,60,60))
    off = int(t*40)*(H+200)-100
    for i in range(2):
        y = off + i*300
        if 0<=y<H:
            draw.line([(0,y),(W,y)], fill=ACCENT_BLUE+(40,))


def tw(d, t, f):
    return d.textbbox((0,0),t,font=f)[2]


def frame(t):
    img = Image.new("RGB", (W,H), (10,10,35))
    d = ImageDraw.Draw(img)
    bg(d, t)

    # fade
    fade = 1.0
    if t < 0.5: fade = t/0.5
    if t > DURATION-0.5: fade = (DURATION-t)/0.5

    fn = dict(zip(
        [8, 6.5, 5.5, 4.5, 4, 3.5, 3],
        [ImageFont.truetype(font_b, s) if s>=3 else ImageFont.truetype(font_r,s) for s in [8,6.5,5.5,4.5,4,3.5,3]]
    ))
    f100 = ImageFont.truetype(font_b, int(100*W/1080))
    f70 = ImageFont.truetype(font_b, int(68*W/1080))
    f40 = ImageFont.truetype(font_r, int(40*W/1080))
    f35 = ImageFont.truetype(font_r, int(35*W/1080))
    f30 = ImageFont.truetype(font_r, int(30*W/1080))
    f45 = ImageFont.truetype(font_b, int(42*W/1080))
    f55 = ImageFont.truetype(font_r, int(55*W/1080))

    if t < 6:
        # 标题
        d.rectangle([(70, 320),(W-70, 323)], fill=ACCENT_BLUE)
        y = 370
        for line in ["Daily","Awesome","Archive"]:
            w = tw(d,line,f100); d.text(((W-w)//2,y),line,font=f100,fill=WHITE); y+=120
        sub = "📅 每日 GitHub 优质项目精选归档"
        w = tw(d,sub,f40); d.text(((W-w)//2,y+15),sub,font=f40,fill=GRAY)
        url = "github.com/xiekun711/daily-awesome-archive"
        w = tw(d,url,f35); d.text(((W-w)//2,1000),url,font=f35,fill=ACCENT_CYAN)
        d.rectangle([(70,1060),(W-70,1063)], fill=ACCENT_PURPLE)

    elif t < 10:
        # 5 领域
        d.text(((W-tw(d,"🔍 每日搜索 5 大领域",f70))//2,130),"🔍 每日搜索 5 大领域",font=f70,fill=WHITE)
        items = [("🤖","AI Agent / LLM 框架",ACCENT_BLUE),("🧠","AI 记忆 / 学习",ACCENT_CYAN),
                 ("🔧","开发工具 / 效率",ACCENT_PURPLE),("⚡","量化金融",ACCENT_GOLD),
                 ("🔥","新颖有趣",(255,100,100))]
        y = 250
        for em,nm,cl in items:
            d.text((120,y),em,font=f55,fill=cl)
            d.text((210,y+5),nm,font=f40,fill=WHITE)
            y+=95
        d.text(((W-tw(d,"📊 每天精选 30+ 优质项目",f45))//2,1100),"📊 每天精选 30+ 优质项目",font=f45,fill=ACCENT_GOLD)

    elif t < 14:
        # 流程
        d.text(((W-tw(d,"⚙️ 自动流程",f70))//2,120),"⚙️ 自动流程",font=f70,fill=WHITE)
        steps = [("08:00","GitHub搜索","5 大领域",ACCENT_BLUE),("08:05","AI评分筛选","多维评分",ACCENT_CYAN),
                 ("08:10","自动归档","git push",ACCENT_PURPLE),("每天","飞书推送","一眼看完",ACCENT_GOLD)]
        y = 260
        for idx,(tm,act,de,cl) in enumerate(steps):
            fb = ImageFont.truetype(font_b, int(36*W/1080))
            d.text((100,y),tm,font=fb,fill=cl)
            d.text((250,y),"→",font=f35,fill=GRAY)
            d.text((300,y),act,font=f35,fill=WHITE)
            d.text((300,y+40),de,font=f30,fill=GRAY)
            if idx<3: d.line([(120,y+45),(120,y+90)],fill=cl+(60,))
            y+=95
        d.text(((W-tw(d,"🚀 全自动 · 无需人工",f35))//2,1050),"🚀 全自动 · 无需人工",font=f35,fill=ACCENT_GOLD)

    else:
        # CTA
        d.text(((W-tw(d,"🔥 开源免费",f100))//2,250),"🔥 开源免费",font=f100,fill=ACCENT_GOLD)
        d.text(((W-tw(d,"MIT License · 欢迎 Star & PR",f40))//2,400),"MIT License · 欢迎 Star & PR",font=f40,fill=WHITE)
        url = "github.com/xiekun711/daily-awesome-archive"
        d.text(((W-tw(d,url,f35))//2,600),url,font=f35,fill=ACCENT_CYAN)
        pages = "🌐 xiekun711.github.io/daily-awesome-archive"
        d.text(((W-tw(d,pages,f35))//2,670),pages,font=f35,fill=ACCENT_CYAN)
        bw, bh = 400, 70
        bx = (W-bw)//2; by = 850
        d.rounded_rectangle([(bx,by),(bx+bw,by+bh)], radius=20, fill=ACCENT_BLUE)
        bt = "⭐ 去 GitHub 点个 Star"
        d.text(((W-tw(d,bt,f45))//2,by+18),bt,font=f45,fill=WHITE)
        d.text(((W-tw(d,"由 Hermes Agent 自动维护",f30))//2,1150),"由 Hermes Agent 自动维护",font=f30,fill=GRAY)

    # 应用淡入淡出
    arr = np.array(img).astype(np.float32)
    if fade < 1:
        bgc = np.array([10,10,35], dtype=np.float32)
        arr = arr * fade + bgc * (1 - fade)
    return arr.astype(np.uint8)


# ============ 生成 ============
total = int(DURATION * FPS)
print(f"Generating {total} frames at {W}x{H}...")

raw = bytearray()
for i in range(total):
    f = frame(i / FPS)
    raw.extend(f.tobytes())
    if (i+1)%60 == 0:
        print(f"  {i+1}/{total}")

print("Encoding...")
cmd = [FFMPEG,'-y','-f','rawvideo','-vcodec','rawvideo',
       '-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(FPS),'-i','-',
       '-c:v','libx264','-preset','fast','-b:v','3000k','-pix_fmt','yuv420p',OUTPUT]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
proc.stdin.write(raw)
proc.stdin.close()
proc.wait()

sz = os.path.getsize(OUTPUT)/1024/1024
print(f"\n✅ Done! {OUTPUT} ({sz:.1f}MB, {DURATION}s)")
