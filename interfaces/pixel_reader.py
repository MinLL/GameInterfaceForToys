from interfaces.interface import Interface
from common.util import *
import dxcam
import os
import cv2 as cv
import settings
from PIL import Image
import time
import math

class PixelReaderInterface(Interface):
    def __init__(self, toy_type):
        Interface.__init__(self, "Pixel Reader", toy_type)
        self.frame_grabber = dxcam.create(device_idx=0, output_idx=int(settings.OUTPUT_IDX), output_color="BGR")
        frame = self.frame_grabber.grab()
        self.height = frame.shape[0]
        self.width = frame.shape[1]
        self.health_down_template = self.load_template("health_down.png")
        self.you_died_template = self.load_template("you_died.png")
        self.last_screen_cap = 0
        
    def load_template(self, file_name, make_binary = False):
        path = os.path.join(os.path.abspath("."), "data/images/eldenring", file_name)
        template = cv.imread(path)
        if(make_binary == True):
            template = self.white_range(template)
        height = int(template.shape[0] * self.height / settings.RESOLUTION_H)
        width =  int(template.shape[1] * self.width / settings.RESOLUTION_W)
        return cv.resize(template, (width, height))

    def white_range(self, mat):
        min = 150
        return cv.inRange(mat, (min, min, min), (255, 255, 255))
  
    def black_range(self, mat):
        max = 165
        return cv.inRange(mat, (0,0,0), (max, max, max))

    def start_cam(self):
        self.frame_grabber.start(target_fps=10)

    def capture_frame(self):
        self.frame = self.frame_grabber.get_latest_frame()
        self.image = Image.fromarray(self.frame)

    def match_template(self, frame, template, confidence=0.85):
        result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
        print(minVal, maxVal, minLoc, maxLoc)
        return (maxVal > confidence)

    def setup(self):
        info("Initializing pixel reader (h{} / w{})".format(self.height, self.width))
        print("Available Devices:")
        info(dxcam.device_info())
        self.start_cam()
        self.vibrate_ramp_start = 0
        self.vibrate_ramp_last = 0
        return Interface.setup(self)

    def event_is_type(self, event, event_type):
        if event.params is None:
            return False
        if not 'capture_type' in event.params:
            return False
        return event.params['capture_type'] == event_type

    def _match_pixel_all(self, event):
        match = True
        for (x, y) in event.params['coordinates']:
            (b, g, r) = self.image.getpixel((int(x), int(y)))
            target = event.params['target_value']
            if (b, g, r) != (target['b'], target['g'], target['r']):
                match = False
        return match
    
    def _match_pixel_range_any(self, event):
        params = event.params
        target_b = int(params['target_value']['b'])
        target_g = int(params['target_value']['g'])
        target_r = int(params['target_value']['r'])
        
        for x in range(int(params['coordinates']['range_x']['start']), int(params['coordinates']['range_x']['end'])):
            for y in range(int(params['coordinates']['range_y']['start']), int(params['coordinates']['range_y']['end'])):
                color = self.image.getpixel((x,y))
                b,g,r = color
                if (b, g, r) == (target_b, target_g, target_r):
                    return (x, y)
        return (-1, -1)

    
    def execute(self):
        self.capture_frame()
        ret = []
        current_time = get_time_ms()
        if not (current_time - self.last_screen_cap > settings.SCREEN_CAP_COOLDOWN):
            return
        for event in self.event_loader.events:
            if hasattr(event, 'last_executed'):
                # Event on cooldown
                if not (current_time - event.last_executed > (int(event.params['cooldown']) * 1000)):
                    return
            if self.event_is_type(event, 'pixel_gauge'):
                coords = self._match_pixel_range_any(event)
                if coords != (-1, -1):
                    success("Matched Event: " + event.name)
                    ret += [event.function(event, coords)]
                    event.last_executed = current_time
            elif self.event_is_type(event, 'pixel_match_all') and self._match_pixel_all(event):
                ret += [event.function(event)]
                event.last_executed = current_time
                success("Matched Event: " + event.name)
        self.last_screen_cap = current_time
        return ret

    def generic_pixel_gauge(self, event, coords):
        start_x = event.params['coordinates']['range_x']['start']
        end_x = event.params['coordinates']['range_x']['end']
        strength = int(((end_x - float(coords[0])) / start_x) * 100)
        success("generic_pixel_gauge: Left most coordinate: {} (start={}, end={})".format(coords[0], start_x, end_x))
        if 'toy_type' in event.params and event.params['toy_type'] == 'estim':
            foo = self.toys.shock
        else:
            foo = self.toys.vibrate
        pattern = ''
        if 'pattern' in event.params:
            pattern = event.params['pattern']
        foo(event.params['duration'], strength, pattern, event=event)


    def generic_ramping_vibration(self, event):
        pattern = ''
        if 'pattern' in event.params:
            pattern = event.params['pattern']
        strength = 0
        current_time = time.time()
        if current_time - self.vibrate_ramp_last > 30: # Reset ramp if more than 30 seconds have passed
            self.vibrate_ramp_start = current_time
        # Ramp up to full speed over the course of the specified duration
        ramp_target = int(event.params['ramp_duration'])
        delta = current_time - self.vibrate_ramp_start
        strength = math.ceil((delta / ramp_target) * 100)
        self.vibrate_ramp_last = current_time
        if strength < 5:
            strength = 5
        if strength > 100:
            strength = 100
        self.toys.vibrate(event.params['duration'], strength, pattern, event=event)

