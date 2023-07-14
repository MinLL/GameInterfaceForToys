from interfaces.interface import Interface
from common.util import *
import dxcam
import os
import cv2 as cv
import settings

class PixelReaderInterface(Interface):
    def __init__(self, toy_type):
        Interface.__init__(self, "Pixel Reader", toy_type)
        self.frame_grabber = dxcam.create(output_color="BGR")
        frame = self.frame_grabber.grab()
        self.height = frame.shape[0]
        self.width = frame.shape[1]
        self.health_down_template = self.load_template("health_down.png")
        self.you_died_template = self.load_template("you_died.png")

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

    def match_template(self, frame, template, confidence=0.85):
        result = cv.matchTemplate(frame, template, cv.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
        print(minVal, maxVal, minLoc, maxLoc)
        return (maxVal > confidence)

    def setup(self):
        info("Initializing pixel reader (h{} / w{})".format(self.height, self.width))
        self.start_cam()
        return Interface.setup(self)
        
    def execute(self):
        self.capture_frame()
        if (self.match_template(self.frame, self.you_died_template, 0.85)):
            print("Match")
        

