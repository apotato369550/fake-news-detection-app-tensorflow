import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
import tensorflow as tf
from keras import layers, models, callbacks

csv_path = 'combined_data.csv'

df = pd.read_csv(csv_path)

# Shuffle the DataFrame
df = shuffle(df).reset_index(drop=True)

# Preprocess title
vectorizer_title = TfidfVectorizer(max_features=5000, stop_words='english')
X_title = vectorizer_title.fit_transform(df['title']).toarray()

# Preprocess text
vectorizer_text = TfidfVectorizer(max_features=5000, stop_words='english')
X_text = vectorizer_text.fit_transform(df['text']).toarray()

# Labels
y = df['true'].values

# Split the data into training and test sets
X_train_title, X_test_title, y_train, y_test = train_test_split(X_title, y, test_size=0.2, random_state=42)
X_train_text, X_test_text, _, _ = train_test_split(X_text, y, test_size=0.2, random_state=42)

# Define the model
input_title = layers.Input(shape=(X_train_title.shape[1],))
input_text = layers.Input(shape=(X_train_text.shape[1],))

# Title processing branch
title_branch = layers.Dense(128, activation='relu')(input_title)
title_branch = layers.Dropout(0.5)(title_branch)

# Text processing branch
text_branch = layers.Dense(128, activation='relu')(input_text)
text_branch = layers.Dropout(0.5)(text_branch)

# Combine branches
combined = layers.concatenate([title_branch, text_branch])

# Final dense layers
combined = layers.Dense(64, activation='relu')(combined)
combined = layers.Dropout(0.5)(combined)
output = layers.Dense(1, activation='sigmoid')(combined)

# Build the model
model = models.Model(inputs=[input_title, input_text], outputs=output)

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Early stopping to prevent overfitting
early_stopping = callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Train the model
model.fit([X_train_title, X_train_text], y_train, validation_split=0.2, epochs=20, batch_size=32, callbacks=[early_stopping])

# Evaluate the model
loss, accuracy = model.evaluate([X_test_title, X_test_text], y_test)
print(f"Test Accuracy: {accuracy}")

# Predict and generate a classification report
y_pred = model.predict([X_test_title, X_test_text])
y_pred_final = (y_pred > 0.5).astype(int)

from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred_final))


# Save the trained model
model.save('fake_news_model.h5')

# Save the vectorizers
import joblib
joblib.dump(vectorizer_title, 'vectorizer_title.pkl')
joblib.dump(vectorizer_text, 'vectorizer_text.pkl')

print("Model and vectorizers saved.")