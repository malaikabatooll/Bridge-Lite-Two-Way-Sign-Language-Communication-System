import pandas as pd
old = pd.read_csv("models/training_data.csv")
new = pd.read_csv("models/new_words_data.csv")
pd.concat([old, new], ignore_index=True).to_csv("models/training_data.csv", index=False)
