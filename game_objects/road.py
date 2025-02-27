import math
import random
from config import *

class Road:
    def __init__(self):
        self.offset = 0
        self.curves = []
        self.noise_points = []
        self.init_road_curves()
        self.init_noise_points()

    def init_noise_points(self):
        self.noise_points = []
        distance_between_points = 200  # Space them out
        
        for i in range(NUM_NOISE_POINTS):
            pos = i * distance_between_points
            offset = random.uniform(-CURVE_AMPLITUDE * 0.7, CURVE_AMPLITUDE * 0.7)
            self.noise_points.append((pos, offset))

    def init_road_curves(self):
        self.curves = []
        self.init_noise_points()
        
        pos = 0
        for i in range(ROAD_SEGMENTS):
            curve_direction = random.uniform(-1.0, 1.0)
            
            if random.random() < 0.2:  # 20% chance of straight section
                amplitude = 0
            else:
                amplitude = random.uniform(CURVE_AMPLITUDE * 0.2, CURVE_AMPLITUDE * 0.8) * curve_direction
            
            wavelength = random.uniform(CURVE_WAVELENGTH * 0.8, CURVE_WAVELENGTH * 1.2)
            phase_offset = random.uniform(0, 2 * math.pi)
            segment_length = wavelength * random.uniform(0.7, 1.3)
            
            self.curves.append({
                "amplitude": amplitude,
                "wavelength": wavelength,
                "phase_offset": phase_offset,
                "segment_length": segment_length,
                "start_position": pos,
                "curve_type": random.choice(["sine", "cosine", "linear"])
            })
            
            pos += segment_length

    def get_current_curve(self, pos):
        total_length = sum(curve["segment_length"] for curve in self.curves)
        normalized_pos = pos % total_length
        
        for curve in self.curves:
            if normalized_pos >= curve["start_position"] and \
               normalized_pos < curve["start_position"] + curve["segment_length"]:
                return curve, normalized_pos - curve["start_position"]
        
        return self.curves[0], 0

    def interpolate_noise(self, pos):
        prev_point = None
        next_point = None
        
        for i, (noise_pos, offset) in enumerate(self.noise_points):
            if noise_pos > pos:
                next_point = (noise_pos, offset)
                if i > 0:
                    prev_point = self.noise_points[i-1]
                else:
                    prev_point = self.noise_points[-1]
                    prev_point = (prev_point[0] - sum(curve["segment_length"] for curve in self.curves), prev_point[1])
                break
        
        if next_point is None:
            next_point = self.noise_points[0]
            next_point = (next_point[0] + sum(curve["segment_length"] for curve in self.curves), next_point[1])
            prev_point = self.noise_points[-1]
        
        if next_point[0] == prev_point[0]:
            return next_point[1]
        
        t = (pos - prev_point[0]) / (next_point[0] - prev_point[0])
        return prev_point[1] + t * (next_point[1] - prev_point[1])

    def get_road_center(self, y_pos):
        road_pos = y_pos + self.offset
        curve, segment_pos = self.get_current_curve(road_pos)
        
        if curve["amplitude"] == 0:
            curve_offset = 0
        else:
            if curve["curve_type"] == "sine":
                curve_offset = curve["amplitude"] * math.sin(
                    (segment_pos / curve["wavelength"] * 2 * math.pi) + curve["phase_offset"]
                )
            elif curve["curve_type"] == "cosine":
                curve_offset = curve["amplitude"] * math.cos(
                    (segment_pos / curve["wavelength"] * 2 * math.pi) + curve["phase_offset"]
                )
            else:  # Linear
                x = ((segment_pos / curve["wavelength"]) % 1) * 4
                if x < 1:
                    wave = x
                elif x < 3:
                    wave = 2 - x
                else:
                    wave = x - 4
                curve_offset = curve["amplitude"] * wave
        
        noise = self.interpolate_noise(road_pos) * 0.3
        return BASE_ROAD_CENTER + curve_offset + noise

    def get_road_edges(self, y_pos):
        center = self.get_road_center(y_pos)
        return center - ROAD_WIDTH / 2, center + ROAD_WIDTH / 2

    def get_lane_positions(self, y_pos):
        left_edge, _ = self.get_road_edges(y_pos)
        return [
            left_edge + LANE_WIDTH / 2,      # Left lane center
            left_edge + LANE_WIDTH * 1.5,    # Middle lane center
            left_edge + LANE_WIDTH * 2.5,    # Right lane center
        ]

    def scroll(self):
        self.offset -= SCROLL_SPEED 