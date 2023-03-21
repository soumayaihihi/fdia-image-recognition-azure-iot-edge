import argparse
import torch
import json
import os
import io

# Imports for the REST API
from flask import Flask, request, jsonify

# Imports for image procesing
from PIL import Image

# Imports for prediction
# from predict import initialize, predict_image, predict_url

app = Flask(__name__)
models = {}

# 4MB Max image size limit
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 

# Default route just shows simple text
@app.route('/')
def index():
    return 'CustomVision.ai model host harness'

# Like the CustomVision.ai Prediction service /image route handles either
#     - octet-stream image file 
#     - a multipart/form-data with files in the imageData parameter
@app.route('/image', methods=['POST'])
@app.route('/<project>/image', methods=['POST'])
@app.route('/<project>/image/nostore', methods=['POST'])
@app.route('/<project>/classify/iterations/<publishedName>/image', methods=['POST'])
@app.route('/<project>/classify/iterations/<publishedName>/image/nostore', methods=['POST'])
@app.route('/<project>/detect/iterations/<publishedName>/image', methods=['POST'])
@app.route('/<project>/detect/iterations/<publishedName>/image/nostore', methods=['POST'])
def predict(model='yolov5_custom', project=None, publishedName=None):
    if request.method != 'POST':
        return
    try:
        imageData = None
        if ('imageData' in request.files):
            imageData = request.files['imageData']
        elif ('imageData' in request.form):
            imageData = request.form['imageData']
        else:
            imageData = io.BytesIO(request.get_data())

        img = Image.open(imageData)
        if model in models:
            results = models[model](img, size=640)  # reduce size=320 for faster inference
            return results.pandas().xyxy[0].to_json(orient='records')
        
    except Exception as e:
        print('EXCEPTION:', str(e))
        return 'Error processing image', 500


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Flask API exposing YOLOv5 model')
    parser.add_argument('--port', default=80, type=int, help='port number')
    parser.add_argument('--model', nargs='+', default='yolov5_custom', help='model(s) to run, i.e. --model yolov5n yolov5s')
    opt = parser.parse_args()

    for m in opt.model:
        if m == 'yolov5_custom':
            models[m] = torch.hub.load('/yolov5', 'custom', 'best.pt', source='local', force_reload=True,)
            # torch.hub.load('.', 'custom', source='local', force_reload=True)
            # models[m].load_state_dict(torch.load('/Downloads/test-yolo-detect/yolov5/inputs/model/best.pt', map_location=torch.device('cpu'))['model'].state_dict())
        else:
            models[m] = torch.hub.load('/home/ubuntu/Downloads/test-yolo-detect/yolov5', m, force_reload=True, skip_validation=True)

        # models[m] = torch.hub.load('ultralytics/yolov5', m, force_reload=True, skip_validation=True)



    app.run(host='0.0.0.0', port=80, debug=True)  # debug=True causes Restarting with stat

