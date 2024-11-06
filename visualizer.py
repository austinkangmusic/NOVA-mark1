import librosa
import numpy as np
import pygame
import math
import random

# Helper function to clamp values
def clamp(min_value, max_value, value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value

class AudioOrb:
    def __init__(self, radius, angle, freq, max_height=100, min_decibel=-60, max_decibel=0):
        self.radius = radius
        self.angle = angle
        self.freq = freq
        self.height = 0.01  # Start height at a very small default value, not zero
        self.min_decibel, self.max_decibel = min_decibel, max_decibel
        self.max_height = max_height
        self.__decibel_height_ratio = (self.max_height) / (self.max_decibel - self.min_decibel)
        self.speed = random.uniform(0.05, 0.1) * random.choice([-1, 1])
        self.initial_radius = radius
        self.outward_force = 0

    def update(self, dt, center_x, center_y, decibel):
        desired_height = (decibel - self.min_decibel) * self.__decibel_height_ratio
        if desired_height < 0.01:
            desired_height = 0.01

        speed = (desired_height - self.height) / 0.1
        self.height += speed * dt
        self.height = clamp(0, self.max_height, self.height)

        self.outward_force = clamp(0, 1, self.height / self.max_height) * 50

        self.angle += self.speed * dt
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
        elif self.angle < 0:
            self.angle += 2 * math.pi

        self.x = center_x + (self.initial_radius + self.outward_force) * math.cos(self.angle)
        self.y = center_y + (self.initial_radius + self.outward_force) * math.sin(self.angle)

    def render(self, screen):
        current_radius = 1 + self.height * 0.005
        if self.height <= self.max_height / 2:
            color_intensity = clamp(0, 255, int((self.height / (self.max_height / 2)) * 255))
            color = (color_intensity, 0, 0)
        else:
            color_intensity = clamp(0, 255, int(((self.height - (self.max_height / 2)) / (self.max_height / 2)) * 255))
            color = (255, color_intensity, color_intensity)

        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(current_radius))

# Load audio data using librosa
filename = "audios/vocoder_output.wav"
time_series, sample_rate = librosa.load(filename)
stft = np.abs(librosa.stft(time_series, hop_length=512, n_fft=2048 * 4))
spectrogram = librosa.amplitude_to_db(stft, ref=np.max)
frequencies = librosa.core.fft_frequencies(n_fft=2048 * 4)
times = librosa.core.frames_to_time(np.arange(spectrogram.shape[1]), sr=sample_rate, hop_length=512, n_fft=2048 * 4)
time_index_ratio = len(times) / times[len(times) - 1]
frequencies_index_ratio = len(frequencies) / frequencies[len(frequencies) - 1]

def get_decibel(target_time, freq):
    time_index = clamp(0, spectrogram.shape[1] - 1, int(target_time * time_index_ratio))
    freq_index = clamp(0, spectrogram.shape[0] - 1, int(freq * frequencies_index_ratio))
    return spectrogram[freq_index][time_index]

def draw_background(screen):
    screen.fill((0, 0, 0))

def run_visualizer():
    pygame.init()
    infoObject = pygame.display.Info()
    screen_w = int(infoObject.current_w / 2)
    screen_h = int(infoObject.current_h / 2)

    screen = pygame.display.set_mode([screen_w, screen_h], pygame.RESIZABLE)
    pygame.display.set_caption('ULTRON')
    ultron_icon = pygame.image.load('ultron.png')
    pygame.display.set_icon(ultron_icon)

    orbs = []
    num_orbs = 777
    center_x = screen_w // 2
    center_y = screen_h // 2

    for _ in range(num_orbs):
        radius = random.uniform(50, 100)
        angle = random.uniform(0, 2 * math.pi)
        freq = random.choice(frequencies)
        orbs.append(AudioOrb(radius, angle, freq))

    pygame.mixer.music.load(filename)

    # Initialize the tick variable here
    getTicksLastFrame = pygame.time.get_ticks()

    running = True
    while running:
        screen_w, screen_h = screen.get_size()
        center_x = screen_w // 2
        center_y = screen_h // 2

        t = pygame.time.get_ticks()
        deltaTime = (t - getTicksLastFrame) / 1000.0
        getTicksLastFrame = t

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        draw_background(screen)

        for orb in orbs:
            orb.update(deltaTime, center_x, center_y, get_decibel(pygame.mixer.music.get_pos() / 1000.0, orb.freq))
            orb.render(screen)

        pygame.display.flip()

    pygame.quit()



def play_visualizer():
    pygame.mixer.music.set_volume(1)  # Mute the audio
    pygame.mixer.music.play()  # Loop the audio indefinitely

def stop_visualizer():
    pygame.mixer.music.stop()  # Stop the audio

