# Google Colab Backend Setup Guide

This guide walks you through setting up Qwen 2.5 32B on Google Colab as the backend for category mapping.

## Overview

You'll be running Qwen 2.5 32B on Colab with:
- **vLLM** for fast inference
- **ngrok** for public API access
- **Flask** for REST API endpoint

## Prerequisites

- Google Colab account (free or Pro recommended)
- ngrok account (free tier works)
- ngrok authtoken

## Step-by-Step Setup

### 1. Get ngrok Authtoken

1. Sign up at [ngrok.com](https://ngrok.com)
2. Go to "Your Authtoken" page
3. Copy your authtoken

### 2. Create Colab Notebook

Create a new notebook at [colab.research.google.com](https://colab.research.google.com)

### 3. Install Dependencies

```python
# Cell 1: Install packages
!pip install vllm flask pyngrok torch transformers -q
```

### 4. Setup ngrok

```python
# Cell 2: Configure ngrok
from pyngrok import ngrok

# Set your ngrok authtoken
ngrok.set_auth_token("YOUR_NGROK_TOKEN_HERE")

# Start ngrok tunnel
public_url = ngrok.connect(5000)
print(f"Public API URL: {public_url}")
```

### 5. Load Qwen 2.5 32B Model

```python
# Cell 3: Initialize vLLM with Qwen 2.5 32B
from vllm import LLM, SamplingParams

print("Loading Qwen 2.5 32B model...")

# Initialize model
llm = LLM(
    model="Qwen/Qwen2.5-32B-Instruct",
    tensor_parallel_size=1,  # Use 1 GPU
    gpu_memory_utilization=0.95,
    max_model_len=4096,  # Adjust based on your needs
    dtype="half",  # Use float16 for efficiency
)

# Sampling parameters for generation
sampling_params = SamplingParams(
    temperature=0.1,  # Low temperature for consistent outputs
    top_p=0.9,
    max_tokens=150,  # Category names are short
    stop=["</s>", "\n\n"],  # Stop sequences
)

print("Model loaded successfully!")
```

### 6. Create Flask API

```python
# Cell 4: Setup Flask API
from flask import Flask, request, jsonify
import threading
import urllib.parse

app = Flask(__name__)

@app.route('/generate', methods=['GET'])
def generate():
    try:
        # Get prompt from URL parameter
        prompt = request.args.get('prompt', '')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Decode URL-encoded prompt
        decoded_prompt = urllib.parse.unquote(prompt)
        
        # Format for Qwen 2.5 instruction format
        formatted_prompt = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{decoded_prompt}<|im_end|>\n<|im_start|>assistant\n"
        
        # Generate response
        outputs = llm.generate([formatted_prompt], sampling_params)
        response_text = outputs[0].outputs[0].text.strip()
        
        return jsonify({"response": response_text})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "model": "Qwen2.5-32B-Instruct"})

# Run Flask in background thread
def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

print("Flask API is running!")
print(f"Access your API at: {public_url}")
```

### 7. Keep Session Alive

```python
# Cell 5: Keep alive (optional)
import time

print("API is running. Keep this cell running to maintain the session.")
print("Colab will disconnect after ~12 hours of inactivity")

try:
    while True:
        time.sleep(300)  # Ping every 5 minutes
        print("Session alive...")
except KeyboardInterrupt:
    print("Stopped by user")
```

## Complete Notebook Code

Here's the full notebook in one block:

```python
# Install
!pip install vllm flask pyngrok torch transformers -q

# Setup ngrok
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_TOKEN")
public_url = ngrok.connect(5000)
print(f"API URL: {public_url}")

# Load model
from vllm import LLM, SamplingParams
llm = LLM(
    model="Qwen/Qwen2.5-32B-Instruct",
    tensor_parallel_size=1,
    gpu_memory_utilization=0.95,
    max_model_len=4096,
    dtype="half"
)
sampling_params = SamplingParams(temperature=0.1, top_p=0.9, max_tokens=150)

# Create API
from flask import Flask, request, jsonify
import threading
import urllib.parse

app = Flask(__name__)

@app.route('/generate', methods=['GET'])
def generate():
    try:
        prompt = urllib.parse.unquote(request.args.get('prompt', ''))
        formatted = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        outputs = llm.generate([formatted], sampling_params)
        return jsonify({"response": outputs[0].outputs[0].text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000), daemon=True).start()
print("Ready!")
```

## Configuration Options

### For Faster Inference (Lower Accuracy)
```python
sampling_params = SamplingParams(
    temperature=0.0,  # Deterministic
    top_p=0.95,
    max_tokens=100,
)
```

### For Higher Quality (Slower)
```python
sampling_params = SamplingParams(
    temperature=0.3,
    top_p=0.9,
    max_tokens=200,
    repetition_penalty=1.1,
)
```

### For Larger Context
```python
llm = LLM(
    model="Qwen/Qwen2.5-32B-Instruct",
    max_model_len=8192,  # Double the context
    gpu_memory_utilization=0.90,  # Lower to fit larger context
)
```

## Troubleshooting

### Out of Memory Error
```python
# Reduce GPU memory usage
llm = LLM(
    model="Qwen/Qwen2.5-32B-Instruct",
    gpu_memory_utilization=0.85,  # Lower from 0.95
    max_model_len=2048,  # Reduce context window
)
```

### Model Loading Slow
- Use Colab Pro for better GPU (A100 vs T4)
- Model takes ~5-10 minutes to load first time
- Subsequent runs in same session are faster

### ngrok Tunnel Expired
- Free ngrok sessions last 2 hours
- Restart Cell 2 to create new tunnel
- Update API_URL in your Python script

### Colab Disconnected
- Free tier disconnects after 12 hours or 90 minutes idle
- Use Colab Pro for longer sessions
- Implement reconnection logic in your script

## 🔄 Alternative: Using Qwen 2.5 14B

If 32B is too slow or causes OOM:

```python
llm = LLM(
    model="Qwen/Qwen2.5-14B-Instruct",  # Smaller model
    gpu_memory_utilization=0.95,
    max_model_len=4096,
)
```

## 📊 Performance Expectations

| Model | GPU | Load Time | Inference Speed | Quality |
|-------|-----|-----------|-----------------|---------|
| Qwen 2.5 32B | T4 | ~10 min | ~2-3 tok/sec | Excellent |
| Qwen 2.5 32B | A100 | ~5 min | ~8-10 tok/sec | Excellent |
| Qwen 2.5 14B | T4 | ~5 min | ~5-6 tok/sec | Very Good |

## Testing Your API

Once deployed, test with:

```bash
curl "https://your-ngrok-url.ngrok-free.dev/health"
```

Expected response:
```json
{"status": "healthy", "model": "Qwen2.5-32B-Instruct"}
```

## Pro Tips

1. **Save your ngrok URL**: Copy it to your category mapper script
2. **Monitor GPU usage**: Check Colab's GPU RAM indicator
3. **Use Colab Pro**: Worth it for longer sessions and A100 GPUs
4. **Batch requests**: Process multiple categories to maximize uptime
5. **Log everything**: Keep track of API calls for debugging

## Notes

- Colab free tier GPU time: ~15 hours/week
- Colab Pro: Longer sessions, better GPUs ($10/month)
- ngrok free tier: 1 agent, 40 connections/min
- Model stays loaded until runtime disconnects

## Useful Links

- [vLLM Documentation](https://docs.vllm.ai/)
- [Qwen 2.5 Model Card](https://huggingface.co/Qwen/Qwen2.5-32B-Instruct)
- [ngrok Documentation](https://ngrok.com/docs)
- [Colab Pro](https://colab.research.google.com/signup)
