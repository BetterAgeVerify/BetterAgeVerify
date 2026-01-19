"""
BetterAgeVerify - Flask API Example
Created by luvaary

This example demonstrates how to create a simple REST API for age verification.
"""

import sys
from pathlib import Path
import io
import base64
import json

sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, render_template_string
from PIL import Image
from src.age_estimator import BetterAgeVerifyEstimator
from src.utils import EdgeCaseDetector, ConsentManager
from src.config import BetterAgeVerifyConfig as Config

app = Flask(__name__)
estimator = BetterAgeVerifyEstimator()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>BetterAgeVerify API Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
        }
        input[type="file"] {
            display: block;
            margin: 20px 0;
            padding: 10px;
            width: 100%;
            border: 2px dashed #3498db;
            border-radius: 4px;
        }
        button {
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background: #2980b9;
        }
        #result {
            margin-top: 20px;
            padding: 20px;
            border-radius: 4px;
            display: none;
        }
        .success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .info {
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .privacy {
            text-align: center;
            color: #27ae60;
            margin-top: 20px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 BetterAgeVerify</h1>
        <div class="subtitle">
            Privacy-First Age Verification API<br>
            Created by <strong>luvaary</strong>
        </div>
        
        <div class="info">
            ℹ️ <strong>Privacy Guarantee:</strong> Your image is processed locally and 
            all biometric data is deleted within 1 second. Nothing is stored.
        </div>
        
        <input type="file" id="imageFile" accept="image/*">
        <button onclick="verifyAge()">Verify Age</button>
        
        <div id="result"></div>
        <div class="privacy">✓ All biometric data deleted immediately</div>
    </div>
    
    <script>
        async function verifyAge() {
            const fileInput = document.getElementById('imageFile');
            const resultDiv = document.getElementById('result');
            
            if (!fileInput.files.length) {
                resultDiv.className = 'error';
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '⚠️ Please select an image first';
                return;
            }
            
            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            
            resultDiv.style.display = 'block';
            resultDiv.className = 'info';
            resultDiv.innerHTML = '⏳ Processing...';
            
            try {
                const response = await fetch('/api/verify', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.className = 'success';
                    resultDiv.innerHTML = `
                        <h3>✓ Verification Successful</h3>
                        <p><strong>Predicted Age:</strong> ${data.predicted_age} years</p>
                        <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}% (${data.confidence_level})</p>
                        <p><strong>Uncertainty:</strong> ±${data.uncertainty} years</p>
                        <p><strong>Category:</strong> ${data.age_category.toUpperCase()}</p>
                        ${data.edge_cases.length > 0 ? `<p><strong>Edge Cases:</strong> ${data.edge_cases.join(', ')}</p>` : ''}
                        <p><small>Processing time: ${data.processing_time}s</small></p>
                    `;
                } else {
                    resultDiv.className = 'error';
                    resultDiv.innerHTML = `
                        <h3>✗ Verification Failed</h3>
                        <p>${data.message}</p>
                    `;
                }
            } catch (error) {
                resultDiv.className = 'error';
                resultDiv.innerHTML = `<h3>✗ Error</h3><p>${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the demo web interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/verify', methods=['POST'])
def verify_age():
    """
    Age verification endpoint.
    
    Expects:
        - multipart/form-data with 'image' file
    
    Returns:
        JSON with verification results
    """
    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'error': 'no_image',
            'message': 'No image file provided'
        }), 400
    
    image_file = request.files['image']
    
    if image_file.filename == '':
        return jsonify({
            'success': False,
            'error': 'empty_filename',
            'message': 'No image file selected'
        }), 400
    
    try:
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        edge_cases = EdgeCaseDetector.analyze_image(image)
        
        result = estimator.estimate_age(image)
        
        image.close()
        del image
        del image_bytes
        
        if result['success']:
            return jsonify({
                'success': True,
                'predicted_age': result['predicted_age'],
                'confidence': result['confidence'],
                'confidence_level': result['confidence_level'],
                'uncertainty': result['uncertainty'],
                'age_category': 'child' if result['is_child'] else 'teen' if result['is_teen'] else 'adult',
                'is_adult': result['is_adult'],
                'is_teen': result['is_teen'],
                'is_child': result['is_child'],
                'edge_cases': [k.replace('_', ' ').title() for k, v in edge_cases.items() if v],
                'processing_time': result['processing_time'],
                'privacy': 'All biometric data deleted immediately',
                'system': f'{Config.PROJECT_NAME} by {Config.CREATOR}'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'unknown'),
                'message': result.get('message', 'Unknown error')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'processing_error',
            'message': str(e)
        }), 500

@app.route('/api/verify-threshold', methods=['POST'])
def verify_threshold():
    """
    Age threshold verification endpoint.
    
    Expects:
        - multipart/form-data with 'image' file
        - form field 'threshold' (integer, default: 13)
    
    Returns:
        JSON with threshold verification results
    """
    if 'image' not in request.files:
        return jsonify({
            'success': False,
            'error': 'no_image',
            'message': 'No image file provided'
        }), 400
    
    threshold = int(request.form.get('threshold', 13))
    image_file = request.files['image']
    
    try:
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        result = estimator.verify_age_threshold(image, threshold_age=threshold)
        
        image.close()
        del image
        del image_bytes
        
        if result['success']:
            return jsonify({
                'success': True,
                'predicted_age': result['predicted_age'],
                'threshold': result['threshold_age'],
                'passes_threshold': result['passes_threshold'],
                'confidence': result['confidence'],
                'confidence_level': result['confidence_level'],
                'privacy': 'All biometric data deleted immediately',
                'system': f'{Config.PROJECT_NAME} by {Config.CREATOR}'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'unknown'),
                'message': result.get('message', 'Unknown error')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'processing_error',
            'message': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'system': f'{Config.PROJECT_NAME} by {Config.CREATOR}',
        'version': Config.VERSION,
        'privacy_mode': Config.PRIVACY_MODE,
        'models_loaded': len(estimator.models)
    })

def main():
    print("\n" + "=" * 70)
    print(f"{Config.PROJECT_NAME} - Flask API Example")
    print(f"Created by {Config.CREATOR}")
    print("=" * 70 + "\n")
    
    print("Starting Flask development server...")
    print("\nAPI Endpoints:")
    print("  - Web UI:            http://localhost:5000/")
    print("  - POST /api/verify:  Age verification")
    print("  - POST /api/verify-threshold: Threshold verification")
    print("  - GET /api/health:   Health check")
    
    print("\nPrivacy:")
    print("  ✓ All biometric data deleted immediately")
    print("  ✓ No long-term storage")
    print("  ✓ Privacy mode enabled")
    
    print("\n" + "=" * 70)
    print("Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
