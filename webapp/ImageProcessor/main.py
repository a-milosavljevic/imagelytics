import os.path
import time
import numpy as np
import cv2 as cv
import json
from db import *


tf.compat.v1.disable_eager_execution()


def square_resize_image(img_input):
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


########################################################################################################################
# INITIALIZATION
########################################################################################################################

db_models = db_get_models()
models = []

for item in db_models:
    model_path = os.path.join(model_root, item.Filename)
    model_json_path = model_path + '.json'
    model_path = model_path + '.h5'

    if os.path.exists(model_path) and os.path.exists(model_json_path):
        with open(model_json_path) as json_file:
            model_dict = json.load(json_file)
            image_size = model_dict['image_size']
            stretch = model_dict['stretch']
            last_conv_layer = model_dict['last_conv_layer']
            classes = model_dict['classes']

        keras_model = tf.keras.models.load_model(model_path)
        keras_model.summary()

        target_layer = keras_model.get_layer(last_conv_layer)

        models.append({'model_id': item.Id,
                       'model_name': item.Filename,
                       'image_size': image_size,
                       'stretch': stretch,
                       'classes': classes,
                       'keras_model': keras_model,
                       'target_layer': target_layer})
    else:
        db_set_model_unavailable(item.Id)


########################################################################################################################
# INFINITE LOOP
########################################################################################################################

while True:
    should_sleep = True
    for model_dict in models:
        model_id = model_dict['model_id']
        images = db_get_project_images(model_id)
        if len(images) > 0:
            should_sleep = False

            model_name = model_dict['model_name']
            image_size = model_dict['image_size']
            stretch = model_dict['stretch']
            classes = model_dict['classes']
            keras_model = model_dict['keras_model']
            target_layer = model_dict['target_layer']

            # Load and resize images for processing
            batch_x = np.zeros((len(images), image_size, image_size, 3), dtype=np.uint8)
            bad_images = []
            original_sizes = []
            for i in range(len(images)):
                item = images[i]
                path = '{}/{}/{}.jpg'.format(img_root, item[1], item[2])
                img_src = cv.imread(path)
                if img_src is not None:
                    original_sizes.append((img_src.shape[1], img_src.shape[0]))
                    img_square = square_resize_image(img_src)
                    #path_square = '{}/{}/{}_SQ.jpg'.format(img_root, item[1], item[2])
                    #cv.imwrite(path_square, img_square)
                    img_square = cv.cvtColor(img_square, cv.COLOR_BGR2RGB)
                    batch_x[i] = img_square
                else:
                    bad_images.append(i)
                    original_sizes.append((0, 0))

            # Run prediction
            batch_y = keras_model.predict_on_batch(batch_x)
            batch_y_class = np.argmax(batch_y, axis=1)

            # Sort by probability
            batch_idx = np.argsort(batch_y, axis=-1)
            batch_idx = np.flip(batch_idx, axis=-1)

            # Fill image info for DB update
            image_classes = []
            for i in range(len(images)):
                item = images[i]
                if i in bad_images:
                    image_classes.append((item[0],))
                else:
                    idx = batch_idx[i, :5]
                    cls = [classes[k] for k in idx]
                    prob = batch_y[i, idx]
                    image_classes.append((item[0],
                                          (cls[0], float(prob[0])),
                                          (cls[1], float(prob[1])),
                                          (cls[2], float(prob[2])),
                                          (cls[3], float(prob[3])),
                                          (cls[4], float(prob[4]))))

            # Visualize heatmaps
            indices = np.expand_dims(np.arange(len(batch_y_class)), axis=1)
            indices = np.concatenate((indices, np.expand_dims(batch_y_class, axis=1)), axis=1)
            output = tf.gather_nd(keras_model.output, indices)
            grads = tf.keras.backend.gradients(output, target_layer.output)[0]
            pooled_grads = tf.keras.backend.mean(grads, axis=(1, 2))
            iterate = tf.keras.backend.function([keras_model.input], [pooled_grads, target_layer.output])
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
            for i in range(len(images)):
                if i not in bad_images:
                    item = images[i]
                    img = batch_x[i].copy()
                    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
                    heatmap = heatmaps[i]

                    heatmap = cv.resize(heatmap, (img.shape[1], img.shape[0]))
                    heatmap = np.uint8(255 * heatmap)
                    heatmap = cv.applyColorMap(heatmap, cv.COLORMAP_JET)

                    superimposed_img = heatmap * 0.4 + img
                    superimposed_img = crop_original(superimposed_img, w=original_sizes[i][0], h=original_sizes[i][1])
                    path_heatmap = '{}/{}/{}_HM.jpg'.format(img_root, item[1], item[2])
                    cv.imwrite(path_heatmap, superimposed_img)

            # Update database
            db_update_project_images(image_classes)
            print('Finished with model {}'.format(model_name))

    if should_sleep:
        # print("Sleeping {} seconds".format(sleep_seconds))
        time.sleep(sleep_seconds)
