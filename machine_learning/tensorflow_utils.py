# machine_learning/tensorflow_utils.py

import tensorflow as tf

def load_model(model_path):
    """Loads a TensorFlow model from the specified path."""
    model = tf.keras.models.load_model(model_path)
    print(f"Model loaded from {model_path}.")
    return model

def make_prediction(model, input_data):
    """Makes a prediction using the provided model and input data."""
    prediction = model.predict(input_data)
    print(f"Prediction: {prediction}")
    return prediction

def evaluate_model(model, test_data, test_labels):
    """Evaluates the model on the test data and returns the loss and accuracy."""
    loss, accuracy = model.evaluate(test_data, test_labels)
    print(f"Model Evaluation - Loss: {loss}, Accuracy: {accuracy}")
    return loss, accuracy

def preprocess_data(data):
    """Preprocesses the input data for the model."""
    # Implement your preprocessing logic here (e.g., normalization, reshaping)
    processed_data = data / 255.0  # Example: Normalize pixel values
    print("Data preprocessed.")
    return processed_data
