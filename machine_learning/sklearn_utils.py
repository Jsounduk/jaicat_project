import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load a sample dataset for training
df = pd.read_csv("jarvis_dataset.csv")

# Create a TF-IDF vectorizer to convert text into numerical features
vectorizer = TfidfVectorizer()

# Fit the vectorizer to the training data and transform the text into features
X = vectorizer.fit_transform(df["text"])
y = df["label"]

# Train a logistic regression model on the features and labels
model = LogisticRegression()
model.fit(X, y)

# Use the trained model to make predictions on new input
new_text = "Turn on the living room lights"
new_features = vectorizer.transform([new_text])
prediction = model.predict(new_features)

print("Prediction:", prediction)
