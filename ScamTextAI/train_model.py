# 📌 Import Required Libraries
import pandas as pd
import string
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


# 📌 Step 1: Load Dataset
data = pd.read_csv("dataset.csv", encoding='latin-1')

# Keep only necessary columns
data = data[['v1', 'v2']]
data.columns = ['label', 'message']


# 📌 Step 2: Convert Labels to Numbers
# ham → 0 (Safe)
# spam → 1 (Scam)
data['label'] = data['label'].map({'ham': 0, 'spam': 1})


# 📌 Step 3: Text Cleaning Function
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = "".join([char for char in text if char not in string.punctuation])  # Remove punctuation
    return text


data['message'] = data['message'].apply(clean_text)


# 📌 Step 4: Split Data
X_train, X_test, y_train, y_test = train_test_split(
    data['message'],
    data['label'],
    test_size=0.2,
    random_state=42
)


# 📌 Step 5: Convert Text to Numerical Features (TF-IDF)
vectorizer = TfidfVectorizer(ngram_range=(1,2))  # Using bigrams for better accuracy
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)


# 📌 Step 6: Train Model (Naive Bayes)
model = MultinomialNB()
model.fit(X_train_vec, y_train)


# 📌 Step 7: Predict & Evaluate
y_pred = model.predict(X_test_vec)

accuracy = accuracy_score(y_test, y_pred)

print("📊 Model Accuracy:", round(accuracy * 100, 2), "%")
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))


# 📌 Step 8: Save Model & Vectorizer
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("\n✅ Model and Vectorizer Saved Successfully!")