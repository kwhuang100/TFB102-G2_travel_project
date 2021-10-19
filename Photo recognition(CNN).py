import numpy as np
import pandas as pd 
from keras.preprocessing.image import ImageDataGenerator, load_img
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import heapq
import random
import os
import cv2

def photo_tag_df():
    CATEGORIES = ['戶外踏青','文化古蹟','主題商圈','宗教祈福','登山健行','親子共遊','藝文館所']
    filenames = os.listdir("./train")
    categories = []
    for filename in filenames:
        category = filename.split('_')[0]
        if category == '登山健行':
            categories.append(1)
        elif category == '文化古蹟':
            categories.append(2)
        elif category == '親子共遊':
            categories.append(3)
        elif category == '主題商圈':
            categories.append(4)
        elif category == '戶外踏青':
            categories.append(5)        
        elif category == '宗教祈福':
            categories.append(6)          
        else:
            categories.append(7)   #藝文館所

    df = pd.DataFrame({
        'filename': filenames,
        'category': categories
    })
    
    return df

def CNN_Model():
    from keras.models import Sequential
    from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, Activation, BatchNormalization

    model = Sequential()

    model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_CHANNELS)))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(BatchNormalization())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(7, activation='softmax')) # 7 because we have 7 classes

    model.compile(loss='categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

    model.summary()
    return model

def prepare_data(df):
    df["category"] = df["category"].replace({1: '登山健行', 2: '文化古蹟', 3:'親子共遊', 4:'主題商圈'\
                                             , 5:'戶外踏青', 6:'宗教祈福', 7:'藝文館所'})
    train_df, validate_df = train_test_split(df, test_size = 0.2, random_state = 66 )
    train_df = train_df.reset_index(drop=True)
    validate_df = validate_df.reset_index(drop=True)
    return train_df, validate_df



def train_ImageDataGenerator(train_df,batch_size,IMAGE_SIZE):
    train_datagen = ImageDataGenerator(
        rotation_range=15,
        rescale=1./255,
        shear_range = 0.2,
        zoom_range = 0.2,
        horizontal_flip = True,
        width_shift_range = 0.1,
        height_shift_range = 0.1
    )

    train_generator = train_datagen.flow_from_dataframe(
        train_df, 
        "./train/", 
        x_col = 'filename',
        y_col = 'category',
        target_size = IMAGE_SIZE,
        class_mode = 'categorical',
        batch_size = batch_size
    )
    return train_generator
    
def validation_ImageDataGenerator(validate_df,batch_size,IMAGE_SIZE):    
    validation_datagen = ImageDataGenerator(rescale=1./255)
    validation_generator = validation_datagen.flow_from_dataframe(
        validate_df, 
        "./train/", 
        x_col='filename',
        y_col='category',
        target_size=IMAGE_SIZE,
        class_mode='categorical',
        batch_size= batch_size
    )
    return validation_generator

def train_test_split_result(train_df, validate_df):
    plt.rcParams['font.sans-serif'] = ['simhei'] 
    plt.rcParams.update({'font.size': 14})
    fig, axes = plt.subplots(2,1, figsize = (12,12))

    print("\nTrain_test_split result is following:")
    axes[0].set_title("train_df")
    train_df['category'].value_counts().plot.bar(ax=axes[0])
    axes[1].set_title("validate_df")
    validate_df['category'].value_counts().plot.bar(ax=axes[1])
    plt.tight_layout()

def model_fit(train_generator,epochs,batch_size ,validation_data, validation_steps, callbacks):
    epochs=3 if FAST_RUN else 50
    history = model.fit_generator(
                                    train_generator, 
                                    epochs = epochs,
                                    validation_data = validation_generator,
                                    validation_steps = total_validate// batch_size,
                                    steps_per_epoch = total_train// batch_size,
                                    callbacks = callbacks
                                    )
    return history

def model_result(history):
    fig, ax = plt.subplots(2, 1, figsize=(8, 12))
    ax[0].plot(history.history['loss'], label="Training loss")
    ax[0].plot(history.history['val_loss'], label="validation loss")
    legend = ax[0].legend(loc='best', shadow=True)
    ax[0].set_title("Traning Loss")
    ax[0].set_ylabel("Loss")
    ax[0].set_xlabel("Epochs")

    ax[1].plot(history.history['accuracy'], label="Training accuracy")
    ax[1].plot(history.history['val_accuracy'],label="Validation accuracy")
    legend = ax[1].legend(loc='best', shadow=True)
    ax[1].set_title("Traning Accuracy")
    ax[1].set_ylabel("Accuracy")
    ax[1].set_xlabel("Epochs")
    
def test_generator():
    test_gen = ImageDataGenerator(rescale=1./255)
    test_generator = test_gen.flow_from_dataframe(
        test_df, 
        "./test/", 
        x_col='filename',
        y_col=None,
        class_mode=None,
        target_size=IMAGE_SIZE,
        batch_size= batch_size ,
        shuffle=False
    )
    return test_generator

def each_photo_predict(predict, test_df):
    plt.rcParams.update({'font.size': 9})
    predict_lists = predict.tolist()
    max_large = []  # 第一大
    second_large = []  #第二大
    for i in range(0, len(predict_lists)):
        Top2_index_list = map(predict_lists[i].index, heapq.nlargest(2, predict_lists[i]))
        Top2_index_list = list(Top2_index_list)
        max_large.append(Top2_index_list[0])
        second_large.append(Top2_index_list[1])

    test_df['category1'] = max_large
    test_df['category2'] = second_large

    label_map = dict((v,k) for k,v in train_generator.class_indices.items())
    test_df['category1'] = test_df['category1'].replace(label_map)
    test_df['category2'] = test_df['category2'].replace(label_map)

    sample_test = test_df.head(35)
    sample_test.head()
    plt.figure(figsize=(12, 24))
    for index, row in sample_test.iterrows():
        filename = row['filename']
        category1 = row['category1']
        category2 = row['category2']
        img = load_img("./test/" + filename, target_size = IMAGE_SIZE)
        plt.subplot(7, 5, index+1)
        plt.imshow(img)
        plt.xlabel(filename + '(' + "{}".format(category1) + "/ {}".format(category2) + ')' )

    plt.tight_layout()
    plt.show()

    
## setting    
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
earlystop = EarlyStopping(patience=10)
learning_rate_reduction = ReduceLROnPlateau(monitor='val_loss', 
                                            patience=2, 
                                            verbose=1, 
                                            factor=0.5, 
                                            min_lr=0.00001)
callbacks = [earlystop, learning_rate_reduction]


FAST_RUN = False
IMAGE_WIDTH = 128
IMAGE_HEIGHT = 128
IMAGE_SIZE = (IMAGE_WIDTH, IMAGE_HEIGHT)
IMAGE_CHANNELS = 3

## preparing data and construct model
df = photo_tag_df()
model = CNN_Model()
train_df, validate_df = prepare_data(df)
train_test_split_result = train_test_split_result(train_df, validate_df)

## Data augumentation and train model
total_train = train_df.shape[0]
total_validate = validate_df.shape[0]
batch_size= 5

train_generator = train_ImageDataGenerator(train_df,batch_size,IMAGE_SIZE)
validation_generator = validation_ImageDataGenerator(validate_df,batch_size,IMAGE_SIZE)
history = model_fit(train_generator,epochs,batch_size, total_validate, total_train, callbacks)

## show model loss and accuracy
model_result = model_result(history)

## predict test data 
test_filenames = os.listdir("./test")
test_df = pd.DataFrame({
    'filename': test_filenames
})
nb_samples = test_df.shape[0]
test_generator = test_generator()
predict = model.predict_generator(test_generator, steps=np.ceil(nb_samples/batch_size))

## show result of test data prediction (Top2)
each_photo_predict = each_photo_predict(predict, test_df)