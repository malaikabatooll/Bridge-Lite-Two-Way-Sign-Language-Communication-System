import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import time
import os
from collections import deque

import camera
import recognizer
import speech
import emergency

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ---------- Bridge Lite theme ----------
BG = "#0A1218"
PANEL = "#101B22"
PANEL_2 = "#16232B"
SIGNAL = "#29E5C6"
SIGNAL_HOVER = "#20B8A0"
WARM = "#FF6B4A"
WARM_HOVER = "#E85A3D"
TEXT = "#F2F5F4"
MUTED = "#7C8B92"
BORDER = "#1E2A32"

FONT_DISPLAY = "Century Gothic"
FONT_BODY = "Segoe UI"
FONT_MONO = "Consolas"

KNOWN_WORDS = {"hello", "bye", "yes", "no", "help", "thank_you", "hospital", "water", "pain", "stop",
               "mother", "father", "think", "sick", "eat", "family", "friend", "more", "same", "work"}
SIGN_PHOTO_DIR = "assets/sign_photos"

last_spoken = None
last_spoken_time = 0
REPEAT_INTERVAL = 1.5
frame_times = deque(maxlen=15)


def draw_gauge(canvas, percent, urgent=False, size=140):
    canvas.delete("all")
    thickness = 12
    margin = thickness
    x0, y0, x1, y1 = margin, margin, size - margin, size - margin

    canvas.create_oval(x0, y0, x1, y1, outline=BORDER, width=thickness)
    extent = -3.6 * percent
    ring_color = WARM if urgent else SIGNAL
    canvas.create_arc(x0, y0, x1, y1, start=90, extent=extent, style="arc",
                       outline=ring_color, width=thickness)

    canvas.create_text(size / 2, size / 2 - 10, text=f"{percent:.0f}%",
                        font=(FONT_DISPLAY, 22, "bold"), fill=TEXT)
    label = "High" if percent >= 80 else "Medium" if percent >= 50 else "Low" if percent > 0 else ""
    canvas.create_text(size / 2, size / 2 + 18, text=label,
                        font=(FONT_MONO, 12), fill=ring_color)


def load_sign_photo(word, max_w=320, max_h=260):
    path = os.path.join(SIGN_PHOTO_DIR, f"{word}.png")
    if not os.path.exists(path):
        return None
    img = Image.open(path)
    img.thumbnail((max_w, max_h))
    return ImageTk.PhotoImage(img)


def start_gui():
    global last_spoken, last_spoken_time

    camera.start_camera()
    recognizer.init_recognizer()
    speech.init_speech()

    window = ctk.CTk()
    window.configure(fg_color=BG)
    window.title("Bridge Lite")
    window.geometry("1000x900")
    window.state("zoomed")

    header = ctk.CTkFrame(window, fg_color="transparent")
    header.pack(fill="x", padx=25, pady=(15, 5))

    title_frame = ctk.CTkFrame(header, fg_color="transparent")
    title_frame.pack(side="left")
    title_row = ctk.CTkFrame(title_frame, fg_color="transparent")
    title_row.pack(anchor="w")
    ctk.CTkLabel(title_row, text="Bridge ", font=(FONT_DISPLAY, 30, "bold"), text_color=TEXT).pack(side="left")
    ctk.CTkLabel(title_row, text="Lite", font=(FONT_DISPLAY, 30, "bold"), text_color=SIGNAL).pack(side="left")
    ctk.CTkLabel(title_frame, text="AI-Based Sign Language to Text & Voice",
                 font=(FONT_BODY, 13), text_color=MUTED).pack(anchor="w")

    ctk.CTkLabel(header, text="Live", font=(FONT_MONO, 13, "bold"),
                 text_color=SIGNAL).pack(side="right", padx=10)

    body = ctk.CTkFrame(window, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=25, pady=10)

    left_col = ctk.CTkScrollableFrame(body, fg_color="transparent")
    left_col.pack(side="left", fill="both", expand=True)

    right_col = ctk.CTkFrame(body, fg_color="transparent", width=260)
    right_col.pack(side="right", fill="y", padx=(15, 0))

    video_frame = ctk.CTkFrame(left_col, corner_radius=16, fg_color=PANEL, border_width=1, border_color=BORDER)
    video_frame.pack(fill="both", expand=True)
    ctk.CTkLabel(video_frame, text="Live Camera Feed", font=(FONT_DISPLAY, 14, "bold"), text_color=TEXT
                 ).pack(anchor="w", padx=15, pady=(12, 5))
    video_label = tk.Label(video_frame, bg=PANEL)
    video_label.pack(padx=10, pady=(0, 10))

    text_frame = ctk.CTkFrame(left_col, corner_radius=16, fg_color=PANEL, border_width=1, border_color=BORDER)
    text_frame.pack(fill="x", pady=(10, 0))
    text_header = ctk.CTkFrame(text_frame, fg_color="transparent")
    text_header.pack(fill="x", padx=15, pady=(10, 0))
    ctk.CTkLabel(text_header, text="Translated Text", font=(FONT_BODY, 13),
                 text_color=MUTED).pack(side="left")

    def speak_last():
        if last_spoken:
            speech.speak_text(last_spoken)

    ctk.CTkButton(text_header, text="Speak", width=30, fg_color="transparent",
                  hover_color=PANEL_2, text_color=SIGNAL, command=speak_last).pack(side="right")

    word_label = ctk.CTkLabel(text_frame, text="No hand detected", font=(FONT_DISPLAY, 36, "bold"), text_color=TEXT)
    word_label.pack(padx=15, pady=(0, 20))

    # ---------- Text -> Sign panel ----------
    t2s_frame = ctk.CTkFrame(left_col, corner_radius=16, fg_color=PANEL, border_width=1, border_color=BORDER)
    t2s_frame.pack(fill="x", pady=(10, 0))
    ctk.CTkLabel(t2s_frame, text="Text \u2192 Sign", font=(FONT_DISPLAY, 14, "bold"), text_color=TEXT
                 ).pack(anchor="w", padx=15, pady=(12, 5))

    t2s_input_row = ctk.CTkFrame(t2s_frame, fg_color="transparent")
    t2s_input_row.pack(fill="x", padx=15)

    text_entry = ctk.CTkEntry(t2s_input_row, placeholder_text="Type one of the 10 words (e.g. help)",
                               fg_color=PANEL_2, border_color=BORDER, text_color=TEXT,
                               placeholder_text_color=MUTED)
    text_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

    t2s_status = ctk.CTkLabel(t2s_frame, text="", font=(FONT_MONO, 12), text_color=MUTED)
    t2s_status.pack(anchor="w", padx=15, pady=(6, 0))

    sign_image_label = tk.Label(t2s_frame, bg=PANEL, text="Type a word above and press Show Sign",
                                 fg=MUTED, font=(FONT_BODY, 11), wraplength=280, justify="center")
    sign_image_label.pack(padx=15, pady=(6, 15))

    def on_show_sign():
        text = text_entry.get().strip().lower().replace(" ", "_")

        if text not in KNOWN_WORDS:
            sign_image_label.configure(image="", text="Not in vocabulary \u2014 10 known signs only", fg=WARM)
            sign_image_label.image = None
            t2s_status.configure(text="")
            return

        photo = load_sign_photo(text)
        if photo is not None:
            sign_image_label.configure(image=photo, text="")
            sign_image_label.image = photo
            t2s_status.configure(text=f"Showing sign for: {text.replace('_', ' ').upper()}", text_color=SIGNAL)
        else:
            sign_image_label.configure(image="", text=f'Photo not captured yet for "{text}"', fg=MUTED)
            sign_image_label.image = None
            t2s_status.configure(text="")

        speech.speak_text(text.replace("_", " "))

    ctk.CTkButton(t2s_input_row, text="Show Sign", command=on_show_sign, width=110,
                  fg_color=SIGNAL, hover_color=SIGNAL_HOVER, text_color=BG).pack(side="right")
    text_entry.bind("<Return>", lambda e: on_show_sign())
    # ---------- end Text -> Sign panel ----------

    result_frame = ctk.CTkFrame(right_col, corner_radius=16, fg_color=PANEL, border_width=1, border_color=BORDER)
    result_frame.pack(fill="x", pady=(0, 10))
    ctk.CTkLabel(result_frame, text="Recognition Result", font=(FONT_BODY, 13),
                 text_color=MUTED).pack(anchor="w", padx=15, pady=(10, 5))
    result_label = ctk.CTkLabel(result_frame, text="-", font=(FONT_DISPLAY, 24, "bold"), text_color=SIGNAL)
    result_label.pack(padx=15, pady=(0, 15))

    conf_frame = ctk.CTkFrame(right_col, corner_radius=16, fg_color=PANEL, border_width=1, border_color=BORDER)
    conf_frame.pack(fill="x", pady=(0, 10))
    ctk.CTkLabel(conf_frame, text="Confidence", font=(FONT_BODY, 13),
                 text_color=MUTED).pack(anchor="w", padx=15, pady=(10, 0))
    gauge_canvas = tk.Canvas(conf_frame, width=140, height=140, bg=PANEL, highlightthickness=0)
    gauge_canvas.pack(padx=15, pady=10)
    draw_gauge(gauge_canvas, 0)

    mode_frame = ctk.CTkFrame(right_col, corner_radius=16, fg_color=PANEL, border_width=1, border_color=BORDER)
    mode_frame.pack(fill="x", pady=(0, 10))
    ctk.CTkLabel(mode_frame, text="Mode", font=(FONT_BODY, 13),
                 text_color=MUTED).pack(anchor="w", padx=15, pady=(10, 5))
    ctk.CTkButton(mode_frame, text="Sign -> Text / Voice", fg_color=SIGNAL,
                  hover_color=SIGNAL, state="disabled",
                  text_color_disabled=BG).pack(fill="x", padx=15, pady=(0, 10))

    status_frame = ctk.CTkFrame(right_col, corner_radius=16, fg_color=PANEL, border_width=1, border_color=BORDER)
    status_frame.pack(fill="x")
    ctk.CTkLabel(status_frame, text="Status", font=(FONT_BODY, 13),
                 text_color=MUTED).pack(anchor="w", padx=15, pady=(10, 5))
    ctk.CTkLabel(status_frame, text="Camera: Connected", text_color=SIGNAL, font=(FONT_BODY, 12)).pack(anchor="w", padx=15)
    ctk.CTkLabel(status_frame, text="Speaker: Ready", text_color=SIGNAL, font=(FONT_BODY, 12)).pack(anchor="w", padx=15, pady=(0, 10))

    footer = ctk.CTkFrame(window, fg_color="transparent")
    footer.pack(fill="x", padx=25, pady=(0, 15))

    def clear_display():
        global last_spoken
        last_spoken = None
        word_label.configure(text="No hand detected", text_color=TEXT)
        result_label.configure(text="-", text_color=SIGNAL)
        draw_gauge(gauge_canvas, 0)

    ctk.CTkButton(footer, text="Speak", command=speak_last, width=110,
                  fg_color=SIGNAL, hover_color=SIGNAL_HOVER, text_color=BG).pack(side="left")
    ctk.CTkButton(footer, text="Clear", command=clear_display, fg_color=PANEL_2,
                  hover_color=BORDER, text_color=TEXT, width=110).pack(side="left", padx=(10, 0))

    ctk.CTkLabel(footer, text="Sign \u2194 Text & Voice (Two-Way)",
                 text_color=MUTED, font=(FONT_MONO, 11)).pack(side="left", expand=True)

    def on_closing(event=None):
        camera.release_camera()
        recognizer.close_recognizer()
        speech.close_speech()
        window.destroy()

    ctk.CTkButton(footer, text="Exit", fg_color=WARM, hover_color=WARM_HOVER,
                  text_color=TEXT, command=on_closing, width=110).pack(side="right")

    def update_frame():
        global last_spoken, last_spoken_time

        now = time.time()
        frame_times.append(now)
        fps = 0
        if len(frame_times) >= 2:
            fps = (len(frame_times) - 1) / (frame_times[-1] - frame_times[0])

        frame = camera.read_frame()
        if frame is not None:
            word, confidence = recognizer.recognize_frame(frame)
            urgent = bool(word) and emergency.is_emergency(word)

            now_time = time.time()
            if word and confidence > 70:
                if word != last_spoken or (now_time - last_spoken_time) >= REPEAT_INTERVAL:
                    if urgent:
                        emergency.play_alarm()
                    speech.speak_text(word)
                    last_spoken = word
                    last_spoken_time = now_time
            elif not word:
                last_spoken = None

            if word:
                display_text = ("EMERGENCY: " + word.upper()) if urgent else word.upper()
                accent = WARM if urgent else SIGNAL
                word_label.configure(text=display_text, text_color=TEXT if not urgent else WARM)
                result_label.configure(text=word.upper(), text_color=accent)
                draw_gauge(gauge_canvas, confidence, urgent=urgent)
            else:
                word_label.configure(text="No hand detected", text_color=TEXT)
                result_label.configure(text="-", text_color=SIGNAL)
                draw_gauge(gauge_canvas, 0)

            cv2.rectangle(frame, (frame.shape[1] - 110, 10), (frame.shape[1] - 10, 40), (43, 35, 22), -1)
            cv2.putText(frame, f"FPS: {fps:.0f}", (frame.shape[1] - 100, 32),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (244, 245, 242), 2)

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, (580, 360))
            pil_img = Image.fromarray(img_resized)
            tk_img = ImageTk.PhotoImage(image=pil_img)
            video_label.configure(image=tk_img)
            video_label.image = tk_img

        window.after(15, update_frame)

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.bind("<KeyPress-q>", on_closing)
    update_frame()
    window.mainloop()


if __name__ == "__main__":
    start_gui()
