# To make python 2 and python 3 compatible code
# from __future__ import division
# from __future__ import absolute_import

# Imports
# import text2speech
# from VideoStream import VideoStream
# import VideoStream
import os.path
import base64
import time
import json
import requests
import numpy
import sys
if sys.version_info[0] < 3:  # e.g python version <3
    import cv2
else:
    import cv2
    #from cv2 import cv2


maxRetry = 5
lastTagSpoken = ''
count = 0


class CameraCapture(object):

    def __IsInt(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def __init__(
            self,
            videoPath,
            predictThreshold,
            imageProcessingEndpoint,
            sendToHubCallback,
            processingDelay
    ):
        self.videoPath = videoPath

        self.predictThreshold = predictThreshold
        self.imageProcessingEndpoint = imageProcessingEndpoint
        self.imageProcessingParams = ""
        self.sendToHubCallback = sendToHubCallback
        self.processingDelay = processingDelay


        if self.__IsInt(videoPath):
            # case of a usb camera (usually mounted at /dev/video* where * is an int)
            self.isWebcam = True

        self.vs = None


    def __sendFrameForProcessing(self, frame):
        global count
        # global count, lastTagSpoken
        count = count + 1
        print("sending frame to model: " + str(count))

        headers = {'Content-Type': 'application/octet-stream'}

        retry = 0
        while retry < maxRetry:
            try:
                response = requests.post(self.imageProcessingEndpoint, headers=headers,
                                         params=self.imageProcessingParams, data=frame)
                break
            except:
                retry = retry + 1
                print(
                    'Image Classification REST Endpoint - Retry attempt # ' + str(retry))
                time.sleep(retry)

        if retry >= maxRetry:
            print("retry inference")
            return []

        predictions = response.json()['predictions']
        sortResponse = sorted(
            predictions, key=lambda k: k['probability'], reverse=True)[0]
        probability = sortResponse['probability']

        print("label: {}, probability {}".format(
            sortResponse['tagName'], sortResponse['probability']))

        if probability > self.predictThreshold:

            return json.dumps(predictions)
        else:
            return []

    def __enter__(self):
        # self.vs = VideoStream(self.videoPath).start()
        self.vs = cv2.VideoCapture(self.videoPath)
        # needed to load at least one frame into the VideoStream class
        time.sleep(1.0)

        return self

    def start(self):

        frameCounter = 0
        while True:
            frameCounter += 1
            # frame = self.vs.read()
            (grabbed, frame) = self.vs.read()

            if(not grabbed == True):
                print('End of stream reached')
                return

            if self.imageProcessingEndpoint != "":

                encodedFrame = cv2.imencode(".jpg", frame)[1].tostring()
                try:
                    response = self.__sendFrameForProcessing(encodedFrame)

                    # forwarding outcome of external processing to the EdgeHub
                    if response != "[]" and self.sendToHubCallback is not None:
                        try:
                            self.sendToHubCallback(response)
                        except:
                            print(
                                'Issue sending telemetry')
                except:
                    print('connectivity issue')

            # slow things down a bit - 1 frame a second is fine for demo purposes and less battery drain and lower Raspberry Pi CPU Temperature
            time.sleep(self.processingDelay)

    def __exit__(self, exception_type, exception_value, traceback):
        pass
