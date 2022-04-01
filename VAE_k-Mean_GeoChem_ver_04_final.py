# !pip install spectral
# !pip install rasterio


import wandb
from wandb.keras import WandbCallback

# Basic import
import matplotlib.pyplot as plt
import numpy as np
from time import time
import rasterio as rio
from sklearn.preprocessing import minmax_scale
from sklearn import cluster
from sklearn.decomposition import PCA


from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score


import pandas as pd
import seaborn as sns
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras

# testing variable
parts = 1 
wandb.login(key='2ab92307128f1ed1aa03d4688a9cf19b1f1c0b93')
wandb.init(project="Geo_chem_autoencoder")
wandb.init(config={"hyper": "parameter"})
# import wandb
# api = wandb.Api()

# run = api.run("fast-flow/Geo_chem_autoencoder/<run_id>")
# run.config["key"] = updated_value
# run.update()

# Importing the data
data_raster = rio.open('Dataset/Wilcannia_Sentinel2.tif')
data_test   = rio.open('Dataset/Wilcannia_RockUnits_15m.tif')
# print(data_raster.meta)
parts += 1
print('step-:',parts)
## Visualizing the data
# Reading and enhancing
data_array = data_raster.read() # reading the data
vmin, vmax = np.nanpercentile(data_array, (5,95)) # 5-95% pixel values stretch


parts += 1
print('step-:',parts)


data_array_test = data_test.read() # reading the data
vmin, vmax = np.nanpercentile(data_array_test, (5,95)) # 5-95% pixel values stretch
# Plotting the enhanced image
# fig = plt.figure(figsize=[20,20])
# plt.axis('off')
# plt.imshow(data_array[0, :, :], vmin=vmin, vmax=vmax)
# plt.show()
parts += 1
print('step-:',parts)

## Reshaping the Train data from brc to rcb
# Creating an empty array with the same dimension and data type
imgxyb = np.empty((data_raster.height, data_raster.width, data_raster.count), data_raster.meta['dtype'])
# Looping through the bands to fill the empty array
no_of_bands = 0
for band in range(imgxyb.shape[2]):
    no_of_bands += 1
    imgxyb[:,:,band] = data_raster.read(band+1)
print('No of bands: ', no_of_bands)

parts += 1
print('step-:',parts)

# Reshaping the input data from rcb to samples and features
data_reshaped = imgxyb.reshape(imgxyb.shape[0]*imgxyb.shape[1], -1)
# Scaling
data_reshaped = minmax_scale(data_reshaped, feature_range=(0, 1), axis=0, copy=False)
print(data_reshaped.shape)

## Reshaping the Test data from brc to rcb
# Creating an empty array with the same dimension and data type
imgxyb_test = np.empty((data_test.height, data_test.width, data_test.count), data_test.meta['dtype'])
# Looping through the bands to fill the empty array
parts += 1
print('step-:',parts)

for band in range(imgxyb_test.shape[2]):
    imgxyb_test[:,:,band] = data_test.read(band+1)

# Reshaping the input data from rcb to samples and features
data_reshaped_test = imgxyb_test.reshape(imgxyb_test.shape[0]*imgxyb_test.shape[1], -1)
# Scaling
data_reshaped_test = minmax_scale(data_reshaped, feature_range=(0, 1), axis=0, copy=False)
data_reshaped_test.shape
parts += 1
print('step-:',parts)

# divide data in Train - Validation - Test
X_train, X_test, y_train, y_test = train_test_split(data_reshaped, data_reshaped_test, test_size=0.1, random_state=42)
X_tr, X_valid, y_tr, y_valid = train_test_split(X_train, y_train, test_size=0.20, random_state=42)

# Standardize Data
sc = StandardScaler()
X_tr_std = sc.fit_transform(X_tr)
X_valid_std = sc.transform(X_valid)
X_test_std = sc.transform(X_test)

parts += 1
print('step-:',parts)

# Let’s set up this AE:

encoder = keras.models.Sequential([
    keras.layers.Dense(9, input_shape=[10]),  ## here edit
    keras.layers.Dense(9, input_shape=[9]),
    keras.layers.Dense(9, input_shape=[9]),

    keras.layers.Dense(9, input_shape=[9]),
    keras.layers.Dense(9, input_shape=[9]),
    keras.layers.Dense(9, input_shape=[9]),

    keras.layers.Dense(9, input_shape=[9]),
    keras.layers.Dense(7, input_shape=[8]),
    keras.layers.Dense(6, input_shape=[7]),

    keras.layers.Dense(5, input_shape=[6]),
])

decoder = keras.models.Sequential([
    keras.layers.Dense(6, input_shape=[5]),  ## here edit

    keras.layers.Dense(7, input_shape=[6]),
    keras.layers.Dense(8, input_shape=[7]),
    keras.layers.Dense(9, input_shape=[8]),

    keras.layers.Dense(9, input_shape=[9]),
    keras.layers.Dense(9, input_shape=[9]),
    keras.layers.Dense(9, input_shape=[9]),

    keras.layers.Dense(9, input_shape=[9]),
    keras.layers.Dense(9, input_shape=[9]),
    keras.layers.Dense(10, input_shape=[9]),
])

autoencoder = keras.models.Sequential([encoder, decoder])
autoencoder.compile(loss='mse', optimizer = keras.optimizers.SGD(learning_rate=0.01))
autoencoder.summary()
history = autoencoder.fit(X_tr_std,X_tr_std, epochs=20, validation_data=(X_valid_std,X_valid_std), # here epochs
                         callbacks=[WandbCallback()])
parts += 1
print('step-:',parts)
# NonLinear Stacked Encoder-Decoder

# nl_st_encoder = keras.models.Sequential([
#     keras.layers.Dense(9, input_shape=[10], activation='relu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(8, activation='selu'),
#     keras.layers.Dense(7, activation='selu'),
#     keras.layers.Dense(6, activation='selu'),
#     keras.layers.Dense(5, activation='selu'),
# ])

# nl_st_decoder = keras.models.Sequential([
#     keras.layers.Dense(6, input_shape=[5], activation='selu'),
#     keras.layers.Dense(7, activation='selu'),
#     keras.layers.Dense(8, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(9, activation='selu'),
#     keras.layers.Dense(10, activation='relu'),
# ])

# nl_st_autoencoder = keras.models.Sequential([nl_st_encoder, nl_st_decoder])
# nl_st_autoencoder.compile(loss='mse', optimizer = keras.optimizers.SGD(lr=0.01, decay=1e-4))
# nl_st_autoencoder.summary()


# history = nl_st_autoencoder.fit(X_tr_std,X_tr_std, epochs=20,validation_data=(X_valid_std,X_valid_std),
#                          callbacks=[keras.callbacks.EarlyStopping(patience=10)],verbose=1)

# wandb.log({'history': history})
parts += 1
print('step-:',parts)
nl_st_codings_train = encoder.predict(X_tr_std)
nl_st_codings_test = encoder.predict(X_test_std)
print(history.history.keys())

# with open('/trainHistoryDict', 'wb') as file_pi:
#         pickle.dump(history.history, file_pi)

codings = encoder.predict(X_tr_std)

# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()
plt.savefig("summarize history for loss nl_st_ae.jpg")

parts += 1
print('step-:',parts)
# PCA 
from sklearn.decomposition import PCA
# pca = PCA(n_components=5,svd_solver='auto')
# scores = pca.fit_transform(X_tr_std) # u


components_num = 5 
pca = PCA(n_components=components_num)
scores = pca.fit_transform(data_reshaped)
var_ratio = pca.explained_variance_ratio_
values = pca.singular_values_

print(var_ratio.shape)
print(values)

parts += 1
print('step-:',parts)
# function to plot and display the image
def plot_data(data,fig_name):
  fig = plt.figure(figsize = (15, 10))
  plt.imshow(data, cmap = 'nipy_spectral')
  plt.colorbar()
  plt.axis('off')
  plt.show()
  plt.savefig(fig_name)

# Clustring

# K-means(PCA)
cl_pca = cluster.KMeans(n_clusters=5) # Creating an object of the classifier      #### HERE clusters 
                                                            #### HERE components,  
param = cl_pca.fit(scores[:,:components_num]) # Training
img_c_pca = cl_pca.labels_ # Getting the labels of the classes
img_cl_pca = img_c_pca.reshape(data_array[0,:,:].shape) # Reshaping the labels to a 3D array (single band)
plot_data(img_cl_pca, 'PCA_k_meansnl_st_.png')

parts += 1
print('step-:',parts)

# K-means (Autoenocder)
cl = cluster.KMeans(n_clusters=5) # Creating an object of the classifier     #### HERE clusters 
param = cl.fit(codings) # Training
img_cl = cl.labels_ # Getting the labels of the classes
# img_cl_pred = cl.predict(data_ae)
img_c2 = img_cl.reshape(data_array[0,:,:].shape) # Reshaping the labels to a 3D array (single band)
plot_data(img_c2, 'nl_st_AE_k_means.png')


codings_train = nl_st_encoder.predict(X_tr_std)   ## endoder edit
codings_test  = nl_st_encoder.predict(X_test_std)  ## encoder edit
scores_train  = pca.transform(X_tr_std)
scores_test   = pca.transform(X_test_std)



parts += 1
print('step-:',parts)
# pd.DataFrame(scores_train, columns=['PC'+str(i) for i in range(pca.n_components_)]).std().plot(kind='bar', color='tab:green')
# plt.ylabel('scores std. dev.');
# plt.savefig('scores_std_devnl_st_.png')

# sns.heatmap(pd.DataFrame(scores_train, columns=['PC'+str(i) for i in range(pca.n_components_)]).corr(), vmin=-1, vmax=+1, cmap='coolwarm', annot=True)
# plt.savefig('heatmap_confusion_matrix_of_PCAnl_st_.png')

# sns.heatmap(pd.DataFrame(codings_train, columns=['E'+str(i) for i in range(5)]).corr(), vmin=-1, vmax=+1, cmap='coolwarm', annot=True) #### HERE range, 
# plt.savefig('heatmap_confusion_matrix_of_AEnl_st_.png')

# sns.heatmap(pd.concat([pd.DataFrame(scores_train, columns=['PC'+str(i) for i in range(pca.n_components_)]),
#                        pd.DataFrame(codings_train, columns=['E'+str(i) for i in range(pca.n_components_)]),
#                        pd.DataFrame(y_tr, columns=['E'+str(i) for i in range(9)])],1).corr(), 
#             vmin=-1, vmax=1, cmap='coolwarm',annot=True, fmt='.2f')
# plt.savefig('heatmap_confusion_matrix_Original_PCA_AE.png')


# # RandomForestClassifier using cross validation

# rfc = RandomForestClassifier(n_estimators=200, max_depth=5)

# labels = ['Original', 'PCA','AE']
# scores = pd.DataFrame(columns=labels)
# scores['PCA'] = cross_val_score(rfc, scores_train, y_tr, cv=5)
# scores['AE'] = cross_val_score(rfc, codings_train, y_tr, cv=5)
# scores['Original'] = cross_val_score(rfc, X_tr_std, y_tr, cv=5)

# sns.barplot(x='dataset', y='score', data = scores.melt(value_name='score', var_name='dataset'))
# plt.ylim(0.9,1)
# plt.savefig('heatmap_confusion_matrix_of_AE.png')



####              #####
####     VAE      #####
####              #####



# mnist_vae_viz.py

# PyTorch variational autoencoder for MNIST visualization
# compress each 28x28 MNIST digit to 2 values then plot

# use custom generated text MNIST rather than
# the built-in torchvision MNIST

# PyTorch 1.8.0-CPU Anaconda3-2020.02  Python 3.7.6
# CPU, Windows 10

import numpy as np
import torch as T
import matplotlib.pyplot as plt
import torchvision as tv  # to visualize fakes

device = T.device("gpu")

# -----------------------------------------------------------

class dataset_playa():
  # for an Autoencoder (not a classifier)
  # assumes data has been converted to tab-delim text files:
  # 7 pixel values (0-255) (tab) label (0-9)
  # [0] [1] . . [7] [7] 

  def __init__(self, tmp_x,tmp_y):
    # tmp_x = np.loadtxt(src_file, usecols=[784],
    #   deliminp.loadtxt(src_file, usecols=range(0,7),
    #   delimiter="\t", comments="#", dtype=np.float32)
    # tmp_y = ter="\t", comments="#", dtype=np.int64)
    self.x_data = T.tensor(tmp_x, dtype=T.float32).to(device) 
    self.x_data /= 255.0  # normalize pixels
    self.y_data = T.tensor(tmp_y, dtype=T.int64).to(device)
    # don't normalize digit labels

  def __len__(self):
    return len(self.x_data)

  def __getitem__(self, idx):
    pixels = self.x_data[idx]
    label = self.y_data[idx]
    return (pixels, label)

# -----------------------------------------------------------
# for the dataset (after reshaping the data)

# def dataset_playa(temp_x,tmp_y):
#   
#   x_data = T.tensor(tmp_x, dtype=T.float32).to(device) 
#   x_data /= 255.0  # normalize pixels
#   y_data = T.tensor(temp_y, dtype=T.int64).to(device)
#   return pixels, label

# -----------------------------------------------------------

class VAE(T.nn.Module):  # [7-6-5-[2,2]-2-5-7]
  def __init__(self):
    super(VAE, self).__init__()  
    self.fc1a = T.nn.Linear(7, 6)  # no labels
    self.fc1b = T.nn.Linear(6, 5)  # no labels

    self.fc2a = T.nn.Linear(5, 2)   # u
    self.fc2b = T.nn.Linear(5,2)   # log-var


    self.fc3 = T.nn.Linear(2, 5)
    self.fc4a = T.nn.Linear(5, 6) 
    self.fc4b  = T.nn.Linear(6, 7)

  def encode(self, x):              # 7-5-[2,2]  
    z = T.relu(self.fc1a(x)) 
    z = T.relu(self.fc1b(z))
    z1 = self.fc2a(z)               # activation here ??
    z2 = self.fc2b(z) 
    return (z1, z2)                 # (u, log-var)

  def decode(self, x):              # 2-5-7
    z = T.relu(self.fc3(x))
    z = T.sigmoid(self.fc4a(z))     
    z = T.sigmoid(self.fc4b(z))      # in [0, 1]
    return z 

  def forward(self, x):
    (u, logvar) = self.encode(x)
    stdev = T.exp(0.5 * logvar)
    noise = T.randn_like(stdev)
    z = u + (noise * stdev)         # [2]
    oupt = self.decode(z)
    return (oupt, u, logvar)

# -----------------------------------------------------------

def cus_loss_func(recon_x, x, u, logvar):
  # https://arxiv.org/abs/1312.6114
  # KLD = 0.5 * sum(1 + log(sigma^2) - u^2 - sigma^2)
  # bce = T.nn.functional.binary_cross_entropy(recon_x, \
  #   x.view(-1, 784), reduction="sum")

  # mse = T.nn.functional.mse_loss(recon_x, x.view(-1, 784))
  mse = T.nn.functional.mse_loss(recon_x, x)

  kld = -0.5 * T.sum(1 + logvar - u.pow(2) - \
    logvar.exp())

  BETA = 1.0
  return mse + (BETA * kld)

# -----------------------------------------------------------

def train(vae, ds, bs, me, lr, le):
  # train autoencoder vae with dataset ds using batch size bs, 
  # with max epochs me, learn rate lr, log_every le
  data_ldr = T.utils.data.DataLoader(ds, batch_size=bs,
    shuffle=True)
  
  # loss_func = T.nn.MSELoss() # use custom loss
  opt = T.optim.SGD(vae.parameters(), lr=lr)
  print("Starting training")
  for epoch in range(0, me):
    for (b_idx, batch) in enumerate(data_ldr):
      opt.zero_grad()
      X = batch[0]  # don't use Y labels to train
      recon_x, u, logvar = vae(X)
      loss_val = cus_loss_func(recon_x, X, u, logvar)
      loss_val.backward()
      opt.step()

    if epoch != 0 and epoch % le == 0:
      print("epoch = %6d" % epoch, end="")
      print("  curr batch loss = %7.4f" % loss_val.item(), end="")
      print("")

      # save and view sample images as sanity check
      num_images = 64
      rinpt = T.randn(num_images, 2).to(device)
      # with T.no_grad():
      #   fakes = vae.decode(rinpt)
      # fakes = fakes.view(num_images, 1, 28, 28)
      # tv.utils.save_image(fakes,
      #   ".\\Fakes\\fakes_" + str(epoch) + ".jpg",
      #   padding=4, pad_value=1.0) # no overwrite

  print("Training complete ")

# -----------------------------------------------------------
# divide data in Train - Validation - Test
# X_train, X_test, y_train, y_test = train_test_split(data_reshaped, data_reshaped_test, test_size=0.3, random_state=42)
# X_tr, X_valid, y_tr, y_valid = train_test_split(X_train, y_train, test_size=0.2, random_state=42) 


# -----------------------------------------------------------
def main():
  # 0. get started
  print("\nBegin VAE visualization ")
  T.manual_seed(1)
  np.random.seed(1)

  # 1. create Dataset object
  print("\nCreating  Dataset ")
  # fn = ".\\Data\\mnist_train_10000.txt"
  # data_ds = MNIST_Dataset(fn)           ############################################ reshaped dataset here.    #############
  data_ds = dataset_playa(X_train,y_train)
  # 2. create and train VAE model 
  print("\nCreating VAE  \n")
  vae = VAE()   # 7-5-[2,2]-2-5-7
  vae.train()           # set mode

  # Hyperparameters
  batch_size = 1000
  max_epochs = 40
  lrn_rate = 0.1
  log_every = int(max_epochs / 10)
  train(vae, data_ds, batch_size, max_epochs, lrn_rate, log_every)

  # 3. TODO: save trained VAE

  # 4. use model encoder to generate (x,y) pairs
  vae.eval()
  all_pixels = data_ds[0:1000][0]  # all pixel values
  all_labels = data_ds[0:1000][1]

  with T.no_grad():
    u, logvar = vae.encode(all_pixels) # mean logvar

  print("\nImages reduced to 2 values (std and var): ")
  print(u)

  # 5. graph the reduced-form digits in 2D
  print("\nPlotting reduced-dim images")
  plt.scatter(u[:,0], u[:,1],
            c=all_labels, edgecolor='none', alpha=0.9,
            cmap=plt.cm.get_cmap('nipy_spectral', 11),
            s=20)  # s=20 orig, alpha=0.9
  plt.xlabel('mean[0]')
  plt.ylabel('mean[1]')
  plt.colorbar()
  # plt.show()
  plt.savefig('VAE visualization.png')

  print("\nEnd VAE visualization")

# -----------------------------------------------------------

if __name__ == "__main__":
  main()


