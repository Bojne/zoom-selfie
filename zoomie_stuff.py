import numpy as np
from PIL import Image
from coremltools.models import MLModel
import os
import glob

CWD = os.path.dirname(__file__)
template_files = glob.glob(os.path.join(CWD, 'template_images', '*.png'))
template_files += glob.glob(os.path.join(CWD, 'template_images', '*.jpg'))
template_files += glob.glob(os.path.join(CWD, 'template_images', '*.jpeg'))

face_model = MLModel('face.mlmodel')

def get_face_bboxes(img):
    img = img.convert('RGB')
    w, h = img.size
    resized_img = img.resize((320, 240))
    result = face_model.predict({'input_image': resized_img, 'iouThreshold': 0.1, 'confidenceThreshold': 0.5}, useCPUOnly=True)
    coordinates = result['coordinates'][:]
    # print("Face output", coordinates)
    # cx, cy, w, h 
    coordinates[:, 0] = coordinates[:, 0]*w
    coordinates[:, 1] = coordinates[:, 1]*h
    coordinates[:, 2] = coordinates[:, 2]*w
    coordinates[:, 3] = coordinates[:, 3]*h
    
    bboxes = []
    for cor in coordinates:
        bboxes.append([cor[0]-cor[2]/2, cor[1]-cor[3]/2, cor[0]+cor[2]/2, cor[1]+cor[3]/2])
    return bboxes

to_int = lambda box: [int(i) for i in box]
box_to_size = lambda box: (box[2]-box[0], box[3]-box[1])

def image_to_face_scraps_or_boxes(image, return_boxes=False):
    boxes = get_face_bboxes(image.convert('RGB'))
    boxes = [to_int(box) for box in boxes]
    if return_boxes:
        return boxes
    scraps = [image.crop(box) for box in boxes]
    return scraps

def put_faces_on_template(face_scraps, template_image):
    boxes = image_to_face_scraps_or_boxes(template_image, return_boxes=True)
    for scrap, box in zip(face_scraps, boxes):
        size = box_to_size(box)
        scrap = scrap.resize(size)
        template_image.paste(scrap, box)
    return template_image

def main(zoom_image, template_image):
    scraps = image_to_face_scraps_or_boxes(zoom_image)
    return put_faces_on_template(scraps, template_image)

if __name__ == '__main__':
    image = Image.open('/Users/sisovina/Downloads/internal_zoom_call.png')
    template_image = Image.open('/Users/sisovina/Downloads/template/image 22.png')
    result = main(image, template_image).convert('RGB')
    result.save('/Users/sisovina/Downloads/zoom_result.jpg')
