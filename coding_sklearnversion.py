# -*- coding: utf-8 -*-
"""Coding-sklearnversion.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Aw6atbTET6S3aYYbvsmevpygt2hx9icr
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from google.colab import drive
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, log_loss

# Mount Google Drive
drive.mount('/content/gdrive', force_remount=True)

# Load datasets
ckd_data = pd.read_csv('/content/gdrive/MyDrive/CKD.csv')
battery_data = pd.read_csv('/content/gdrive/MyDrive/Battery_Dataset.csv')

# Convert string labels to numerical labels
ckd_data['label'] = ckd_data['label'].map({'Normal': 0, 'CKD': 1})
battery_data['label'] = battery_data['label'].map({'Normal': 0, 'Defective': 1})

# Logistic Regression Implementation
class LogisticRegression:
    def __init__(self, learning_rate=0.001, epochs=1000, lambda_=0.1):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.lambda_ = lambda_  # Regularization parameter
        self.weights = None
        self.bias = None
        self.loss_history = []  # To store loss values

    def sigmoid(self, z):
        z = np.clip(z, -500, 500)  # Prevents overflow
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0

        for epoch in range(self.epochs):
            linear_model = np.dot(X, self.weights) + self.bias
            y_predicted = self.sigmoid(linear_model)

            # Compute log loss
            loss = log_loss(y, y_predicted)
            self.loss_history.append(loss)

            # Gradient with regularization
            dw = (1 / n_samples) * (np.dot(X.T, (y_predicted - y)) + self.lambda_ * self.weights)
            db = (1 / n_samples) * np.sum(y_predicted - y)

            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

    def predict(self, X):
        linear_model = np.dot(X, self.weights) + self.bias
        y_predicted = self.sigmoid(linear_model)
        return [1 if i > 0.5 else 0 for i in y_predicted]

# Accuracy Evaluation
def accuracy(y_true, y_pred):
    return np.sum(y_true == y_pred) / len(y_true)

# K-Fold Cross-Validation
class KFoldCV:
    def __init__(self, k=10):
        self.k = k

    def split(self, X, y):
        indices = np.arange(len(X))
        np.random.shuffle(indices)
        folds = np.array_split(indices, self.k)
        return folds

    def evaluate(self, model, X, y):
        folds = self.split(X, y)
        accuracies = []

        for i in range(self.k):
            test_idx = folds[i]
            train_idx = np.concatenate([folds[j] for j in range(self.k) if j != i])

            X_train, y_train = X[train_idx], y[train_idx]
            X_test, y_test = X[test_idx], y[test_idx]

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            accuracies.append(accuracy(y_test, y_pred))

        return np.mean(accuracies)

# Prepare datasets
scaler = StandardScaler()
X_ckd = scaler.fit_transform(ckd_data.iloc[:, :-1].values)
y_ckd = ckd_data.iloc[:, -1].values
X_battery = scaler.fit_transform(battery_data.iloc[:, :-1].values)
y_battery = battery_data.iloc[:, -1].values

# Train and evaluate logistic regression model
log_reg = LogisticRegression(learning_rate=0.001, epochs=1000, lambda_=0.1)
kfold = KFoldCV(k=10)

ckd_accuracy = kfold.evaluate(log_reg, X_ckd, y_ckd)
battery_accuracy = kfold.evaluate(log_reg, X_battery, y_battery)

print(f"CKD Dataset Accuracy: {ckd_accuracy:.4f}")
print(f"Battery Dataset Accuracy: {battery_accuracy:.4f}")

# Plot learning curve
plt.plot(log_reg.loss_history)
plt.title("Learning Curve (Log Loss vs. Epochs)")
plt.xlabel("Epochs")
plt.ylabel("Log Loss")
plt.show()