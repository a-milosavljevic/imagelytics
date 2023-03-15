"""
settings.py script contains different parameters that specify model and training procedure.
experiment_no is used for training different experiments and it should be incremented before training.
"""
import os
import tensorflow as tf
import shutil


########################################################################################################################
# TRAINING SETTINGS
########################################################################################################################

experiment_no = 1  # for tracking different experiments

batch_size = 16  # adjust according to available GPU memory

image_size = 512  # images are resized for training and evaluation to (image_size, image_size)
stretch = False  # if False keep aspect ratio, if True stretch images

# images are listed from the folder and divided into subsets according to the specified pattern
subset_distribution = ['T', 'S', 'V', 'T', 'S', 'T', 'T', 'V', 'S', 'T']  # train (T) 50%, val (V) 20%, test (S) 30%

# optimizer selection
#optimizer_name = 'SGD'
#optimizer_name = 'RMSprop'
optimizer_name = 'Adam'

if optimizer_name == 'SGD':
    init_lr = 1e-2
    optimizer = tf.keras.optimizers.SGD(learning_rate=init_lr, momentum=0.9)
elif optimizer_name == 'RMSprop':
    init_lr = 1e-3
    optimizer = tf.keras.optimizers.RMSprop(learning_rate=init_lr)
elif optimizer_name == 'Adam':
    init_lr = 1e-3
    optimizer = tf.keras.optimizers.Adam(learning_rate=init_lr)

data_augmentation = True  # use data augmentation for training
cosine_annealing = False  # use cosine annealing for training

monitor_loss = True  # monitor loss or accuracy for early stopping and learning rate reduce
if monitor_loss:
    val_monitor = ('val_loss', 'min')
else:
    val_monitor = ('val_sparse_categorical_accuracy', 'max')

# cosine annealing settings
lr_scale = 0.01
lr_period = 10
lr_decay = 0.7

# number of epochs, learning rate reduce patience, and early stopping settings
if cosine_annealing:
    epochs = 100 * lr_period
    epochs_warmup = lr_period
    reduce_lr_patience = lr_period
    early_stopping_patience = 3 * lr_period
else:
    epochs = 1000
    epochs_warmup = 10
    reduce_lr_patience = 10
    early_stopping_patience = 30

join_test_with_train = False  # if set test subset is joined to train subset while traning

heatmaps_for_test_images_only = True  # heatmaps are generated only for test images


########################################################################################################################
# MODEL SETTINGS
########################################################################################################################

dropout_rate = 0  # dropout rate after fully connected layers (0 means no dropout is used)
hidden_neurons = 0  # number of neurons in the hidden layer in classifier (0 means no hidden layer is used)

# CNN architecture selection (to add new architectures model.py must be extended)
#architecture = 'ResNet50'
#architecture = 'ResNet50V2'
#architecture = 'EfficientNetB0'
#architecture = 'EfficientNetB1'
architecture = 'EfficientNetB2'
#architecture = 'EfficientNetB3'
#architecture = 'EfficientNetB4'
#architecture = 'EfficientNetB5'
#architecture = 'EfficientNetB6'


########################################################################################################################
# FOLDER SETTINGS
########################################################################################################################

# root folder of the dataset
root_folder = os.path.join('D:\\', 'Datasets', 'Chiro10')

# data subfolder
data_folder = os.path.join(root_folder, 'data')
# folder with original images organized in subfolders by class
original_data_folder = os.path.join(data_folder, 'data_original')

# tmp subfolder where outputs are created
tmp_folder = os.path.join(root_folder, 'tmp')
if not os.path.exists(tmp_folder):
    os.makedirs(tmp_folder)

# train, validation, and test subfolders where processed images for training are saved
train_folder = os.path.join(data_folder, 'train_{}{}'.format(image_size, '_st' if stretch else ''))
if not os.path.exists(train_folder):
    os.makedirs(train_folder)

val_folder = os.path.join(data_folder, 'val_{}{}'.format(image_size, '_st' if stretch else ''))
if not os.path.exists(val_folder):
    os.makedirs(val_folder)

test_folder = os.path.join(data_folder, 'test_{}{}'.format(image_size, '_st' if stretch else ''))
if not os.path.exists(test_folder):
    os.makedirs(test_folder)

# name of the folder used for saving outputs in the current experiment
curr_folder_name = '{}_{}{}px_{}_do{}_hn{}_da{}_ca{}_lr{}_{}_{}_bs{}'.format('{:03d}'.format(experiment_no),
                                                                             'st' if stretch else '',
                                                                             image_size,
                                                                             architecture,
                                                                             dropout_rate,
                                                                             hidden_neurons,
                                                                             'Y' if data_augmentation else 'N',
                                                                             'Y' if cosine_annealing else 'N',
                                                                             init_lr,
                                                                             optimizer_name,
                                                                             'loss' if monitor_loss else 'acc',
                                                                             batch_size)

# current experiment folder path
curr_folder = os.path.join(tmp_folder, curr_folder_name)
if not os.path.exists(curr_folder):
    os.mkdir(curr_folder)

# copying current settings.py to current folder for tracking purposes
src_settings_file = os.path.join(os.getcwd(), 'settings.py')
dst_settings_file = os.path.join(curr_folder, 'settings.py')
if os.path.exists(dst_settings_file):
    os.remove(dst_settings_file)
shutil.copyfile(src_settings_file, dst_settings_file)

# experiments CSV file for tracking results of different experiments
experiments_file = os.path.join(tmp_folder, 'experiments.csv')
if not os.path.exists(experiments_file):
    with open(experiments_file, 'w') as f:
        f.write('ExperimentNo,ImageSize,Architecture,Dropout,HiddenNeurons,DataAugmentation,CosineAnnealing,'
                'InitLearningRate,Optimizer,MonitorLoss,BatchSize,TrainAcc,ValAcc,TestAcc\r\n')
