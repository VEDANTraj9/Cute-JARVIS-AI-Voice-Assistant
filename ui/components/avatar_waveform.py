"""
Animated Female AI Avatar & Circular Audio Waveform Component.
Combines a stylized anime-tech female avatar (blinking, breathing, speaking lips)
with high-fps reactive concentric rings, orbital glowing particles,
and radial audio equalizer waves responding to AssistantState and RMS amplitude.
"""

import math
import random
import time
from typing import List, Tuple
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QPainter, QColor, QPen, QBrush, QRadialGradient,
    QLinearGradient, QPainterPath, QFont
)
from PySide6.QtWidgets import QWidget

from config.constants import AssistantState
from ui.styles.colors import Palette

class AvatarWaveformWidget(QWidget):
    """Futuristic glowing circular audio visualizer with animated female AI avatar."""
    
    avatar_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(320, 320)
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)

        # Internal state
        self.state = AssistantState.IDLE
        self.audio_amplitude = 0.0      # 0.0 to 1.0 (external RMS from speech/audio)
        self.smoothed_amplitude = 0.0
        
        # Animation parameters
        self.phase_angle = 0.0          # Orbital rotation angle (degrees)
        self.breathing_time = 0.0       # Subtle floating / breath
        self.mouth_openness = 0.0       # Lip sync movement
        
        # Blinking control
        self.is_blinking = False
        self.blink_progress = 0.0       # 0.0 (open) to 1.0 (shut)
        self.last_blink_time = time.time()
        self.next_blink_interval = random.uniform(3.0, 5.5)

        # Background particles
        self.particles: List[dict] = []
        self._init_particles(count=28)

        # High-FPS Animation Timer (60 FPS -> ~16ms)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(16)

    def _init_particles(self, count: int):
        """Generate subtle orbital floating neon particles."""
        self.particles = []
        for _ in range(count):
            self.particles.append({
                "angle": random.uniform(0, 360),
                "distance": random.uniform(105, 145),
                "speed": random.uniform(0.3, 1.2) * (1 if random.random() > 0.5 else -1),
                "size": random.uniform(2.0, 4.5),
                "color_type": random.choice(["cyan", "purple", "pink"]),
                "alpha": random.uniform(0.3, 0.9)
            })

    def set_state(self, state: AssistantState):
        """Update current operational state."""
        self.state = state
        self.update()

    def set_audio_amplitude(self, amp: float):
        """Update current audio volume level (0.0 to 1.0)."""
        self.audio_amplitude = max(0.0, min(1.0, amp))

    def _update_animation(self):
        """Frame update loop for 60fps animations."""
        now = time.time()

        # Update orbital rotation based on state
        speed_mult = 1.0
        if self.state == AssistantState.LISTENING:
            speed_mult = 2.2
        elif self.state == AssistantState.THINKING:
            speed_mult = 3.5
        elif self.state == AssistantState.SPEAKING:
            speed_mult = 1.8

        self.phase_angle = (self.phase_angle + 0.8 * speed_mult) % 360
        self.breathing_time += 0.05

        # Smooth audio amplitude transition (easing)
        target_amp = self.audio_amplitude
        if self.state == AssistantState.SPEAKING and target_amp < 0.05:
            # Subtle synthetic speech bounce when active
            target_amp = 0.25 + 0.3 * abs(math.sin(self.breathing_time * 6))

        self.smoothed_amplitude += (target_amp - self.smoothed_amplitude) * 0.25

        # Mouth movement during speech
        if self.state == AssistantState.SPEAKING:
            self.mouth_openness = 0.3 + 0.7 * self.smoothed_amplitude * abs(math.sin(self.breathing_time * 8))
        else:
            self.mouth_openness = max(0.0, self.mouth_openness - 0.1)

        # Eye blinking logic
        if not self.is_blinking:
            if now - self.last_blink_time > self.next_blink_interval:
                self.is_blinking = True
                self.blink_progress = 0.0
        else:
            self.blink_progress += 0.25
            if self.blink_progress >= 1.0:
                self.is_blinking = False
                self.blink_progress = 0.0
                self.last_blink_time = now
                self.next_blink_interval = random.uniform(2.8, 6.0)

        # Update orbital particles
        for p in self.particles:
            p["angle"] = (p["angle"] + p["speed"] * speed_mult) % 360

        self.update()

    def mousePressEvent(self, event):
        """Trigger clicked signal on avatar."""
        if event.button() == Qt.LeftButton:
            self.avatar_clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        """Render avatar, circular waveforms, glowing halos and orbital rings."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        width = self.width()
        height = self.height()
        center_x = width / 2.0
        center_y = height / 2.0
        base_radius = min(width, height) * 0.26

        # Determine theme accents according to assistant state
        accent_color, glow_color = self._get_state_colors()

        # 1. Background Ambient Glow
        self._draw_ambient_glow(painter, center_x, center_y, base_radius * 2.2, glow_color)

        # 2. Orbital Neon Particles
        self._draw_particles(painter, center_x, center_y)

        # 3. Concentric Rotating Rings & Status Arcs
        self._draw_orbital_rings(painter, center_x, center_y, base_radius, accent_color)

        # 4. Circular Audio Waveform / Equalizer Bars
        self._draw_circular_waveform(painter, center_x, center_y, base_radius, accent_color)

        # 5. Cute Anime AI Female Avatar Face
        self._draw_cute_avatar(painter, center_x, center_y, base_radius)

    def _get_state_colors(self) -> Tuple[QColor, QColor]:
        """Return accent and ambient glow colors matching operational state."""
        if self.state == AssistantState.LISTENING:
            return QColor(Palette.CYAN), QColor(0, 240, 255, 60)
        elif self.state == AssistantState.THINKING:
            return QColor(Palette.PURPLE), QColor(138, 77, 255, 65)
        elif self.state == AssistantState.SPEAKING:
            return QColor(Palette.PINK), QColor(255, 92, 168, 75)
        elif self.state == AssistantState.ERROR:
            return QColor(Palette.STATE_ERROR), QColor(255, 69, 101, 75)
        # IDLE
        return QColor(Palette.CYAN_DIM), QColor(0, 240, 255, 25)

    def _draw_ambient_glow(self, painter: QPainter, cx: float, cy: float, radius: float, glow_color: QColor):
        """Draw deep radial gradient glow beneath the avatar."""
        gradient = QRadialGradient(QPointF(cx, cy), radius)
        gradient.setColorAt(0.0, glow_color)
        gradient.setColorAt(0.65, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 15))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_particles(self, painter: QPainter, cx: float, cy: float):
        """Draw floating glowing orbital particles."""
        painter.setPen(Qt.NoPen)
        for p in self.particles:
            rad = math.radians(p["angle"])
            dist = p["distance"] + 6.0 * math.sin(self.breathing_time + p["angle"])
            px = cx + dist * math.cos(rad)
            py = cy + dist * math.sin(rad)

            if p["color_type"] == "cyan":
                color = QColor(0, 240, 255, int(p["alpha"] * 255))
            elif p["color_type"] == "purple":
                color = QColor(179, 136, 255, int(p["alpha"] * 255))
            else:
                color = QColor(255, 92, 168, int(p["alpha"] * 255))

            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(px, py), p["size"], p["size"])

    def _draw_orbital_rings(self, painter: QPainter, cx: float, cy: float, base_radius: float, accent: QColor):
        """Render concentric cyber rings with dashed tech segments."""
        # Outer delicate ring
        r1 = base_radius + 38 + (self.smoothed_amplitude * 12)
        pen1 = QPen(QColor(accent.red(), accent.green(), accent.blue(), 70), 1.5, Qt.DashLine)
        pen1.setDashPattern([6, 10])
        painter.setPen(pen1)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), r1, r1)

        # Rotating segment arc
        r2 = base_radius + 24
        pen2 = QPen(QColor(Palette.PURPLE_LIGHT), 2.5)
        painter.setPen(pen2)
        span_angle = 60 * 16
        painter.drawArc(
            QRectF(cx - r2, cy - r2, r2 * 2, r2 * 2),
            int(self.phase_angle * 16),
            span_angle
        )
        painter.drawArc(
            QRectF(cx - r2, cy - r2, r2 * 2, r2 * 2),
            int((self.phase_angle + 180) * 16),
            span_angle
        )

    def _draw_circular_waveform(self, painter: QPainter, cx: float, cy: float, base_radius: float, accent: QColor):
        """Draw radial dynamic equalizer bars around the avatar circumference."""
        num_bars = 48
        angle_step = 360.0 / num_bars
        inner_r = base_radius + 6.0

        for i in range(num_bars):
            ang_deg = i * angle_step + self.phase_angle * 0.5
            ang_rad = math.radians(ang_deg)

            # Calculate reactive wave height
            sine_wave = math.sin(ang_rad * 4 + self.breathing_time * 3)
            cos_wave = math.cos(ang_rad * 3 - self.breathing_time * 2)
            wave_mod = (sine_wave + cos_wave) * 0.5

            bar_len = 5.0 + (wave_mod * 4.0) + (self.smoothed_amplitude * 28.0)
            if self.state == AssistantState.LISTENING:
                bar_len += 8.0 * abs(math.sin(ang_rad * 6 + self.breathing_time * 5))
            elif self.state == AssistantState.THINKING:
                bar_len = 6.0 + 8.0 * abs(math.sin(ang_rad * 2 - self.phase_angle * 0.1))

            outer_r = inner_r + max(3.0, bar_len)

            x1 = cx + inner_r * math.cos(ang_rad)
            y1 = cy + inner_r * math.sin(ang_rad)
            x2 = cx + outer_r * math.cos(ang_rad)
            y2 = cy + outer_r * math.sin(ang_rad)

            # Gradient color from base to tip
            alpha = int(120 + 135 * min(1.0, bar_len / 35.0))
            pen_color = QColor(accent.red(), accent.green(), accent.blue(), alpha)
            painter.setPen(QPen(pen_color, 2.2, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _draw_cute_avatar(self, painter: QPainter, cx: float, cy: float, base_radius: float):
        """
        Draw cute anime female AI avatar:
        - Floating breathing movement
        - Cyber-headset with glowing cat-ear/antennae nodes
        - Anime eyes that blink periodically
        - Rosy glowing cheeks
        - Animated sweet smile
        """
        # Breathing vertical displacement
        breath_y = 3.0 * math.sin(self.breathing_time * 2.0)
        ay = cy + breath_y
        ax = cx

        face_radius = base_radius - 2.0

        # Avatar Base Halo Background
        bg_grad = QRadialGradient(QPointF(ax, ay), face_radius)
        bg_grad.setColorAt(0.0, QColor("#1A1D36"))
        bg_grad.setColorAt(0.85, QColor("#101328"))
        bg_grad.setColorAt(1.0, QColor("#0A0D1D"))
        painter.setPen(QPen(QColor(Palette.PURPLE), 2.5))
        painter.setBrush(QBrush(bg_grad))
        painter.drawEllipse(QPointF(ax, ay), face_radius, face_radius)

        # Cyber Headset / Holographic Cat-ear Antennae
        ear_w = 18.0
        ear_h = 24.0
        ear_pen = QPen(QColor(Palette.CYAN), 2.0)
        ear_brush = QBrush(QColor(138, 77, 255, 120))
        painter.setPen(ear_pen)
        painter.setBrush(ear_brush)

        # Left cyber ear
        left_ear = QPainterPath()
        left_ear.moveTo(ax - face_radius * 0.65, ay - face_radius * 0.6)
        left_ear.lineTo(ax - face_radius * 0.85, ay - face_radius * 1.1)
        left_ear.lineTo(ax - face_radius * 0.35, ay - face_radius * 0.85)
        left_ear.closeSubpath()
        painter.drawPath(left_ear)

        # Right cyber ear
        right_ear = QPainterPath()
        right_ear.moveTo(ax + face_radius * 0.65, ay - face_radius * 0.6)
        right_ear.lineTo(ax + face_radius * 0.85, ay - face_radius * 1.1)
        right_ear.lineTo(ax + face_radius * 0.35, ay - face_radius * 0.85)
        right_ear.closeSubpath()
        painter.drawPath(right_ear)

        # Headset Band
        band_pen = QPen(QColor(Palette.BORDER_PURPLE), 4.0, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(band_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(
            QRectF(ax - face_radius * 0.75, ay - face_radius * 0.95, face_radius * 1.5, face_radius * 1.4),
            20 * 16,
            140 * 16
        )

        # Cute Anime Hair Silhouette (Violet / Lavender bangs)
        hair_path = QPainterPath()
        hair_path.moveTo(ax - face_radius * 0.7, ay - face_radius * 0.2)
        # Bangs sweeping down
        hair_path.cubicTo(
            ax - face_radius * 0.4, ay - face_radius * 0.8,
            ax + face_radius * 0.4, ay - face_radius * 0.8,
            ax + face_radius * 0.7, ay - face_radius * 0.2
        )
        hair_path.lineTo(ax + face_radius * 0.65, ay - face_radius * 0.05)
        hair_path.cubicTo(
            ax + face_radius * 0.3, ay - face_radius * 0.35,
            ax - face_radius * 0.3, ay - face_radius * 0.35,
            ax - face_radius * 0.65, ay - face_radius * 0.05
        )
        hair_path.closeSubpath()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#7C4DFF")))
        painter.drawPath(hair_path)

        # Rosy Cheeks
        blush_color = QColor(255, 92, 168, 90)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(blush_color))
        painter.drawEllipse(QPointF(ax - face_radius * 0.42, ay + 10), 12, 6)
        painter.drawEllipse(QPointF(ax + face_radius * 0.42, ay + 10), 12, 6)

        # Cyber Cheek Markings (Cyan micro-dots)
        painter.setBrush(QBrush(QColor(Palette.CYAN)))
        painter.drawEllipse(QPointF(ax - face_radius * 0.55, ay + 10), 2.5, 2.5)
        painter.drawEllipse(QPointF(ax - face_radius * 0.48, ay + 13), 2.0, 2.0)
        painter.drawEllipse(QPointF(ax + face_radius * 0.55, ay + 10), 2.5, 2.5)
        painter.drawEllipse(QPointF(ax + face_radius * 0.48, ay + 13), 2.0, 2.0)

        # Expressive Anime Eyes (or Blinking Line)
        eye_y = ay - 4.0
        eye_dist = face_radius * 0.32
        eye_w = 14.0
        eye_h = 16.0

        if self.is_blinking:
            # Cute curved shut eye lines (^_^)
            pen_shut = QPen(QColor(Palette.CYAN_LIGHT), 2.8, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen_shut)
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(QRectF(ax - eye_dist - eye_w / 2, eye_y - 4, eye_w, 10), 30 * 16, 120 * 16)
            painter.drawArc(QRectF(ax + eye_dist - eye_w / 2, eye_y - 4, eye_w, 10), 30 * 16, 120 * 16)
        else:
            # Open glowing anime eyes
            for eye_center_x in [ax - eye_dist, ax + eye_dist]:
                # White sclera
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.drawEllipse(QPointF(eye_center_x, eye_y), eye_w * 0.6, eye_h * 0.65)

                # Cyan Iris
                iris_grad = QRadialGradient(QPointF(eye_center_x, eye_y), eye_w * 0.5)
                iris_grad.setColorAt(0.0, QColor(Palette.CYAN_LIGHT))
                iris_grad.setColorAt(0.7, QColor(Palette.CYAN))
                iris_grad.setColorAt(1.0, QColor("#006070"))
                painter.setBrush(QBrush(iris_grad))
                painter.drawEllipse(QPointF(eye_center_x, eye_y), eye_w * 0.45, eye_h * 0.55)

                # Dark Pupil
                painter.setBrush(QBrush(QColor("#081224")))
                painter.drawEllipse(QPointF(eye_center_x, eye_y), eye_w * 0.22, eye_h * 0.28)

                # Sparkle Eye Catchlights (Anime glint)
                painter.setBrush(QBrush(QColor("#FFFFFF")))
                painter.drawEllipse(QPointF(eye_center_x - 2.5, eye_y - 3.0), 3.0, 3.0)
                painter.drawEllipse(QPointF(eye_center_x + 2.0, eye_y + 2.5), 1.6, 1.6)

                # Eyelashes
                lash_pen = QPen(QColor("#B388FF"), 2.2, Qt.SolidLine, Qt.RoundCap)
                painter.setPen(lash_pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawArc(QRectF(eye_center_x - eye_w * 0.6, eye_y - eye_h * 0.75, eye_w * 1.2, 8), 20 * 16, 140 * 16)

        # Mouth (Sweet Smile or Talking Openness)
        mouth_y = ay + 21.0
        mouth_pen = QPen(QColor(Palette.PINK), 2.2, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(mouth_pen)

        if self.mouth_openness > 0.15:
            # Talking mouth
            open_h = 4.0 + (self.mouth_openness * 9.0)
            painter.setBrush(QBrush(QColor(Palette.PINK)))
            painter.drawEllipse(QPointF(ax, mouth_y), 7.0, open_h)
            # Small white tooth sparkle
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor("#FFFFFF")))
            painter.drawRect(QRectF(ax - 3, mouth_y - open_h * 0.6, 6, 2))
        else:
            # Cute subtle smile arc
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(QRectF(ax - 8, mouth_y - 4, 16, 8), 210 * 16, 120 * 16)

        # Headset Glow Nodes (Left & Right Earcups)
        node_glow = QColor(Palette.CYAN if self.state != AssistantState.SPEAKING else Palette.PINK)
        painter.setPen(QPen(node_glow, 2.0))
        painter.setBrush(QBrush(QColor(Palette.BG_BASE)))
        painter.drawEllipse(QPointF(ax - face_radius * 0.92, ay), 7, 12)
        painter.drawEllipse(QPointF(ax + face_radius * 0.92, ay), 7, 12)
