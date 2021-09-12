# -*- coding: utf-8 -*-
"""Hackathon - Hindi character classification

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12n87ojReg2qBhtS5CS5eqze3Wc2rynsR
"""

from google_drive_downloader.google_drive_downloader import GoogleDriveDownloader as gdd
gdd.download_file_from_google_drive(file_id='1s4bVYjVwfHBPIcy6W5XAm4sjrGMjFlG_',
                                    dest_path='/content/train.zip',
                                    unzip=True)
gdd.download_file_from_google_drive(file_id='1_0Rzyx9A41WqeAja2seZEmEw2_OGKPg3',
                                    dest_path='/content/test.zip',
                                    unzip=True)

from keras.preprocessing import image
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
import tensorflow as tf
import numpy as np
from tensorflow.keras import datasets, layers, models
import cv2 
import matplotlib.pyplot as plt

batch_size=100

train_data_ex = ImageDataGenerator(
        rescale=1./255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)

train_generator = train_data_ex.flow_from_directory(
        '/content/training',  
        target_size=(64,64),
        batch_size=batch_size,
        class_mode='binary')

val_data_ex = ImageDataGenerator(rescale=1./255,validation_split = 0.2)

val_generator = val_data_ex.flow_from_directory(
    '/content/training',
    target_size=(64,64),
    batch_size=batch_size,
    subset = 'validation' ,
    class_mode='binary')

train_generator.class_indices

model = models.Sequential()
model.add(layers.Conv2D(128, kernel_size=4, strides=1, activation='relu', input_shape=(64,64,3),padding="same"))
model.add(layers.AveragePooling2D((2,2)))
model.add(layers.Conv2D(64, kernel_size=4, strides=1, activation='relu', padding="same"))
model.add(layers.MaxPooling2D((2,2)))
model.add(layers.Conv2D(32, kernel_size=4, strides=1, activation='relu', padding="same"))
model.add(layers.MaxPooling2D((2,2)))
model.add(layers.Conv2D(16, kernel_size=4, strides=1, activation='relu', padding="same"))
model.add(layers.AveragePooling2D((2,2)))
model.add(layers.Dropout(0.2))
model.add(layers.Flatten())
model.add(layers.Dense(1024))
model.add(layers.Dense(1,activation="sigmoid"))
model.summary()
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='binary_crossentropy',
              metrics=['accuracy'])
'''
checkpoint_filepath = './checkpoint'
model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_filepath,
    save_weights_only=True,
    monitor='accuracy',
    mode='max',
    save_best_only=True,
    save_freq=1000)
'''

#model.fit(train_generator, steps_per_epoch=10, epochs=200, batch_size=100)#,callbacks=[model_checkpoint_callback]) 
history=model.fit(
    train_generator,
    steps_per_epoch=50,
    epochs=50,
    batch_size=100,
    validation_data =val_generator,
    validation_steps=10
)

from keras.models import model_from_json
json_model = model.to_json()
with open('/content/drive/MyDrive/Tensored.json', 'w') as json_file:
    json_file.write(json_model)
model.save_weights('/content/drive/MyDrive/Tensored_weights.h5')

val_loss=history.history['val_loss']
train_loss=history.history['loss']

plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)
fig, axs = plt.subplots(1, 1,figsize=(12,10))
axs.set_title("Train Loss Vs Validation Loss ")
axs.plot(val_loss, label='Validation Loss',color='red')
axs.plot(train_loss, label = 'Training loss ',color='blue')
axs.set_xlabel('Epoch')
axs.set_ylabel('Loss')
axs.legend(loc='upper right')

l2 = [1,0,1,0,1,0,1,0,1,0,0,0,1,0,1,0,0,0,0,1,1,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,0,0,0,0,0,0,1,1,1,0,0,0,1,0,1,1,1,0,1,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0]

import os
res={}
for i in range(1,99):
  img = image.load_img('/content/test/'+str(i)+'.jpg')
  plt.imshow(img)
  plt.show()
  

  X = image.img_to_array(img)
  X=np.expand_dims(X,axis=0)
  images =  np.vstack([X])
  value = model.predict(images)
  if value==0:
    print(i," - 0 - ",l2[i-1])
  else:
    print(i," - 1 - ",l2[i-1])
  
  test_set = str(i) + '.jpg'
  res[test_set] = int(value[0][0])

img_path='/content/test/5.jpg' #dog
# Define a new Model, Input= image 
# Output= intermediate representations for all layers in the  
# previous model after the first.
successive_outputs = [layer.output for layer in model.layers[1:]]
#visualization_model = Model(img_input, successive_outputs)
visualization_model = tf.keras.models.Model(inputs = model.input, outputs = successive_outputs)
#Load the input image
img = load_img(img_path, target_size=(64,64))
# Convert ht image to Array of dimension (150,150,3)
x   = img_to_array(img)                           
x   = x.reshape((1,) + x.shape)
# Rescale by 1/255
x /= 255.0
# Let's run input image through our vislauization network
# to obtain all intermediate representations for the image.
successive_feature_maps = visualization_model.predict(x)
# Retrieve are the names of the layers, so can have them as part of our plot
layer_names = [layer.name for layer in model.layers]
for layer_name, feature_map in zip(layer_names, successive_feature_maps):
  print(feature_map.shape)
  if len(feature_map.shape) == 4:
    
    # Plot Feature maps for the conv / maxpool layers, not the fully-connected layers
   
    n_features = feature_map.shape[-1]  # number of features in the feature map
    size       = feature_map.shape[ 1]  # feature map shape (1, size, size, n_features)
    
    # We will tile our images in this matrix
    display_grid = np.zeros((size, size * n_features))
    
    # Postprocess the feature to be visually palatable
    for i in range(n_features):
      x  = feature_map[0, :, :, i]
      x -= x.mean()
      x /= x.std ()
      x *=  64
      x += 128
      x  = np.clip(x, 0, 255).astype('uint8')
      # Tile each filter into a horizontal grid
      display_grid[:, i * size : (i + 1) * size] = x
# Display the grid
    scale = 20. / n_features
    plt.figure( figsize=(scale * n_features, scale) )
    plt.title ( layer_name )
    plt.grid  ( False )
    plt.imshow( display_grid, aspect='auto', cmap='viridis' )

l1 = []
for key in res.keys():
    l1.append(int(res[key]))
print(l1)

l2 = [1,0,1,0,1,0,1,0,1,0,0,0,1,0,1,0,0,0,0,1,1,1,1,1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,0,0,0,0,0,0,1,1,1,0,0,0,1,0,1,1,1,0,1,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,1,1,1,1,1,0,0,0,0]
len(l2),len(l1)

acc = 0
for i in range(98):
    acc += (l1[i] == l2[i])
print(acc/len(l1))

import json
def write_json(filename, result):
    with open(filename, 'w') as outfile:
        json.dump(result, outfile)
def read_json(filename):
    with open(filename, 'r') as outfile:
        data =  json.load(outfile)
    return data

write_json('/content/drive/MyDrive/result.json', res)

