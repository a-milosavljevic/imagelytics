import os
from PySide6.QtCore import *
from PySide6.QtWidgets import QApplication
import threading
import time
import json
import numpy as np
import cv2 as cv
import tensorflow as tf
import base64
import webbrowser


tf.compat.v1.disable_eager_execution()


def square_resize_image(img_input, image_size, stretch):
    if stretch:
        img_out = cv.resize(img_input, (image_size, image_size), interpolation=cv.INTER_AREA)
    else:
        img_out = img_input
        w, h = img_out.shape[1], img_out.shape[0]
        top, bottom, left, right = 0, 0, 0, 0
        if w >= h:
            top = (w - h) // 2
            bottom = (w - h) - top
        else:
            left = (h - w) // 2
            right = (h - w) - left
        #mean_color = tuple(np.average(img_input, axis=(0, 1)))
        img_out = cv.copyMakeBorder(img_out, top, bottom, left, right, cv.BORDER_CONSTANT, value=(0, 0, 0)) #mean_color
        img_out = cv.resize(img_out, (image_size, image_size), interpolation=cv.INTER_AREA)
    return img_out


def crop_original(img_input, w, h):
    d = img_input.shape[0]
    if w > h:
        top = round(d * 0.5 * (w - h) / w)
        bottom = d - top
        return img_input[top:bottom, :, :]
    elif w < h:
        left = round(d * 0.5 * (h - w) / h)
        right = d - left
        return img_input[:, left:right, :]
    else:
        return img_input


def resize_original_aspect(img_input, w, h):
    d = img_input.shape[0]
    if w > h:
        dh = round(d * h / w)
        return cv.resize(img_input, (d, dh), interpolation=cv.INTER_LINEAR)
    elif w < h:
        dw = round(d * w / h)
        return cv.resize(img_input, (dw, d), interpolation=cv.INTER_LINEAR)
    else:
        return img_input


class MyApp(QObject):

    def __init__(self, app):
        QObject.__init__(self)
        self.app = app
        self._models_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'models')
        self._processing = False
        self._thread = None
        self._lock = threading.Lock()
        self._cancel = False
        self._model = ''
        self._images = []
        self._output_file = ''
        self._project_name = 'Project name'
        self._project_desc = 'Project description'
        self._processed_images = []
        self._processing_error = ''

    # PROPERTY processing (bool)

    @Signal
    def processing_changed(self):
        pass

    def get_processing(self):
        return self._processing

    def set_processing(self, v):
        if self._processing != v:
            self._processing = v
            self.processing_changed.emit()

    processing = Property(bool, get_processing, set_processing, notify=processing_changed)

    # SLOTS

    @Slot(str)
    def log(self, s):
        print(s)

    @Slot(bool)
    def set_wait_cursor(self, on):
        if on:
            self.app.setOverrideCursor(Qt.WaitCursor)
        else:
            self.app.restoreOverrideCursor()

    @Slot(result=list)
    def get_models(self):
        models = []
        files = os.listdir(self._models_path)
        for file in files:
            if file[-3:].lower() == '.h5':
                name = file[:-3]
                txt_path = os.path.join(self._models_path, name + '.json')
                if os.path.exists(txt_path):
                    models.append(name)
        return models

    @Slot(str, list, str, str, str)
    def start_processing(self, model, images, output_file, project_name, project_desc):
        # print(model, images)
        if self._thread is not None and self._thread.is_alive():
            self.cancel_processing()
        self.set_wait_cursor(True)
        self._lock.acquire()
        self._cancel = False
        self._model = model
        self._output_file = output_file
        self._project_name = project_name
        self._project_desc = project_desc
        self._images = images
        self._processed_images = []
        self._processing_error = ''
        self._lock.release()
        self._thread = threading.Thread(target=self.thread_function)
        self._thread.start()
        self.set_wait_cursor(False)
        self.set_processing(True)

    @Slot()
    def cancel_processing(self):
        if self._thread is not None and self._thread.is_alive():
            self.set_wait_cursor(True)
            self._lock.acquire()
            self._cancel = True
            self._lock.release()
            while self._thread.is_alive():
                time.sleep(0.01)
            self._thread = None
            print("Thread is canceled")
            self.set_wait_cursor(False)
        self.set_processing(False)

    @Slot(str)
    def open_report(self, output_file):
        webbrowser.open_new_tab(output_file)

    @Slot(result=list)
    def get_processing_progress(self):
        if self._thread is None or not self._thread.is_alive():
            self.set_processing(False)
        self._lock.acquire()
        processed_images = self._processed_images
        self._processed_images = []
        self._lock.release()
        return processed_images

    @Slot(result=str)
    def get_processing_error(self):
        if self._thread is None or not self._thread.is_alive():
            self.set_processing(False)
        self._lock.acquire()
        processing_error = self._processing_error
        self._lock.release()
        return processing_error

    def thread_function(self):
        try:
            # Load model
            self._lock.acquire()
            model_name = self._model
            models_path = self._models_path
            output_file = self._output_file
            project_name = self._project_name
            project_desc = self._project_desc
            self._lock.release()
            print("Model:", model_name)
            if output_file[:8].lower() == 'file:///':
                output_file = output_file[8:]
            print("Output file:", output_file)

            model_path = os.path.join(models_path, model_name + '.h5')
            json_path = os.path.join(models_path, model_name + '.json')
            with open(json_path) as json_file:
                if json_path is None:
                    raise 'Error opening "' + json_path + '" for reading!'
                model_dict = json.load(json_file)
                image_size = model_dict['image_size']
                stretch = model_dict['stretch']
                last_conv_layer = model_dict['last_conv_layer']
                classes = model_dict['classes']
                classes_cnt = [0 for c in classes]

            model = tf.keras.models.load_model(model_path)
            target_layer = model.get_layer(last_conv_layer)

            with open(output_file, 'w') as html_file:
                if html_file is None:
                    raise RuntimeError('Error opening "' + output_file + '" for writing!')
                html_file.write('<!DOCTYPE html>\n')
                html_file.write('<html>\n')
                html_file.write('<head>\n')
                html_file.write('    <title>Imagelytics - {}</title>\n'.format(project_name))
                html_file.write('    <meta charset="utf-8" />\n')
                html_file.write('    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
                html_file.write('    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">\n')
                html_file.write('    <style>\n')
                html_file.write('        .progress-probability {\n')
                html_file.write('            margin-bottom: 10px;\n')
                html_file.write('        }\n')
                html_file.write('    </style>\n')
                html_file.write('</head>\n')
                html_file.write('<body>\n')
                html_file.write('<div class="jumbotron text-center">\n')
                html_file.write('    <h1>{}</h1>\n'.format(project_name))
                html_file.write('    <h2><b>Model:</b> {}</h2>\n'.format(model_name))
                if project_desc:
                    html_file.write('    <p>{}</p>\n'.format(project_desc))

                html_file.write('</div>\n')
                html_file.write('<div class="container">\n')

                loop = True
                while loop:
                    self._lock.acquire()
                    loop = not self._cancel
                    image = None
                    if loop and len(self._images) > 0:
                        image = self._images[0]
                        if len(self._images) > 1:
                            self._images = self._images[1:]
                        else:
                            self._images = None
                            loop = False
                    self._lock.release()

                    if image is not None:
                        imageUrl = image
                        print("Processing image:", imageUrl)

                        # Load and resize images for processing
                        batch_x = np.zeros((1, image_size, image_size, 3), dtype=np.uint8)

                        if image[:8].lower() == 'file:///':
                            image = image[8:]

                        image_name, image_ext = os.path.splitext(os.path.basename(image))

                        img_src = cv.imread(image)
                        if img_src is None:
                            print('Bad image:', image)
                            html_file.write('<div class="row">\n')
                            html_file.write('	<div class="col-sm-6" style="padding-bottom:15px">\n')
                            html_file.write('	</div>\n')
                            html_file.write('	<div class="col-sm-6">\n')
                            html_file.write('		<div class="alert alert-danger"><strong>{}</strong></div>\n'.format(image_name))
                            html_file.write('		<div class="well">\n')
                            html_file.write('		    <div>Error reading file:</div>\n')
                            html_file.write('		    <div>{}</div>\n'.format(image))
                            html_file.write('		</div>\n')
                            html_file.write('	</div>\n')
                            html_file.write('</div>\n')
                            html_file.write('<hr/>\n')
                        else:
                            img_square = square_resize_image(img_src, image_size, stretch)
                            img_square = cv.cvtColor(img_square, cv.COLOR_BGR2RGB)
                            batch_x[0] = img_square

                            # Run prediction
                            batch_y = model.predict_on_batch(batch_x)
                            batch_y_class = np.argmax(batch_y, axis=1)

                            # Sort by probability
                            batch_idx = np.argsort(batch_y, axis=-1)
                            batch_idx = np.flip(batch_idx, axis=-1)

                            # Fill image info

                            idx = batch_idx[0, :5]
                            cls = [classes[k] for k in idx]
                            prob = batch_y[0, idx]
                            top_class = idx[0]
                            top5_classes = []
                            for ci in range(len(cls)):
                                top5_classes.append((cls[ci], float(prob[ci])))
                            #print(top5_classes)

                            # Visualize heatmaps
                            indices = np.expand_dims(np.arange(len(batch_y_class)), axis=1)
                            indices = np.concatenate((indices, np.expand_dims(batch_y_class, axis=1)), axis=1)
                            output = tf.gather_nd(model.output, indices)
                            grads = tf.keras.backend.gradients(output, target_layer.output)[0]
                            pooled_grads = tf.keras.backend.mean(grads, axis=(1, 2))
                            iterate = tf.keras.backend.function([model.input], [pooled_grads, target_layer.output])
                            pooled_grads_value, target_layer_output_value = iterate([batch_x])

                            pooled_grads_value_ex = np.expand_dims(pooled_grads_value, axis=1)
                            pooled_grads_value_ex = np.expand_dims(pooled_grads_value_ex, axis=2)
                            pooled_grads_value_ex = np.repeat(pooled_grads_value_ex, target_layer_output_value.shape[1], axis=1)
                            pooled_grads_value_ex = np.repeat(pooled_grads_value_ex, target_layer_output_value.shape[2], axis=2)
                            target_layer_output_value = np.multiply(target_layer_output_value, pooled_grads_value_ex)

                            heatmaps = np.mean(target_layer_output_value, axis=-1)
                            heatmaps = np.maximum(heatmaps, 0)
                            heatmaps_max = np.max(heatmaps, axis=(1, 2))
                            heatmaps_max = np.expand_dims(heatmaps_max, axis=1)
                            heatmaps_max = np.expand_dims(heatmaps_max, axis=2)
                            heatmaps_max = np.repeat(heatmaps_max, heatmaps.shape[1], axis=1)
                            heatmaps_max = np.repeat(heatmaps_max, heatmaps.shape[2], axis=2)
                            heatmaps = np.divide(heatmaps, heatmaps_max)

                            # Save heatmaps
                            img_square = cv.cvtColor(img_square, cv.COLOR_RGB2BGR)
                            heatmap = heatmaps[0]
                            heatmap = cv.resize(heatmap, (image_size, image_size))
                            heatmap = np.uint8(255 * heatmap)
                            heatmap = cv.applyColorMap(heatmap, cv.COLORMAP_JET)

                            superimposed_img = heatmap * 0.4 + img_square
                            if stretch:
                                superimposed_img = resize_original_aspect(superimposed_img,
                                                                          w=img_src.shape[1], h=img_src.shape[0])
                            else:
                                superimposed_img = crop_original(superimposed_img,
                                                                 w=img_src.shape[1], h=img_src.shape[0])
                            img_buff = cv.imencode('.jpg', superimposed_img)[1]
                            img_base64 = base64.b64encode(img_buff).decode('ascii')

                            # Write HTML entry
                            html_file.write('<div class="row">\n')
                            html_file.write('	<div class="col-sm-6" style="padding-bottom:15px">\n')
                            html_file.write('		<img style="margin:auto" class="img-responsive img-rounded" alt="{}" src="data:image/jpeg;base64,{}" />\n'.format(image_name, img_base64))
                            html_file.write('	</div>\n')
                            html_file.write('	<div class="col-sm-6">\n')
                            html_file.write('		<div class="alert alert-info"><strong>{}</strong></div>\n'.format(image_name))
                            html_file.write('		<div class="well">\n')
                            for ci in range(len(top5_classes)):
                                cls = top5_classes[ci][0]
                                prob = '{:.2f}'.format(round(100 * top5_classes[ci][1], 2))
                                html_file.write('			<div>{} <span class="pull-right">{}%</span></div>\n'.format(cls, prob))
                                html_file.write('			<div class="progress progress-probability">\n')
                                html_file.write('				<div class="progress-bar" role="progressbar" aria-valuenow="{}" aria-valuemin="0" aria-valuemax="100" style="width:{}%"></div>\n'.format(prob, prob))
                                html_file.write('			</div>\n')
                            html_file.write('		</div>\n')
                            html_file.write('	</div>\n')
                            html_file.write('</div>\n')
                            html_file.write('<hr/>\n')

                            classes_cnt[top_class] += 1

                        self._lock.acquire()
                        self._processed_images.append(imageUrl)
                        self._lock.release()

                # Write project statistics
                html_file.write('<div class="row">\n')
                html_file.write('	<div class="alert alert-info text-center"><h2>Class statistics</h2></div>\n')
                html_file.write('	<div class="well">\n')
                total_images = sum(classes_cnt)
                sorted_classes = np.argsort(classes_cnt)[::-1]
                for ci in sorted_classes:
                    cls = classes[ci]
                    cnt = classes_cnt[ci]
                    if cnt > 0:
                        pct = '{:.2f}'.format(round(100 * cnt / total_images, 2))
                        html_file.write('		<div>{} <span class="pull-right">{} ({}%)</span></div>\n'.format(cls, cnt, pct))
                        html_file.write('		<div class="progress progress-probability">\n')
                        html_file.write('			<div class="progress-bar" role="progressbar" aria-valuenow="{}" aria-valuemin="0" aria-valuemax="100" style="width:{}%"></div>\n'.format(pct, pct))
                        html_file.write('		</div>\n')
                html_file.write('	</div>\n')
                html_file.write('</div>\n')

                # Close HTML file
                html_file.write('</div>\n')
                html_file.write('</body>\n')
                html_file.write('</html>\n')

        except RuntimeError as err:
            self._lock.acquire()
            self._processing_error = 'Unexpected runtime error:\n{}'.format(err)
            self._lock.release()

        except Exception as err:
            self._lock.acquire()
            self._processing_error = 'Unexpected {}:\n{}'.format(type(err).__name__, err)
            self._lock.release()
