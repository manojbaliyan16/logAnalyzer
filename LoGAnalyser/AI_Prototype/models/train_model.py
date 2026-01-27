"""
Train ML model for log analysis
Uses Random Forest with TF-IDF features
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
import json

def prepare_features(df):
    """Prepare features for training"""
    
    print("Preparing features...")
    
    # Text features (TF-IDF)
    vectorizer = TfidfVectorizer(
        max_features=150,  # Increased for real logs
        ngram_range=(1, 3),  # Include trigrams for better crash pattern matching
        min_df=2,
        max_df=0.8,  # Ignore terms that appear in >80% of documents
        stop_words='english'
    )
    
    text_features = vectorizer.fit_transform(df['log_content']).toarray()
    print(f"Text features shape: {text_features.shape}")
    
    # Encode categorical features
    sw_encoder = LabelEncoder()
    platform_encoder = LabelEncoder()
    
    df['sw_version_encoded'] = sw_encoder.fit_transform(df['sw_version'])
    df['platform_encoded'] = platform_encoder.fit_transform(df['platform'])
    
    # Metadata features
    metadata_features = df[[
        'sw_version_encoded',
        'platform_encoded',
        'has_missing_blocks',
        'has_overwritten',
        'log_size'
    ]].values
    
    # Normalize log size
    metadata_features[:, 4] = metadata_features[:, 4] / 50000.0
    
    print(f"Metadata features shape: {metadata_features.shape}")
    
    # Combine features
    X = np.hstack([text_features, metadata_features])
    print(f"Combined features shape: {X.shape}")
    
    # Encode labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df['root_cause'])
    
    # Encode severity
    severity_encoder = LabelEncoder()
    y_severity = severity_encoder.fit_transform(df['severity'])
    
    return X, y, y_severity, vectorizer, label_encoder, severity_encoder, sw_encoder, platform_encoder

def train_model(data_path='data/combined_training.csv'):
    """Train the model"""
    
    print("=" * 60)
    print("Training AI Log Analyzer Model")
    print("=" * 60)
    
    # Try combined data first, fall back to synthetic
    if not os.path.exists(data_path):
        print(f"⚠ Combined data not found: {data_path}")
        data_path = 'data/synthetic_logs.csv'
        print(f"  Using synthetic data: {data_path}")
    
    # Load data
    print(f"\nLoading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples")
    
    # Prepare features
    X, y, y_severity, vectorizer, label_encoder, severity_encoder, sw_encoder, platform_encoder = prepare_features(df)
    
    # Split data
    print("\nSplitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Train model for root cause prediction
    print("\nTraining Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,  # More trees for better accuracy
        max_depth=25,  # Deeper trees for complex patterns
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\nEvaluating model...")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {accuracy:.2%}")
    
    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        zero_division=0
    ))
    
    # Feature importance
    print("\nTop 10 Important Features:")
    # Get actual number of text features from vectorizer
    n_text_features = len(vectorizer.get_feature_names_out())
    feature_names = (
        [f'text_{i}' for i in range(n_text_features)] +
        ['sw_version', 'platform', 'missing_blocks', 'overwritten', 'log_size']
    )
    
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(feature_importance.head(10))
    
    # Save model and artifacts
    print("\nSaving model and artifacts...")
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(model, 'models/ml_model.pkl')
    joblib.dump(vectorizer, 'models/vectorizer.pkl')
    joblib.dump(label_encoder, 'models/label_encoder.pkl')
    joblib.dump(severity_encoder, 'models/severity_encoder.pkl')
    joblib.dump(sw_encoder, 'models/sw_encoder.pkl')
    joblib.dump(platform_encoder, 'models/platform_encoder.pkl')
    
    # Save config
    config = {
        'classes': label_encoder.classes_.tolist(),
        'severity_classes': severity_encoder.classes_.tolist(),
        'sw_versions': sw_encoder.classes_.tolist(),
        'platforms': platform_encoder.classes_.tolist(),
        'accuracy': float(accuracy),
        'num_features': X.shape[1]
    }
    
    with open('models/config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✓ Model training complete!")
    print(f"✓ Model saved to models/ml_model.pkl")
    print(f"✓ Config saved to models/config.json")
    
    return model, vectorizer, label_encoder

if __name__ == '__main__':
    train_model()
