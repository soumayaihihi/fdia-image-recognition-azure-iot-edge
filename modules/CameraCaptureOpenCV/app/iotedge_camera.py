# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import os
import random
import sys
import time
import asyncio
from azure.iot.device import IoTHubModuleClient, Message
# import ptvsd

# ptvsd.enable_attach(address=('0.0.0.0', 5678))
# ptvsd.wait_for_attach()


# from iothub_client import IoTHubModuleClient, IoTHubClientError, IoTHubTransportProvider
# from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError

import CameraCapture
from CameraCapture import CameraCapture


# global counters
SEND_CALLBACKS = 0
module_client = None


def send_to_Hub_callback(strMessage):
    if strMessage == []:
        return

    message = Message(strMessage)
    message.content_encoding = "utf-8"
    message.custom_properties["appid"] = "scanner";


    # hubManager.send_event_to_output("output1", message, 0)
    print('sent from send_to_Hub_callback')

# Callback received when the message that we're forwarding is processed.


def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    SEND_CALLBACKS += 1


class HubManager(object):

    async def __init__(
            self
    ):
        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()
        await self.client.connect()

    def send_event_to_output(self, outputQueueName, event, send_context):
        pass
        
        # self.client.send_message(message);
        # self.client.send_event_async(
        #     outputQueueName, event, send_confirmation_callback, send_context)


def initialise(
        videoPath,
        predictThreshold,
        imageProcessingEndpoint=""
):
    '''
    Capture a camera feed, send it to processing and forward outputs to EdgeHub

    :param str connectionString: Edge Hub connection string. Mandatory.
    :param int videoPath: camera device path such as /dev/video0 or a test video file such as /TestAssets/myvideo.avi. Mandatory.
    :param str imageProcessingEndpoint: service endpoint to send the frames to for processing. Example: "http://face-detect-service:8080". Leave empty when no external processing is needed (Default). Optional.

    '''
    try:
        print("\nPython %s\n" % sys.version)
        print("Camera Capture Azure IoT Edge Module. Press Ctrl-C to exit.")

        # global hubManager
        # hubManager = HubManager()

        with CameraCapture(videoPath, predictThreshold, imageProcessingEndpoint, send_to_Hub_callback) as cameraCapture:
            cameraCapture.start()
    except KeyboardInterrupt:
        print("Camera capture module stopped")

async def main():
    global module_client
    try:
        VIDEO_PATH = os.getenv('Video', '0')
        PREDICT_THRESHOLD = os.getenv('Threshold', .75)
        IMAGE_PROCESSING_ENDPOINT = os.getenv('AiEndpoint', 'http://localhost:80/image')

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        module_client.connect()

    except ValueError as error:
        print(error)
        sys.exit(1)

    initialise(VIDEO_PATH,
         PREDICT_THRESHOLD, IMAGE_PROCESSING_ENDPOINT)

if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    asyncio.run(main())
