# E-commerce Category Mapper

An intelligent category mapping system that uses AI (Qwen 2.5 32B) and semantic embeddings to automatically map internal product categories to standardized marketplace categories.

## Overview

This tool helps e-commerce operations teams automatically map custom internal product categories to standardized marketplace category hierarchies (like Tesco, Amazon, etc.). It combines:

- **Qwen 2.5 32B LLM** (hosted on Google Colab) for intelligent category selection
- **Sentence Transformers** (MiniLM) for semantic similarity matching
- **Multi-stage fallback system** for high accuracy

## Features

- **Semantic Pre-filtering**: Uses embeddings to narrow down top 30 most relevant categories
- **AI-Powered Mapping**: Leverages Qwen 2.5 32B for context-aware category selection
- **Multi-Stage Fallback**:
  1. Exact normalized matching
  2. Trailing segment matching
  3. Embedding-based similarity (threshold: 0.85)
- **Async Processing**: Concurrent API calls with rate limiting
- **Auto-save**: Progress saved every 10 items
- **Detailed Logging**: Full audit trail of mapping decisions

## Prerequisites

- Python 3.8+
- Google Colab account (for hosting Qwen 2.5 32B)
- ngrok (for exposing Colab API)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/category-mapper.git
cd category-mapper

# Install dependencies
pip install -r requirements.txt
```

## Dependencies

```
pandas
openpyxl
aiohttp
ujson
sentence-transformers
scikit-learn
numpy
```

## Setup

### 1. Backend Setup (Google Colab)

See [COLAB_SETUP.md](COLAB_SETUP.md) for detailed instructions on setting up Qwen 2.5 32B on Google Colab with ngrok.

### 2. Excel Template Setup

Your Excel file should have two sheets:

**Sheet 1: "Categories"**
- Contains allowed marketplace categories in hierarchical format
- Each column represents a level (e.g., Col1: "Food", Col2: "Beverages", Col3: "Soft Drinks")

**Sheet 2: "Check"**
- Column 1: Your internal categories to be mapped

### 3. Configuration

Update the file path in the script:

```python
file_path = r"path/to/your/Category_mapping_template.xlsx"
API_URL = "https://your-ngrok-url.ngrok-free.dev/generate"
```

## Usage

```bash
python category_mapper.py
```

The script will:
1. Load allowed categories from Excel
2. Generate embeddings for semantic matching
3. Process each internal category through AI
4. Save results with quality flags
5. Output final mapped file

## Output

The script generates:
- **[Original]_Tesco.xlsx**: Final mapped categories
- **[Original]_Tesco_Mapped_autosave.xlsx**: Periodic backup
- **category_mapping_logs.txt**: Detailed processing log with top matches for each item

Output columns:
- Original internal category
- `Mapped Category`: Selected marketplace category
- `Check`: Flag for manual review (if similarity < threshold)

## How It Works

```
Internal Category
    ↓
Semantic Search (Top 30 matches)
    ↓
LLM Selection (Qwen 2.5 32B)
    ↓
Multi-Stage Validation
    ↓
Final Mapped Category
```

### Matching Strategy

1. **Exact Match**: Normalized string comparison
2. **Trailing Match**: Matches last 1-3 segments of hierarchy
3. **Semantic Fallback**: Embedding similarity ≥ 0.85

## Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `top_n` | 30 | Number of candidates for LLM |
| `semaphore` | 10 | Concurrent API requests |
| `similarity_threshold` | 0.85 | Minimum similarity for auto-accept |
| `autosave_interval` | 10 | Save progress every N items |

## Example

**Input**: "Organic Whole Milk 1L"

**Process**:
1. Semantic search finds: "Food & Drink > Dairy > Milk > Whole Milk", "Food & Drink > Dairy > Organic Products", etc.
2. LLM selects: "Food & Drink > Dairy > Milk > Whole Milk"
3. Validation confirms high confidence
4. Output: Mapped with no manual check needed

## Troubleshooting

**API Connection Issues**
- Verify ngrok URL is active
- Check Colab runtime hasn't expired
- Ensure firewall allows outbound connections

**Low Accuracy**
- Increase `top_n` to provide more context
- Adjust similarity threshold
- Review prompt engineering in `build_prompt()`

**Memory Issues**
- Reduce concurrent requests (lower semaphore value)
- Process in smaller batches

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file

## Author

**Yugesh**

- Specializes in automation, marketplace integration, and data analysis

## Acknowledgments

- Qwen 2.5 by Alibaba Cloud
- Sentence Transformers by UKPLab
- Community feedback and testing

## Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This tool is designed for e-commerce operations teams handling large-scale category mapping. Accuracy improves with well-structured allowed category hierarchies and quality LLM backend configuration.
