# pip install rasterio
# pip install spectral

import matplotlib.pyplot as plt
import numpy as np
from time import time
import rasterio as rio

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard

from sklearn.preprocessing import minmax_scale
from sklearn import cluster
from sklearn.decomposition import PCA

# Importing the data
data_raster = rio.open('Dataset/Delamerian_Landsat8.tif')
# print(data_raster.meta)

## Visualizing the data
# Reading and enhancing
print('reading the data')
data_array = data_raster.read() # reading the data
# vmin, vmax = np.nanpercentile(data_array, (5,95)) # 5-95% pixel values stretch
# Plotting the enhanced image
# fig = plt.figure(figsize=[20,20])
# plt.axis('off')
# plt.imshow(data_array[1, :, :], cmap='gray', vmin=vmin, vmax=vmax)
# plt.show()

## Reshaping the input data from brc to rcb
# Creating an empty array with the same dimension and data type
imgxyb = np.empty((data_raster.height, data_raster.width, data_raster.count), data_raster.meta['dtype'])
# Looping through the bands to fill the empty array
for band in range(imgxyb.shape[2]):
    imgxyb[:,:,band] = data_raster.read(band+1)

# Reshaping the input data from rcb to samples and features
data_reshaped = imgxyb.reshape(imgxyb.shape[0]*imgxyb.shape[1], -1)
# Scaling
data_reshaped = minmax_scale(data_reshaped, feature_range=(0, 1), axis=0, copy=False)
print('reshaping the data')
# print(data_reshaped.shape)

def plot_data(data):
  fig = plt.figure(figsize = (15, 10))
  plt.imshow(data, cmap = 'nipy_spectral')
  plt.colorbar()
  plt.axis('off')
  plt.show()


pca = PCA(n_components=data_array.shape[0])
components = pca.fit_transform(data_reshaped)
var_ratio = pca.explained_variance_ratio_
values = pca.singular_values_
# print()
print(var_ratio.shape)
print(values)
def calculate_WSS(points, kmax):
  sse = []
  for k in range(1, kmax+1):
    kmeans = cluster.KMeans(n_clusters = k).fit(points)
    centroids = kmeans.cluster_centers_
    pred_clusters = kmeans.predict(points)
    curr_sse = 0

    # calculate square of Euclidean distance of each point from its cluster center and add to current WSS
    for i in range(len(points)):
      curr_center = centroids[pred_clusters[i]]
      curr_sse += (points[i, 0] - curr_center[0]) ** 2 + (points[i, 1] - curr_center[1]) ** 2

    sse.append(curr_sse)
  return sse
# hyperparameyers
kmax            = 20
components_num  = 10
n_clusters      = 10
no_epochs       = 100
encoding_dim    = 10
print('hyperparameters   ')
print('no of compenents  ', components_num)
print('max no of clusters', kmax)
print('Number of clusters', n_clusters)
print('Epochs            ', no_epochs)
print('Encoding dimension', encoding_dim)
sse = calculate_WSS(components[:,:components_num], kmax)
print(sse)
# plot_data(sse)

# from sklearn.metrics import silhouette_score

# sil = []

## The Silhouette Method
# dissimilarity would not be defined for a single cluster, thus, minimum number of clusters should be 2
# for k in range(2, kmax+1):
#   kmeans = cluster.KMeans(n_clusters = k).fit(components[:,:components_num])
#   labels = kmeans.labels_
#   sil.append(silhouette_score(components[:,:components_num], labels, metric = 'euclidean'))
# print(sil)


# K-means
cl = cluster.KMeans(n_clusters) # Creating an object of the classifier
# components_num = 5
param = cl.fit(components[:,:components_num]) # Training
img_c = cl.labels_ # Getting the labels of the classes
img_cl = img_c.reshape(data_array[0,:,:].shape) # Reshaping the labels to a 3D array (single band)
# plot_data(img_cl)



# Building the autoencoder

print('Encoding dimensions =', encoding_dim)
input_dim = Input(shape = (data_reshaped.shape[-1], ), name = 'InputLayer')

# Encoder layers
encoded0 = Dense(150, activation = 'relu', name = 'EncodeLayer0')(input_dim)
encoded1 = Dense(100, activation = 'relu', name = 'EncodeLayer1')(encoded0)
encoded2 = Dense(90, activation = 'relu', name = 'EncodeLayer2')(encoded1)
encoded3 = Dense(85, activation = 'relu', name = 'EncodeLayer3')(encoded2)
encoded4 = Dense(80, activation = 'relu', name = 'EncodeLayer4')(encoded3)
encoded5 = Dense(75, activation = 'relu', name = 'EncodeLayer5')(encoded4)
encoded6 = Dense(70, activation = 'relu', name = 'EncodeLayer6')(encoded5)

# Coded part
encoded7 = Dense(encoding_dim, activation = 'linear', name = 'CodeLayer')(encoded6)

# Decoder layers
decoded1 = Dense(70, activation = 'relu', name = 'DecodeLayer1')(encoded7)
decoded2 = Dense(75, activation = 'relu', name = 'DecodeLayer2')(decoded1)
decoded3 = Dense(80, activation = 'relu', name = 'DecodeLayer3')(decoded2)
decoded4 = Dense(85, activation = 'relu', name = 'DecodeLayer4')(decoded3)
decoded5 = Dense(90, activation = 'relu', name = 'DecodeLayer5')(decoded4)
decoded6 = Dense(100, activation = 'relu', name = 'DecodeLayer6')(decoded5)
decoded7 = Dense(150, activation = 'relu', name = 'DecodeLayer7')(decoded6)

decoded8 = Dense(data_reshaped.shape[-1], activation = 'sigmoid', name = 'OutputLayer')(decoded7)

print(input_dim)

# Combining encoder and deocder layers
autoencoder = Model(inputs = input_dim, outputs = decoded8)

autoencoder.summary()

# Compiling the model
autoencoder.compile(optimizer = 'adam',
                    loss = 'mse',
                    metrics = [tf.keras.metrics.MeanSquaredLogarithmicError()]
                    )

# Callbacks
## Early stopping
early_stop = EarlyStopping(monitor = 'mean_squared_logarithmic_error',
                            mode = 'min',
                            min_delta = 0,
                            patience = 5,
                            restore_best_weights = True)

## Checkpoint
checkpoint = ModelCheckpoint(filepath = 'Path/checkpoint.h5',
                             monitor = 'mean_squared_logarithmic_error',
                             mode ='min',
                             save_best_only = True)

## Tensorboard
tensorboard = TensorBoard(log_dir='Path\{}'.format(time()))

# Fitting the model
hist = autoencoder.fit(data_reshaped,
                       data_reshaped,
                       epochs = no_epochs,
                       batch_size = 256,
                       shuffle = True,
                       callbacks=[early_stop,
                                  checkpoint,
                                  tensorboard])

# Seperating the encoder part from the auto encoder model
encoder = Model(inputs = input_dim, outputs = encoded7)

# Summary
# encoder.summary()

# Getting the data with the reduced dimesion
data_ae = encoder.predict(data_reshaped)

# K-means
cl = cluster.KMeans(n_clusters=10) # Creating an object of the classifier
param = cl.fit(data_ae) # Training
img_c = cl.labels_ # Getting the labels of the classes
# img_cl_pred = cl.predict(data_ae)
img_cl = img_cl.reshape(data_array[0,:,:].shape) # Reshaping the labels to a 3D array (single band)
save.plot_data(img_cl)
