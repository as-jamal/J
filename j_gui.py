import customtkinter as ctk
import tkinter as tk
import threading
import random
import math
import psutil
from datetime import datetime

try:
    import j_engine
except ImportError:
    class DummyEngine:
        def stop(self):
            pass

    class MockJEngine:
        def __init__(self):
            self.memory = {"status": "active", "version": "3.0.0"}
            self.engine = DummyEngine()

        def process_command(self, cmd):
            if "artificial intelligence" in cmd.lower():
                return (
                    "Artificial Intelligence enables machines to process information, "
                    "learn from experience, and perform complex cognitive tasks."
                )
            return f"Processed command: '{cmd}'. J is active and ready."

        def listen(self, timeout=5, phrase_time_limit=8):
            return "Hello J"

        def speak(self, text):
            pass

    j_engine = MockJEngine()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# -----------------------------------------------------
# CRIMSON RED THEME COLOR SYSTEM
# -----------------------------------------------------
BG = "#050608"              # Deep dark background
SIDEBAR_BG = "#07080b"      # Sidebar container
PANEL_BG = "#080a0e"        # Workspace & Chat panel fill
PANEL_BORDER = "#151822"    # Dark panel border
CARD_BG = "#0a0c12"         # Stat cards background
CARD_BORDER = "#181b28"     # Stat cards border

TEXT_WHITE = "#ffffff"      # Primary white text
TEXT_LIGHT = "#e2e8f0"      # Light off-white text
TEXT_MUTED = "#64748b"      # Muted slate text
TEXT_DIM = "#475569"        # Dim subtext

# Vibrant Crimson Red Palette
RED_PRIMARY = "#ff1e42"     # Vibrant Crimson Red primary accent
RED_GLOW = "#ff385c"        # Bright Crimson Red glow
RED_DARK = "#99001c"        # Deep Crimson container border
RED_CONTAINER = "#1a080c"   # Dark Crimson background fill
PURPLE = "#a855f7"          # RAM Accent
BLUE = "#3b82f6"            # Storage Accent
GREEN = "#00e676"           # Battery / Network Green accent


class JApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("J • Personal AI Assistant")
        self.geometry("1480x880")
        self.minsize(1150, 750)
        self.configure(fg_color=BG)

        self.running = True
        self.listening = False
        self.particles = []
        self.orb_phase = 0.0
        self.eq_phase = 0.0

        # AI Visualizer Dynamic State: "READY", "LISTENING", "THINKING", "SPEAKING"
        self.ai_state = "READY"

        self.create_layout()
        self.create_sidebar()
        self.create_topbar()
        self.create_workspace()
        self.create_chat_panel()
        self.create_bottom_stats()
        self.create_particles()

        self.update_system_stats()
        self.animate_visualizer()

        # Normal initial greeting
        self.add_chat("J", "Hello! I am J. How can I help you today?", assistant=True)

    # -----------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------

    def create_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(
            self, width=220, corner_radius=0, fg_color=SIDEBAR_BG
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.main = ctk.CTkFrame(
            self, corner_radius=0, fg_color=BG
        )
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(0, weight=0)  # Topbar
        self.main.grid_rowconfigure(1, weight=1)  # Workspace + Chat
        self.main.grid_rowconfigure(2, weight=0)  # Bottom Stats
        self.main.grid_columnconfigure(0, weight=1)

    # -----------------------------------------------------
    # SIDEBAR
    # -----------------------------------------------------

    def create_sidebar(self):
        self.sidebar.grid_rowconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(1, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=0)

        # Header Logo "J" in Crimson Red
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=22, pady=(22, 15), sticky="w")

        ctk.CTkLabel(
            logo_frame,
            text="J",
            font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold"),
            text_color=RED_PRIMARY
        ).pack()

        # Navigation Items
        nav = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav.grid(row=1, column=0, padx=10, pady=10, sticky="new")

        nav_items = [
            ("⌂", "Home"),
            ("💬", "Chat"),
            ("📊", "System"),
            (">_", "Commands"),
            ("🧠", "Memory"),
            ("⚙", "Settings"),
            ("ⓘ", "About J")
        ]

        self.nav_buttons = []

        for icon, text in nav_items:
            button = ctk.CTkButton(
                nav,
                text=f"  {icon}   {text}",
                height=44,
                anchor="w",
                corner_radius=12,
                fg_color="transparent",
                hover_color="#141724",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=14),
                command=lambda t=text: self.navigation_clicked(t)
            )
            button.pack(fill="x", pady=3)
            self.nav_buttons.append(button)

        # Active tab styling in Crimson Red
        self.nav_buttons[0].configure(
            fg_color=RED_CONTAINER,
            border_width=1,
            border_color=RED_DARK,
            text_color=RED_PRIMARY,
            font=ctk.CTkFont(size=14, weight="bold")
        )

        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.grid(row=2, column=0, padx=16, pady=20, sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)

        self.voice_mode_button = ctk.CTkButton(
            bottom,
            text="📊  VOICE MODE",
            height=46,
            corner_radius=12,
            fg_color=RED_CONTAINER,
            border_width=1,
            border_color=RED_DARK,
            hover_color="#2b0c12",
            text_color=RED_PRIMARY,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.start_voice
        )
        self.voice_mode_button.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            bottom,
            text="J 3.0.0",
            text_color="#454c5e",
            font=ctk.CTkFont(size=11)
        ).grid(row=1, column=0, pady=(12, 0), sticky="w", padx=4)

    # -----------------------------------------------------
    # TOP BAR (Clean Normal Top Bar without fake window controls)
    # -----------------------------------------------------

    def create_topbar(self):
        self.topbar = ctk.CTkFrame(
            self.main, height=56, corner_radius=0, fg_color=BG
        )
        self.topbar.grid(row=0, column=0, sticky="ew")
        self.topbar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.topbar,
            text="J  •  Personal AI Assistant",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=0, padx=20, pady=14, sticky="w")

        right = ctk.CTkFrame(self.topbar, fg_color="transparent")
        right.grid(row=0, column=1, padx=20, sticky="e")

        ctk.CTkLabel(
            right, text="● ONLINE", text_color=GREEN,
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left")

    # -----------------------------------------------------
    # WORKSPACE & CHAT
    # -----------------------------------------------------

    def create_workspace(self):
        self.workspace_frame = ctk.CTkFrame(
            self.main, fg_color="transparent"
        )
        self.workspace_frame.grid(
            row=1, column=0, sticky="nsew",
            padx=16, pady=(0, 10)
        )

        self.workspace_frame.grid_columnconfigure(0, weight=1)
        self.workspace_frame.grid_columnconfigure(1, weight=0, minsize=420)
        self.workspace_frame.grid_rowconfigure(0, weight=1)

        self.center_area = ctk.CTkFrame(
            self.workspace_frame,
            fg_color=PANEL_BG,
            corner_radius=18,
            border_width=1,
            border_color=PANEL_BORDER
        )
        self.center_area.grid(
            row=0, column=0, sticky="nsew", padx=(0, 12)
        )

        self.center_area.grid_rowconfigure(0, weight=1)
        self.center_area.grid_rowconfigure(1, weight=0)
        self.center_area.grid_columnconfigure(0, weight=1)

        self.create_orb_area()

    # -----------------------------------------------------
    # DYNAMIC REALISTIC 3D ORB & VISUALIZER
    # -----------------------------------------------------

    def create_orb_area(self):
        self.orb_area = ctk.CTkFrame(
            self.center_area, fg_color="transparent"
        )
        self.orb_area.grid(row=0, column=0, sticky="nsew")

        self.orb_area.grid_rowconfigure(0, weight=1)
        self.orb_area.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.orb_area,
            bg=PANEL_BG,
            highlightthickness=0,
            bd=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Dynamic Status Label
        self.status_label = ctk.CTkLabel(
            self.orb_area,
            text="J IS READY",
            text_color=RED_PRIMARY,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.status_label.place(relx=0.5, rely=0.74, anchor="center")

        self.hint_label = ctk.CTkLabel(
            self.orb_area,
            text="Press microphone or type a command",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12)
        )
        self.hint_label.place(relx=0.5, rely=0.78, anchor="center")

        # Equalizer Waveform canvas below status
        self.eq_canvas = tk.Canvas(
            self.orb_area,
            width=180,
            height=20,
            bg=PANEL_BG,
            highlightthickness=0,
            bd=0
        )
        self.eq_canvas.place(relx=0.5, rely=0.82, anchor="center")

        # Floating Bottom Dock Controls
        controls = ctk.CTkFrame(
            self.orb_area,
            width=360,
            height=66,
            corner_radius=33,
            fg_color="#0c0e14",
            border_width=1,
            border_color="#1c1f2c"
        )
        controls.place(relx=0.5, rely=0.91, anchor="center")
        controls.pack_propagate(False)

        # 1. Speaker button
        ctk.CTkButton(
            controls, text="🔊", width=55, height=46,
            fg_color="transparent", hover_color="#181b28",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=18),
            command=self.test_speaker
        ).place(x=15, y=10)

        # 2. Focus / Scan button
        ctk.CTkButton(
            controls, text="🔲", width=55, height=46,
            fg_color="transparent", hover_color="#181b28",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=18)
        ).place(x=75, y=10)

        # 3. Center Mic Button (Glowing circular red mic button)
        self.mic_button = ctk.CTkButton(
            controls, text="🎙", width=62, height=54,
            corner_radius=31, fg_color=RED_CONTAINER,
            hover_color="#360f15", border_width=1,
            border_color=RED_PRIMARY, text_color=RED_PRIMARY,
            font=ctk.CTkFont(size=22),
            command=self.start_voice
        )
        self.mic_button.place(relx=0.5, rely=0.5, anchor="center")

        # 4. Keyboard button
        ctk.CTkButton(
            controls, text="⌨", width=55, height=46,
            fg_color="transparent", hover_color="#181b28",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=18),
            command=self.focus_input
        ).place(x=230, y=10)

        # 5. Equalizer button
        ctk.CTkButton(
            controls, text="📊", width=55, height=46,
            fg_color="transparent", hover_color="#181b28",
            text_color=TEXT_MUTED, font=ctk.CTkFont(size=18)
        ).place(x=290, y=10)

    def create_particles(self):
        self.particles.clear()

        # Generate 900 3D spherical mesh particles with harmonic attributes
        for _ in range(900):
            u = random.uniform(0, math.tau)
            v = random.uniform(0, math.pi)
            r0 = random.uniform(105, 185)

            self.particles.append({
                "u": u,
                "v": v,
                "r0": r0,
                "speed_u": random.uniform(0.002, 0.008),
                "speed_v": random.uniform(0.001, 0.005),
                "size": random.choice([1, 1, 1.5, 2, 2.5])
            })

    def animate_visualizer(self):
        if not self.running:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 10 or height <= 10:
            self.after(30, self.animate_visualizer)
            return

        self.canvas.delete("all")

        cx = width * 0.50
        cy = height * 0.40

        # Adjust simulation dynamics based on current AI state (READY, LISTENING, THINKING, SPEAKING)
        if self.ai_state == "LISTENING":
            speed_mult = 1.8
            wave_amp = 36.0
            freq1, freq2 = 5.0, 3.0
            pulse_breath = math.sin(self.orb_phase * 3.0) * 15
        elif self.ai_state == "THINKING":
            speed_mult = 2.4
            wave_amp = 24.0
            freq1, freq2 = 4.0, 6.0
            pulse_breath = math.cos(self.orb_phase * 2.0) * 10
        elif self.ai_state == "SPEAKING":
            speed_mult = 1.4
            wave_amp = 30.0
            freq1, freq2 = 3.5, 2.5
            pulse_breath = math.sin(self.orb_phase * 2.5) * 18
        else:  # READY
            speed_mult = 1.0
            wave_amp = 18.0
            freq1, freq2 = 2.5, 2.0
            pulse_breath = math.sin(self.orb_phase) * 6

        self.orb_phase += 0.035 * speed_mult
        self.eq_phase += 0.12 * speed_mult

        # Outer subtle glowing circular boundary
        self.canvas.create_oval(
            cx - 210, cy - 210,
            cx + 210, cy + 210,
            outline="#121522",
            width=1
        )

        # Sort particles by projected Z for 3D depth layering
        rendered_particles = []

        rot_a = self.orb_phase * 0.4

        for p in self.particles:
            p["u"] += p["speed_u"] * speed_mult
            p["v"] += p["speed_v"] * speed_mult

            u = p["u"]
            v = p["v"]

            # Multi-harmonic surface distortion wave function
            w1 = math.sin(freq1 * u + self.orb_phase) * math.cos(freq2 * v - self.orb_phase * 0.8)
            w2 = math.sin(2.0 * u * v + self.orb_phase * 1.5) * 0.3
            wave = (w1 + w2) * wave_amp

            r = p["r0"] + wave + pulse_breath

            # 3D Coordinates
            x3d = r * math.sin(v) * math.cos(u)
            y3d = r * math.sin(v) * math.sin(u)
            z3d = r * math.cos(v)

            # Rotate around Y axis
            xr = x3d * math.cos(rot_a) + z3d * math.sin(rot_a)
            yr = y3d
            zr = -x3d * math.sin(rot_a) + z3d * math.cos(rot_a)

            # Perspective scale
            scale = 0.72 + (zr + 200) / 450.0

            x = cx + xr * scale
            y = cy + yr * scale * 0.85

            rendered_particles.append((zr, x, y, yr, scale, p["size"]))

        # Sort back to front
        rendered_particles.sort(key=lambda item: item[0])

        for zr, x, y, yr, scale, p_size in rendered_particles:
            # Color gradient: Top/Front = Vibrant Crimson Red, Core/Bottom = Deep Burgundy & Violet
            normalized_y = (yr + 180) / 360.0
            normalized_y = max(0.0, min(1.0, normalized_y))

            if self.ai_state == "THINKING":
                # Shifting Crimson to Violet morph
                r_c = int(255 * (1 - normalized_y * 0.4))
                g_c = int(20 * (1 - normalized_y))
                b_c = int(80 + normalized_y * 175)
            elif self.ai_state == "LISTENING":
                # High energy Coral Crimson
                r_c = 255
                g_c = int(30 + normalized_y * 140)
                b_c = int(60 + normalized_y * 80)
            else:
                # Vibrant Crimson Red (#ff1e42 to #800020)
                r_c = int(255 - normalized_y * 120)
                g_c = int(30 * (1 - normalized_y))
                b_c = int(60 * (1 - normalized_y))

            color_hex = f"#{r_c:02x}{g_c:02x}{b_c:02x}"
            size = max(1, int(p_size * scale))

            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=color_hex,
                outline=""
            )

        # Central glowing "J" logo
        self.canvas.create_text(
            cx, cy - 2,
            text="J",
            fill=RED_PRIMARY,
            font=("Segoe UI", 72, "bold")
        )

        # Audio Equalizer Bars animation
        self.eq_canvas.delete("all")
        num_bars = 21
        bar_w = 4
        gap = 4

        for i in range(num_bars):
            bx = 5 + i * (bar_w + gap)

            if self.ai_state == "LISTENING":
                h = 5 + int(14 * abs(math.sin(self.eq_phase + i * 0.5)))
            elif self.ai_state == "SPEAKING":
                h = 4 + int(12 * abs(math.cos(self.eq_phase + i * 0.4)))
            elif self.ai_state == "THINKING":
                h = 3 + int(8 * abs(math.sin(self.eq_phase * 0.7 + i)))
            else:
                h = 3 + int(5 * abs(math.sin(self.eq_phase * 0.3 + i * 0.3)))

            by1 = 10 - h // 2
            by2 = 10 + h // 2

            self.eq_canvas.create_line(
                bx, by1, bx, by2,
                fill=RED_PRIMARY,
                width=bar_w
            )

        self.after(30, self.animate_visualizer)

    # -----------------------------------------------------
    # CHAT PANEL
    # -----------------------------------------------------

    def create_chat_panel(self):
        self.chat_panel = ctk.CTkFrame(
            self.workspace_frame,
            width=420,
            corner_radius=18,
            fg_color=PANEL_BG,
            border_width=1,
            border_color=PANEL_BORDER
        )
        self.chat_panel.grid(row=0, column=1, sticky="nsew")
        self.chat_panel.grid_propagate(False)

        self.chat_panel.grid_rowconfigure(1, weight=1)
        self.chat_panel.grid_columnconfigure(0, weight=1)

        # Header: CHAT & ONLINE indicator
        header = ctk.CTkFrame(
            self.chat_panel, height=54,
            fg_color="transparent"
        )
        header.grid(
            row=0, column=0, sticky="ew",
            padx=18, pady=(12, 0)
        )
        header.grid_columnconfigure(0, weight=1)

        left_hdr = ctk.CTkFrame(header, fg_color="transparent")
        left_hdr.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left_hdr, text="💬", text_color=RED_PRIMARY,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            left_hdr, text="CHAT", text_color=RED_PRIMARY,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="● ONLINE", text_color=GREEN,
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=0, column=1, sticky="e")

        # Scrollable Chat Container
        self.chat_scroll = ctk.CTkScrollableFrame(
            self.chat_panel, fg_color="transparent"
        )
        self.chat_scroll.grid(
            row=1, column=0, sticky="nsew",
            padx=8, pady=5
        )

        # Input Frame
        input_frame = ctk.CTkFrame(
            self.chat_panel,
            height=58,
            corner_radius=14,
            fg_color="#0c0e14",
            border_width=1,
            border_color="#1c1f2c"
        )
        input_frame.grid(
            row=2, column=0, sticky="ew",
            padx=14, pady=14
        )
        input_frame.grid_columnconfigure(0, weight=1)

        self.chat_entry = ctk.CTkEntry(
            input_frame,
            height=42,
            placeholder_text="Type your message...",
            fg_color="transparent",
            border_width=0,
            text_color=TEXT_WHITE,
            placeholder_text_color="#454c5e",
            font=ctk.CTkFont(size=13)
        )
        self.chat_entry.grid(
            row=0, column=0, sticky="ew",
            padx=(14, 0), pady=8
        )
        self.chat_entry.bind("<Return>", lambda event: self.send_text())

        # Send button with Crimson Red outline & arrow icon
        ctk.CTkButton(
            input_frame,
            text="➤",
            width=42,
            height=38,
            corner_radius=10,
            fg_color=RED_CONTAINER,
            hover_color="#360f15",
            border_width=1,
            border_color=RED_PRIMARY,
            text_color=RED_PRIMARY,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.send_text
        ).grid(row=0, column=1, padx=8, pady=8)

    def add_chat(self, sender, message, assistant=False):
        time_str = datetime.now().strftime("%I:%M %p").lstrip("0")

        row = ctk.CTkFrame(
            self.chat_scroll, fg_color="transparent"
        )
        row.pack(fill="x", pady=8, padx=6)

        if assistant:
            # Avatar badge with crimson red border and J logo
            ctk.CTkLabel(
                row, text="J", width=34, height=34,
                corner_radius=17, fg_color=RED_CONTAINER,
                border_width=1, border_color=RED_PRIMARY,
                text_color=RED_PRIMARY,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left", anchor="n", padx=(0, 10))

            msg_box = ctk.CTkFrame(row, fg_color="transparent")
            msg_box.pack(side="left", anchor="nw")

            ctk.CTkLabel(
                msg_box, text=message, justify="left",
                anchor="w", wraplength=260,
                fg_color="#12141c", corner_radius=14,
                border_width=1, border_color="#1c1f2c",
                text_color=TEXT_LIGHT,
                font=ctk.CTkFont(size=12),
                padx=14, pady=10
            ).pack(anchor="w")

            ctk.CTkLabel(
                msg_box, text=time_str, text_color=TEXT_DIM,
                font=ctk.CTkFont(size=10)
            ).pack(anchor="w", padx=4, pady=(4, 0))

        else:
            msg_box = ctk.CTkFrame(row, fg_color="transparent")
            msg_box.pack(side="right", anchor="ne")

            ctk.CTkLabel(
                msg_box, text=message, justify="left",
                anchor="e", wraplength=260,
                fg_color="#1f1838", corner_radius=14,
                border_width=1, border_color="#312659",
                text_color=TEXT_WHITE,
                font=ctk.CTkFont(size=12),
                padx=14, pady=10
            ).pack(anchor="e")

            ctk.CTkLabel(
                msg_box, text=f"{time_str}  ✓", text_color=TEXT_DIM,
                font=ctk.CTkFont(size=10)
            ).pack(anchor="e", padx=4, pady=(4, 0))

        self.after(100, self.scroll_chat)

    def scroll_chat(self):
        try:
            self.chat_scroll._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    # -----------------------------------------------------
    # BOTTOM SYSTEM STATS BAR
    # -----------------------------------------------------

    def create_bottom_stats(self):
        self.stats_bar = ctk.CTkFrame(
            self.main, height=95, fg_color="transparent"
        )
        self.stats_bar.grid(
            row=2, column=0, sticky="ew",
            padx=16, pady=(0, 16)
        )

        for i in range(5):
            self.stats_bar.grid_columnconfigure(i, weight=1)

        self.cpu_card = self.create_stat_card_ui(
            0, "CPU USAGE", "🔲", "--%", RED_PRIMARY, None
        )
        self.ram_card = self.create_stat_card_ui(
            1, "RAM USAGE", "🎛", "--%", PURPLE, "-- GB / -- GB"
        )
        self.storage_card = self.create_stat_card_ui(
            2, "STORAGE", "💾", "--%", BLUE, "-- GB / -- GB"
        )
        self.battery_card = self.create_stat_card_ui(
            3, "BATTERY", "🔋", "--%", GREEN, "Status"
        )
        self.network_card = self.create_stat_card_ui(
            4, "NETWORK", "📶", "Connected", GREEN, "Ping: 18 ms"
        )

    def create_stat_card_ui(self, col, title, icon, value_text, accent_color, subtext):
        card = ctk.CTkFrame(
            self.stats_bar,
            height=86,
            corner_radius=14,
            fg_color=CARD_BG,
            border_width=1,
            border_color=CARD_BORDER
        )
        card.grid(row=0, column=col, sticky="nsew", padx=4)
        card.grid_propagate(False)

        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.place(x=12, y=10)

        ctk.CTkLabel(
            top_frame, text=icon, text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            top_frame, text=title, text_color=TEXT_MUTED,
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(side="left")

        val_label = ctk.CTkLabel(
            card, text=value_text, text_color=accent_color,
            font=ctk.CTkFont(size=18 if len(value_text) > 4 else 22, weight="bold")
        )
        val_label.place(relx=0.90, rely=0.38, anchor="e")

        sub_label = None
        if subtext:
            sub_label = ctk.CTkLabel(
                card, text=subtext, text_color=TEXT_DIM,
                font=ctk.CTkFont(size=10)
            )
            sub_label.place(x=12, y=62)

        graph = tk.Canvas(
            card, width=130, height=24,
            bg=CARD_BG, highlightthickness=0
        )
        graph.place(relx=0.92, rely=0.74, anchor="e")

        return {
            "card": card,
            "value": val_label,
            "subtext": sub_label,
            "graph": graph,
            "accent": accent_color
        }

    # -----------------------------------------------------
    # COMMAND PROCESSING & VOICE
    # -----------------------------------------------------

    def send_text(self):
        command = self.chat_entry.get().strip()
        if not command:
            return

        self.chat_entry.delete(0, "end")
        self.add_chat("You", command, assistant=False)
        self.set_ai_state("THINKING", "J IS THINKING...")

        threading.Thread(
            target=self.process_command,
            args=(command,),
            daemon=True
        ).start()

    def process_command(self, command):
        try:
            response = j_engine.process_command(command)
            self.after(
                0,
                lambda r=response: self.handle_response(r)
            )
        except Exception as e:
            print("Command error:", e)
            self.after(
                0,
                lambda: self.handle_response(
                    "Something went wrong while processing your command."
                )
            )

    def handle_response(self, response):
        self.add_chat("J", response, assistant=True)
        self.set_ai_state("SPEAKING", "J IS SPEAKING...")

        threading.Thread(
            target=self.speech_thread,
            args=(response,),
            daemon=True
        ).start()

    def speech_thread(self, text):
        try:
            j_engine.speak(text)
        finally:
            self.after(0, lambda: self.set_ai_state("READY", "J IS READY"))

    def start_voice(self):
        if self.listening:
            return

        self.listening = True
        self.mic_button.configure(
            fg_color="#3d000a",
            border_color=RED_PRIMARY,
            text_color=RED_PRIMARY
        )

        self.set_ai_state("LISTENING", "J IS LISTENING...")
        self.hint_label.configure(text="Speak now...")

        threading.Thread(
            target=self.voice_thread,
            daemon=True
        ).start()

    def voice_thread(self):
        try:
            command = j_engine.listen(
                timeout=5,
                phrase_time_limit=8
            )

            if command:
                self.after(
                    0,
                    lambda c=command: self.voice_received(c)
                )
            else:
                self.after(
                    0,
                    lambda: self.set_ai_state("READY", "J IS READY")
                )

        except Exception as e:
            print("Voice error:", e)
            self.after(
                0,
                lambda: self.set_ai_state("READY", "MICROPHONE ERROR")
            )
        finally:
            self.after(0, self.voice_finished)

    def voice_received(self, command):
        self.add_chat("You", command, assistant=False)
        self.set_ai_state("THINKING", "J IS THINKING...")

        threading.Thread(
            target=self.process_command,
            args=(command,),
            daemon=True
        ).start()

    def voice_finished(self):
        self.listening = False
        self.mic_button.configure(
            fg_color=RED_CONTAINER,
            border_color=RED_PRIMARY,
            text_color=RED_PRIMARY
        )
        self.hint_label.configure(text="Press microphone or type a command")

    def test_speaker(self):
        self.set_ai_state("SPEAKING", "TESTING SPEAKER...")

        threading.Thread(
            target=self.speaker_thread,
            daemon=True
        ).start()

    def speaker_thread(self):
        try:
            j_engine.speak("Speaker test successful. J is ready.")
        finally:
            self.after(
                0,
                lambda: self.set_ai_state("READY", "J IS READY")
            )

    def set_ai_state(self, state, text):
        self.ai_state = state
        self.status_label.configure(
            text=text,
            text_color=RED_PRIMARY
        )

    # -----------------------------------------------------
    # SYSTEM MONITOR UPDATE
    # -----------------------------------------------------

    def update_system_stats(self):
        if not self.running:
            return

        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            ram_pct = mem.percent
            ram_used_gb = mem.used / (1024 ** 3)
            ram_total_gb = mem.total / (1024 ** 3)

            disk = psutil.disk_usage("C:\\")
            disk_pct = disk.percent
            disk_used_gb = disk.used / (1024 ** 3)
            disk_total_gb = disk.total / (1024 ** 3)

            battery = psutil.sensors_battery()
            bat_pct = battery.percent if battery else 100
            bat_charging = "⚡ Charging" if (battery and battery.power_plugged) else "🔋 Battery"

            self.update_card(self.cpu_card, cpu, f"{cpu:.0f}%")
            self.update_card(
                self.ram_card, ram_pct, f"{ram_pct:.0f}%",
                f"{ram_used_gb:.1f} GB / {ram_total_gb:.1f} GB"
            )
            self.update_card(
                self.storage_card, disk_pct, f"{disk_pct:.0f}%",
                f"{disk_used_gb:.0f} GB / {disk_total_gb:.0f} GB"
            )
            self.update_card(self.battery_card, bat_pct, f"{bat_pct:.0f}%", bat_charging)
            self.update_card(self.network_card, 18, "Connected", "Ping: 18 ms")

        except Exception as e:
            print("Stats error:", e)

        self.after(2000, self.update_system_stats)

    def update_card(self, card, val_num, val_text, sub_text=None):
        card["value"].configure(text=val_text)

        if sub_text and card.get("subtext"):
            card["subtext"].configure(text=sub_text)

        graph = card["graph"]
        graph.delete("all")

        points = []
        for x in range(0, 131, 10):
            y = 12 + random.randint(-6, 6)
            points.append((x, y))

        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            graph.create_line(
                x1, y1, x2, y2,
                fill=card["accent"],
                width=1.5
            )

    # -----------------------------------------------------
    # NAVIGATION
    # -----------------------------------------------------

    def navigation_clicked(self, page):
        for button in self.nav_buttons:
            button.configure(
                fg_color="transparent",
                border_width=0,
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(size=14, weight="normal")
            )

        index = [
            "Home", "Chat", "System",
            "Commands", "Memory",
            "Settings", "About J"
        ].index(page)

        self.nav_buttons[index].configure(
            fg_color=RED_CONTAINER,
            border_width=1,
            border_color=RED_DARK,
            text_color=RED_PRIMARY,
            font=ctk.CTkFont(size=14, weight="bold")
        )

        if page == "Chat":
            self.chat_entry.focus()
        elif page == "Home":
            self.set_ai_state("READY", "J IS READY")

    def focus_input(self):
        self.chat_entry.focus()

    def on_closing(self):
        self.running = False

        try:
            j_engine.engine.stop()
        except Exception:
            pass

        self.destroy()


if __name__ == "__main__":
    app = JApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
