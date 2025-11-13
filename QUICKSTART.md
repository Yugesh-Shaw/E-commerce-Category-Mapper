# Quick Start Guide

Get up and running with Category Mapper in 15 minutes!

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] Google Colab account
- [ ] ngrok account (free tier works)
- [ ] Excel file with categories prepared

## 5-Minute Setup

### Step 1: Clone and Install (2 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/category-mapper.git
cd category-mapper

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Setup Colab Backend (5 minutes)

1. Open [Google Colab](https://colab.research.google.com)
2. Create new notebook
3. Copy this complete setup code:

```python
# Install packages
!pip install vllm flask pyngrok -q

# Setup ngrok (replace with your token)
from pyngrok import ngrok
ngrok.set_auth_token("YOUR_NGROK_TOKEN")
public_url = ngrok.connect(5000)
print(f"Your API URL: {public_url}")

# Load Qwen 2.5 32B
from vllm import LLM, SamplingParams
import urllib.parse
from flask import Flask, request, jsonify
import threading

llm = LLM(model="Qwen/Qwen2.5-32B-Instruct", gpu_memory_utilization=0.95)
sampling_params = SamplingParams(temperature=0.1, top_p=0.9, max_tokens=150)

# Create API
app = Flask(__name__)

@app.route('/generate', methods=['GET'])
def generate():
    prompt = urllib.parse.unquote(request.args.get('prompt', ''))
    formatted = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
    return jsonify({"response": llm.generate([formatted], sampling_params)[0].outputs[0].text.strip()})

threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000), daemon=True).start()
print("API Ready! Copy the URL above.")
```

4. Run all cells
5. Copy the ngrok URL (looks like: `https://xxxx-xxxx.ngrok-free.dev`)

### Step 3: Configure Script (3 minutes)

1. Open `category_mapper.py`
2. Update line 30 with your file path:
   ```python
   file_path = r"C:\path\to\your\Category_mapping_template.xlsx"
   ```
3. Update line 35 with your ngrok URL:
   ```python
   API_URL = "https://your-ngrok-url.ngrok-free.dev/generate"
   ```

### Step 4: Prepare Excel File (5 minutes)

Create an Excel file with two sheets:

**Sheet 1: "Categories"**
```
Level 1    | Level 2  | Level 3
Food       | Dairy    | Milk
Food       | Dairy    | Cheese
Electronics| Audio    | Headphones
```

**Sheet 2: "Check"**
```
Internal Category
Organic Whole Milk 1L
Wireless Headphones
```

See [EXCEL_TEMPLATE.md](EXCEL_TEMPLATE.md) for detailed format.

### Step 5: Run! (1 minute)

```bash
python category_mapper.py
```

Watch the magic happen!

## Understanding Output

Your Excel file will now have two new columns:

- **Mapped Category**: The AI-selected category
- **Check**: Flag for manual review (empty = high confidence)

Files created:
- `[Original]_Tesco.xlsx` - Final output
- `[Original]_Tesco_Mapped_autosave.xlsx` - Backup
- `category_mapping_logs.txt` - Detailed logs

## 🔧 Common First-Run Issues

### "API connection failed"
Check ngrok URL is correct and Colab is still running

### "Out of memory" on Colab
Use Qwen 2.5 14B instead (change model name in Colab code)

### "No module named 'sentence_transformers'"
Run `pip install -r requirements.txt` again

### Categories not matching well
Review your allowed categories hierarchy structure

## Pro Tips

1. **Start Small**: Test with 10-20 categories first
2. **Review Logs**: Check `category_mapping_logs.txt` to see why mappings were chosen
3. **Adjust Threshold**: Lower `SIMILARITY_THRESHOLD` (line 37) if too many false positives
4. **Use Colab Pro**: For faster processing with A100 GPU
5. **Batch Process**: Process in chunks if you have thousands of categories

## Next Steps

Once you're comfortable with the basics:

1. Read [COLAB_SETUP.md](COLAB_SETUP.md) for advanced Colab configuration
2. Read [EXCEL_TEMPLATE.md](EXCEL_TEMPLATE.md) for template optimization
3. Adjust parameters in script (lines 37-42) to tune for your use case
4. Consider using `config.py` for easier configuration management

## Example Run

```
$ python category_mapper.py

🚀 Starting category mapping process...
✅ Loaded 1,247 allowed categories.
✅ Loaded 500 internal categories.
🧠 Encoding allowed categories using embeddings...
✅ Row 1: Exact match → 'Food & Drink > Dairy > Milk > Whole Milk'
✅ Row 2: Semantic fallback → 'Electronics > Audio > Headphones > Wireless' (Similarity: 0.92)
💾 Autosaved at row 10
...
✅ Final output saved to: Category_mapping_template_Tesco.xlsx
🎉 Mapping complete!
📊 Summary: 475 auto-mapped, 20 need review, 5 errors
```

## Need Help?

- Check [Troubleshooting](#-common-first-run-issues) above
- Review detailed logs in `category_mapping_logs.txt`
- See [COLAB_SETUP.md](COLAB_SETUP.md) for backend issues
- Open an issue on GitHub

## ⏱️ Time Estimates

| Categories | Processing Time | API Calls |
|-----------|----------------|-----------|
| 100 | ~5 minutes | 100 |
| 500 | ~25 minutes | 500 |
| 1,000 | ~50 minutes | 1,000 |
| 5,000 | ~4 hours | 5,000 |

*Times based on Qwen 2.5 32B on Colab T4 GPU*

Happy mapping!
