"""
AI-powered log analyzer using trained ML model
"""

import numpy as np
import joblib
import re
import json

class AIAnalyzer:
    def __init__(self, model_path='models/ml_model.pkl', config_path='models/config.json'):
        """Initialize AI analyzer with trained model"""
        
        print("Loading AI model...")
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load('models/vectorizer.pkl')
        self.label_encoder = joblib.load('models/label_encoder.pkl')
        self.severity_encoder = joblib.load('models/severity_encoder.pkl')
        self.sw_encoder = joblib.load('models/sw_encoder.pkl')
        self.platform_encoder = joblib.load('models/platform_encoder.pkl')
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        print(f"✓ Model loaded (Accuracy: {self.config['accuracy']:.2%})")
    
    def preprocess(self, log_content, metadata):
        """Preprocess log for model input"""
        
        # Text features
        text_features = self.vectorizer.transform([log_content]).toarray()
        
        # Extract metadata
        sw_version = metadata.get('sw_version', 'AIVI_SW5244')
        platform = metadata.get('platform', 'gen3')
        has_missing = 1 if metadata.get('has_missing_blocks', False) else 0
        has_overwritten = 1 if metadata.get('has_overwritten', False) else 0
        log_size = len(log_content) / 50000.0
        
        # Encode categorical
        try:
            sw_encoded = self.sw_encoder.transform([sw_version])[0]
        except:
            sw_encoded = 0
        
        try:
            platform_encoded = self.platform_encoder.transform([platform])[0]
        except:
            platform_encoded = 0
        
        # Metadata features
        metadata_features = np.array([[
            sw_encoded,
            platform_encoded,
            has_missing,
            has_overwritten,
            log_size
        ]])
        
        # Combine
        features = np.hstack([text_features, metadata_features])
        
        return features
    
    def analyze(self, log_content, metadata=None):
        """
        Analyze log using AI model
        
        Returns:
            {
                'root_cause': str,
                'confidence': float,
                'top_3_predictions': list,
                'method': 'ai',
                'severity': str
            }
        """
        
        if metadata is None:
            metadata = self._extract_metadata_from_log(log_content)
        
        # Preprocess
        features = self.preprocess(log_content, metadata)
        
        # Predict
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        
        # Get root cause
        root_cause = self.label_encoder.inverse_transform([prediction])[0]
        confidence = probabilities[prediction]
        
        # Get top 3 predictions
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3_predictions = [
            {
                'cause': self.label_encoder.inverse_transform([idx])[0],
                'confidence': float(probabilities[idx])
            }
            for idx in top_3_indices
        ]
        
        # Infer severity
        severity = self._infer_severity(root_cause, confidence)
        
        # Generate explanation
        explanation = self._generate_explanation(log_content, root_cause, confidence)
        
        return {
            'root_cause': root_cause,
            'confidence': float(confidence),
            'top_3_predictions': top_3_predictions,
            'method': 'ai',
            'severity': severity,
            'explanation': explanation,
            'metadata': metadata
        }
    
    def _extract_metadata_from_log(self, log_content):
        """Extract metadata from log content"""
        metadata = {}
        
        # Extract SW version
        sw_match = re.search(r'(AIVI|PIVI)_SW\d+', log_content)
        if sw_match:
            metadata['sw_version'] = sw_match.group()
        
        # Extract platform
        platform_match = re.search(r'Platform:\s*(gen\d)', log_content)
        if platform_match:
            metadata['platform'] = platform_match.group(1)
        
        # Check for missing/overwritten blocks
        metadata['has_missing_blocks'] = 'missing' in log_content.lower()
        metadata['has_overwritten'] = 'overwritten' in log_content.lower()
        
        return metadata
    
    def _infer_severity(self, root_cause, confidence):
        """Infer severity based on root cause and confidence"""
        severity_map = {
            'Watchdog Timeout': 'CRITICAL',
            'Kernel Panic': 'CRITICAL',
            'Memory Leak': 'HIGH',
            'SW Update Failure': 'HIGH',
            'Hardware Fault': 'HIGH',
            'CAN Bus Error': 'MEDIUM',
            'File System Error': 'MEDIUM',
            'Network Timeout': 'LOW',
            'Unknown Issue': 'MEDIUM',
            'No Issue': 'LOW'
        }
        
        base_severity = severity_map.get(root_cause, 'MEDIUM')
        
        # Adjust based on confidence
        if confidence < 0.5:
            return 'UNCERTAIN'
        
        return base_severity
    
    def _generate_explanation(self, log_content, root_cause, confidence):
        """Generate human-readable explanation"""
        
        explanations = {
            'Memory Leak': 'Detected memory allocation issues and high memory usage patterns',
            'Watchdog Timeout': 'System reset triggered by watchdog timeout, indicating task execution delay',
            'CAN Bus Error': 'CAN communication failure detected with frame transmission errors',
            'SW Update Failure': 'Software update or flash operation failed',
            'Kernel Panic': 'Critical kernel error causing system halt',
            'File System Error': 'File system corruption or mount failure detected',
            'Network Timeout': 'Network connection timeout or communication failure',
            'Hardware Fault': 'Hardware component malfunction detected',
            'Unknown Issue': 'Unable to identify specific root cause from log patterns',
            'No Issue': 'No significant errors detected in log'
        }
        
        base_explanation = explanations.get(root_cause, 'Analysis based on ML model prediction')
        
        if confidence > 0.9:
            confidence_level = 'very high'
        elif confidence > 0.7:
            confidence_level = 'high'
        elif confidence > 0.5:
            confidence_level = 'moderate'
        else:
            confidence_level = 'low'
        
        return f"{base_explanation} (confidence: {confidence_level})"
    
    def analyze_file(self, file_path):
        """Analyze log from file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
        
        return self.analyze(log_content)
