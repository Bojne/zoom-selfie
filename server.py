import os
import glob
from io import BytesIO
from PIL import Image
from flask import Flask, render_template, request
from zoomie_stuff import main, template_files

print('Found {} template files'.format(len(template_files)))

app = Flask(__name__)

def file_handle_to_pil_image(f):
    image_bytes = BytesIO(f.read())
    return Image.open(image_bytes).convert('RGB')

DIRNAME = 'static/results'

@app.route('/', methods=['GET', 'POST'])
def index():
    for fn in glob.glob(os.path.join(DIRNAME, '*')):
        os.remove(fn)
    assert len(glob.glob(os.path.join(DIRNAME, '*'))) == 0, 'Found {} file'.format(len(glob.glob(os.path.join(DIRNAME, '*'))))
    if request.method == 'POST':
        f = request.files['content']
        image = file_handle_to_pil_image(f).convert('RGB')
        results = [main(image, Image.open(fn)) for fn in template_files]
        filenames = []
        for index, fn in enumerate(template_files):
            print('processing', index)
            result = main(image, Image.open(fn)).convert('RGB')
            filename = os.path.join(DIRNAME, '{}.jpg'.format(index))
            if os.path.exists(filename): os.remove(filename)
            result.save(filename)
            filenames.append(filename)
        return render_template('index.html', filenames=filenames)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)