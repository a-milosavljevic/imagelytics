import os
import tensorflow as tf


img_root = '../WebApp/WebApp/img'   #'../WebApp/img'
sql_server = '(local)\\SQLEXPRESS'  #'IMAGELYTICS-SERVER'
sleep_seconds = 3
batch_size = 32
model_root = os.path.join(os.getcwd(), 'models')
