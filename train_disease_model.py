import os
import numpy as np
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

# Your small dataset path (change only if different)
DATA_DIR = r"C:\cropwisex\small_plantvillage"

# Your 6 class names (must match your subfolder names exactly)
CLASSES = [
    "Tomato_Healthy",
    "Tomato_Early_Blight",
    "Tomato_Late_Blight",
    "Potato_Healthy",
    "Potato_Early_Blight",
    "Potato_Late_Blight"
]

# Data preparation
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

train_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(224, 224),
    batch_size=16,
    class_mode='categorical',
    classes=CLASSES,
    subset='training'
)

val_gen = datagen.flow_from_directory(
    DATA_DIR,
    target_size=(224, 224),
    batch_size=16,
    class_mode='categorical',
    classes=CLASSES,
    subset='validation'
)

# Build fast model
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(len(CLASSES), activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=predictions)

model.compile(optimizer=Adam(learning_rate=0.001), loss='categorical_crossentropy', metrics=['accuracy'])

# Train (fast)
print("Starting training...")
model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=8,  # 8 epochs is enough for small data
    verbose=1
)

# Save
model.save("crop_disease_model.h5")
print("Model saved as crop_disease_model.h5")
print("Class order (remember this!):", CLASSES)