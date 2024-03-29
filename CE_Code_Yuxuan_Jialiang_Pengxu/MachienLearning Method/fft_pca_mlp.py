import os.path
import re
import sys
import numpy as np
from keras.models import Model, Sequential
from keras.layers import Flatten, Dense, Input, BatchNormalization
# from keras.engine.topology import get_source_inputs
from keras.utils.layer_utils import get_source_inputs
from keras.utils import layer_utils
from keras.utils.data_utils import get_file
from keras import backend as K
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.imagenet_utils import preprocess_input
# from keras.optimizers import RMSprop
from tensorflow.keras.optimizers import RMSprop
from keras.callbacks import ModelCheckpoint
# from keras.utils import to_categorical
from tensorflow.keras.utils import to_categorical
from keras.models import load_model
from sklearn.decomposition import PCA
from keras.layers import Dropout
import random
# from sklearn.externals import joblib
import joblib
from scipy.fftpack import fft,ifft
import matplotlib.pyplot as plt 
from ann_visualizer.visualize import ann_viz
from tensorflow.keras.utils import plot_model
from scipy.fftpack import fft,ifft

sbox=(
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16) 
hw = [bin(x).count("1") for x in range(256)]

model = Sequential()
model.add(Dense(256, input_dim=600, activation='relu'))
model.add(Dropout(0.8,seed=random.randint(0,99)))
#model.add(BatchNormalization())
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.5,seed=random.randint(0,99)))
#model.add(BatchNormalization())
model.add(Dense(9, activation='softmax'))
optimizer = RMSprop(lr=0.001)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

# tempTraces = np.load('./train/traces.npy')
# tempPText  = np.load('./train/textin.npy')
# tempKey    = np.load('./train/keylist.npy')
# tempSbox = [sbox[tempPText[i][0] ^ tempKey[i][0]] for i in range(len(tempPText))] 
# tempHW   = [hw[s] for s in tempSbox]

# atkTraces = np.load("./test/2019.04.03-14.47.53_traces.npy")
# atkPText  = np.load("./test/2019.04.03-14.47.53_textin.npy")
# atkKey    = np.load("./test/2019.04.03-14.47.53_keylist.npy")
# atkSbox = [sbox[atkPText[i][0] ^ atkKey[i][0]] for i in range(len(atkPText))] 
# atkHW   = [hw[s] for s in atkSbox]

# tempTraces = abs(fft(tempTraces))
# atkTraces = abs(fft(atkTraces))


# print("开始PCA降维")
# pca = PCA(n_components=600)
# pca.fit(tempTraces)
# joblib.dump(pca, "./PCAfft_for_mlp.m")
# '''
# pca = joblib.load("./PCAfft_for_mlp.m")
# '''
# tempTraces = pca.transform(tempTraces)
# print("完成PCA")

# print(tempTraces.shape)
# atkTraces = pca.transform(atkTraces)

# history = model.fit(tempTraces, to_categorical(tempHW), epochs=60, batch_size=16,validation_split=0.05)
# loss_and_metrics = model.evaluate(atkTraces, to_categorical(atkHW,num_classes=9), batch_size=128)
# #print(model.predict(atkTraces))
# guss = model.predict(atkTraces)
# a = np.zeros(100)
# for i in range(100):
#     a[i] = abs(np.argmax(guss[i,:]) - atkHW[i])
# print("差值数组为："+str(a))
# print("测试集正确率为："+str(loss_and_metrics[1]))
# right = 0
# for i in range(100):
#     if a[i] == 0:
#         right = right + 1
# print("汉明重量正确的有"+str(right)+"个")
# plot_model(model,show_shapes=True,to_file='fft_model.png')
# plt.plot(history.history['accuracy'])
# plt.plot(history.history['val_accuracy'])
# plt.title('Model accuracy')
# plt.ylabel('Accuracy')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Test'], loc='upper left')
# plt.show()

# 绘制训练 & 验证的损失值
# plt.plot(history.history['loss'])
# plt.plot(history.history['val_loss'])
# plt.title('Model loss')
# plt.ylabel('Loss')
# plt.xlabel('Epoch')
# plt.legend(['Train', 'Test'], loc='upper left')
# plt.show()
result = []
for dig in range(16):
    print(str(dig)+" dig")
    tempTraces = np.load('./train/traces.npy')
    tempPText  = np.load('./train/textin.npy')
    tempKey    = np.load('./train/keylist.npy')
    tempSbox = [sbox[tempPText[i][dig] ^ tempKey[i][dig]] for i in range(len(tempPText))] 
    tempHW   = [hw[s] for s in tempSbox]

    atkTraces = np.load("./test/2019.04.03-14.47.53_traces.npy")
    atkPText  = np.load("./test/2019.04.03-14.47.53_textin.npy")
    atkKey    = np.load("./test/2019.04.03-14.47.53_keylist.npy")
    atkSbox = [sbox[atkPText[i][dig] ^ atkKey[i][dig]] for i in range(len(atkPText))] 
    atkHW   = [hw[s] for s in atkSbox]

    tempTraces = abs(fft(tempTraces))
    atkTraces = abs(fft(atkTraces))


    print("start PCA")
    pca = PCA(n_components=600)
    pca.fit(tempTraces)
    joblib.dump(pca, "./PCAfft_for_mlp.m")
    '''
    pca = joblib.load("./PCAfft_for_mlp.m")
    '''
    tempTraces = pca.transform(tempTraces)
    print("finish PCA")

    print(tempTraces.shape)
    atkTraces = pca.transform(atkTraces)

    history = model.fit(tempTraces, to_categorical(tempHW), epochs=60, batch_size=16,validation_split=0.05)
    loss_and_metrics = model.evaluate(atkTraces, to_categorical(atkHW,num_classes=9), batch_size=128)
    #print(model.predict(atkTraces))
    guss = model.predict(atkTraces)
    a = np.zeros(100)
    for i in range(100):
        a[i] = abs(np.argmax(guss[i,:]) - atkHW[i])
    print("matrix:"+str(a))
    print("accu:"+str(loss_and_metrics[1]))
    right = 0
    for i in range(100):
        if a[i] == 0:
            right = right + 1
    result.append(a)

rate = []
corr_list = np.zeros(16)
for i in range(len(result[0])):
    num = 0
    for j in range(16):
        if result[j][i] == 0:
            corr_list[j] = 1
    rate.append(corr_list.sum()/16*100)

print(rate)
plt.plot(rate)
plt.grid()
plt.show()
