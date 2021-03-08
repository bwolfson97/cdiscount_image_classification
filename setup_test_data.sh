#!/bin/bash

# Add first n lines of train.csv and test.csv to test data
echo "Setting up test data..."
N="200"

for f in train.csv test.csv
do
    head -n $N data/$f > data/TESTING/$f
done

# Link images
ln -s ~/kaggle/cdiscount_image_classification/data/images ~/kaggle/cdiscount_image_classification/data/TESTING/images
echo "Completed."
