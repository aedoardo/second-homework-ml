# -*- coding: utf-8 -*-
"""Homework ML Code.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1N86yW9_KpL52GMHeIEcIm6NVGe3kWDsz
"""

import numpy as np
import tensorflow as tf
import keras
from keras.preprocessing.image import ImageDataGenerator
from google.colab import drive
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, Flatten,\
                         Conv2D, MaxPooling2D, MaxPool2D
from keras.layers.normalization import BatchNormalization
from keras import regularizers
from keras import optimizers
from keras.applications.resnet50 import preprocess_input
!pip install split-folders
import splitfolders

device_name = tf.test.gpu_device_name()
if device_name != '/device:GPU:0':
  raise SystemError('GPU device not found')
print('Found GPU at: {}'.format(device_name))

drive.mount('/content/drive')

# load datasets
ZIP_PATH = "/content/drive/MyDrive/training.zip"
  
!cp {ZIP_PATH} .
!unzip -u -q training.zip
!rm training.zip

print("Dataset loaded! \n")
splitfolders.ratio("training", output="dataset", seed=1337, ratio=(.7, .3), group_prefix=None) # default values

# define costants

epochs = 25
batch_size = 32
image_shape = (224, 224)

# function to build an ImageDataGenerator


def build_image_data_generator(zoom_range=0.1, rotation_range=10, w_shift_range=0.1,
                         h_shift_range=0.1, horizontal_flip=True,
                         vertical_flip=False, validation_split=0.3, pr_f=None):
  return ImageDataGenerator(
      rescale= 1. / 255,
      zoom_range=zoom_range,
      rotation_range=rotation_range,
      width_shift_range=w_shift_range,
      height_shift_range=h_shift_range,
      horizontal_flip=horizontal_flip,
      vertical_flip=vertical_flip,
      #validation_split=validation_split,
      #preprocessing_function=pr_f
  )


# function to build a Generator from an ImageDataGenerator

def build_generator(image_data_generator, set_type='training', target_size=image_shape, color_mode="rgb", class_mode="categorical", shuffle=True,directory='dataset/train/'):
  return image_data_generator.flow_from_directory(
      directory=directory,
      #subset=set_type,
      target_size=target_size,
      color_mode=color_mode,
      batch_size=batch_size,
      class_mode=class_mode,
      shuffle=shuffle,
  )

train_datagen = build_image_data_generator(pr_f=preprocess_input) # datagen for training
train_generator = build_generator(train_datagen) # generator for training

test_datagen = build_image_data_generator(0, 0, 0, 0, False, False) # test datagen
test_generator = build_generator(test_datagen, set_type='validation', shuffle=False, directory='dataset/val/') # generator for validation

# numbers

num_samples = train_generator.n
num_classes = train_generator.num_classes
input_shape = train_generator.image_shape

class_names = [k for k, v in train_generator.class_indices.items()]

print("Image input {}".format(str(input_shape)))
print("Classes: {}".format(class_names))

print("Loaded {} training samples from {} classes".format(str(num_samples), str(num_classes)))
print("Loaded {} validation samples from {} classes".format(str(test_generator.n), str(num_classes)))

import matplotlib.pyplot as plt

n = 3
x,y = train_generator.next()
# x,y size is train_generator.batch_size

for i in range(0,n):
    image = x[i]
    label = y[i].argmax()  # categorical from one-hot-encoding
    print(class_names[label])
    plt.imshow(image)
    plt.show()

# try with AlexNET

def AlexNet(input_shape, num_classes, regl2=0.0001, lr=0.0001):

  model = Sequential()

  model.add(Conv2D(filters=96, input_shape=input_shape, kernel_size=(11, 11),
            strides=(2, 4), padding='valid'))
  model.add(Activation("relu"))
  model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))
  model.add(BatchNormalization())

  model.add(Conv2D(filters=256, kernel_size=(11, 11), strides=(1, 1), padding='valid'))
  model.add(Activation("relu"))
  model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))
  model.add(BatchNormalization())

  model.add(Conv2D(filters=256, kernel_size=(3, 3), strides=(1, 1), padding='valid'))
  model.add(Activation("relu"))
  model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2), padding='valid'))
  model.add(BatchNormalization())

  model.add(Flatten())
  flatten_shape = (input_shape[0] * input_shape[1] * input_shape[2], )

  model.add(Dense(4096, kernel_regularizer=regularizers.l2(regl2)))
  model.add(Activation('relu'))
  model.add(Dropout(0.4))
  model.add((BatchNormalization()))

  model.add(Dense(num_classes))
  model.add(Activation('softmax'))
  
  adam = optimizers.Adam(lr=lr)
  model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=["accuracy"])

  return model

def FirstCustomModel(input_shape, num_classes, lr=0.0001):
  model = Sequential()

  model.add(Conv2D(16, 3, strides=(2, 2), input_shape=input_shape, padding='valid', activation='relu'))
  model.add(MaxPooling2D())

  model.add(Conv2D(32, 3, strides=(2, 2), padding='valid', activation='relu'))
  model.add(MaxPooling2D())

  model.add(Conv2D(64, 3, strides=(2, 2), padding='valid', activation='relu'))
  model.add(MaxPooling2D())

  model.add(Dropout(0.4))
  model.add(Flatten())
  model.add(Dense(128, activation='relu'))
  model.add(Dense(num_classes, activation='softmax'))

  adam = optimizers.Adam(lr=lr)
  model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=["accuracy"])
  return model

def VGG16(input_shape, num_classes, lr=0.001):
  model = Sequential()

  model.add(Conv2D(filters=64, kernel_size=(3, 3), padding="same", input_shape=input_shape, activation="relu"))
  model.add(Conv2D(filters=64, kernel_size=(3, 3), padding="same", activation="relu"))
  model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))

  model.add(Conv2D(filters=128, kernel_size=(3, 3), padding="same", activation="relu"))
  model.add(Conv2D(filters=128, kernel_size=(3, 3), padding="same", activation="relu"))
  model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))

  model.add(Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"))
  model.add(Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"))
  model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))

  model.add(Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
  model.add(Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
  model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))

  model.add(Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
  model.add(Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"))
  model.add(MaxPool2D(pool_size=(2, 2), strides=(2, 2)))

  model.add(Flatten())
  model.add(Dense(4096, activation="relu"))
  model.add(Dense(4096, activation="relu"))
  model.add(Dense(num_classes, activation="softmax"))
  SGD = optimizers.SGD(lr=lr)
  model.compile(loss='categorical_crossentropy', optimizer=SGD, metrics=["accuracy"])

  return model


def SecondCustomModel(input_shape, num_classes, lr=0.0001):
  model = Sequential()

  model.add(Conv2D(16, 3, strides=(2, 2), input_shape=input_shape, padding='valid', activation='relu'))
  model.add(MaxPooling2D())
  model.add(Dropout(0.2))

  model.add(Conv2D(32, 3, strides=(2, 2), padding='valid', activation='relu'))
  model.add(MaxPooling2D())
  model.add(Dropout(0.2))

  model.add(Conv2D(64, 3, strides=(2, 2), padding='valid', activation='relu'))
  model.add(MaxPooling2D())
  model.add(Dropout(0.2))

  model.add(Flatten())
  model.add(Dense(4096, activation='relu'))
  model.add(Dense(128, activation='relu'))
  model.add(Dense(num_classes, activation='softmax'))

  adam = optimizers.Adam(lr=lr)
  model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=["accuracy"])
  return model


model = SecondCustomModel(input_shape, num_classes)

model.summary()

# train the model

steps_per_epoch = train_generator.n // train_generator.batch_size
val_steps = test_generator.n // test_generator.batch_size + 1
try:
  history = model.fit(train_generator, epochs=epochs, verbose=1, steps_per_epoch=steps_per_epoch, validation_data=test_generator, validation_steps=val_steps)
except KeyboardInterrupt:
  pass

# model evaluation

test_generator = build_generator(test_datagen, set_type="validation", shuffle=False, directory='dataset/val/')
val_steps=test_generator.n//test_generator.batch_size+1
loss, acc = model.evaluate(test_generator,verbose=1,steps=val_steps)
print('Test loss: {}'.format(loss))
print('Test accuracy: {}'.format(acc))

# metrics scores

import sklearn.metrics 
from sklearn.metrics import classification_report, confusion_matrix

val_steps=test_generator.n//test_generator.batch_size+1
test_generator = build_generator(test_datagen, set_type="validation", shuffle=False, directory='dataset/val/')

preds = model.predict(test_generator,verbose=1,steps=val_steps)

Ypred = np.argmax(preds, axis=1)
Ytest = test_generator.classes  # shuffle=False in test_generator

print(classification_report(Ytest, Ypred, labels=None, target_names=class_names, digits=3))

import sklearn.metrics 
from sklearn.metrics import classification_report, confusion_matrix

val_steps=test_generator.n//test_generator.batch_size+1
test_generator = build_generator(test_datagen, set_type="validation", shuffle=False, directory='dataset/val/')

preds = model.predict_generator(test_generator,verbose=1,steps=val_steps)

Ypred = np.argmax(preds, axis=1)
Ytest = test_generator.classes  # shuffle=False in test_generator

cm = confusion_matrix(Ytest, Ypred)

conf = [] # data structure for confusions: list of (i,j,cm[i][j])
for i in range(0,cm.shape[0]):
  for j in range(0,cm.shape[1]):
    if (i!=j and cm[i][j]>0):
      conf.append([i,j,cm[i][j]])

col=2
conf = np.array(conf)
conf = conf[np.argsort(-conf[:,col])]  # decreasing order by 3-rd column (i.e., cm[i][j])

print('%-16s     %-16s  \t%s \t%s ' %('True','Predicted','errors','err %'))
print('------------------------------------------------------------------')
for k in conf:
  print('%-16s ->  %-16s  \t%d \t%.2f %% ' %(class_names[k[0]],class_names[k[1]],k[2],k[2]*100.0/test_generator.n))

import matplotlib.pyplot as plt

# summarize history for accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()