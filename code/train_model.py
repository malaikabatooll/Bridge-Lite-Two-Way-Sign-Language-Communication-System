import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_csv("models/training_data.csv")

X = df.drop("label", axis=1)   # the 63 landmark numbers
y = df["label"]                 # the word each row belongs to

# Split off 20% of the data purely to test accuracy honestly,
# on samples the model never trained on
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Test accuracy: {acc*100:.2f}%")

joblib.dump(model, "models/word_classifier.pkl")
print("Model saved to models/word_classifier.pkl")
