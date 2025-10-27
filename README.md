# PDF Accessibility Tagger

Automated PDF accessibility tagging with LLM-powered structure detection and intelligent caching.

## Quick Start

```bash
# Tag any PDF
python auto_tag_pdf.py "path/to/input.pdf" "output_name"
```

**Output:** `output/output_name_tagged.pdf`

## Features

✅ **LLM-Powered Classification** - Uses Google Gemini to identify content types  
✅ **Complete Taxonomy** - 41 tag types across 9 categories  
✅ **Intelligent Cache** - Minimizes LLM calls for similar PDFs  
✅ **Structure Tree** - Creates proper PDF/UA structure hierarchy  
✅ **MCID Support** - Links structure elements to content  

## Installation

```bash
pip install -r requirements.txt
```

Create `.env` file:
```
GEMINI_API_KEY=your_key_here
```

## Usage

### Basic Tagging

```bash
python auto_tag_pdf.py "input.pdf" "my_document"
```

Creates:
- `output/my_document_tagged.pdf` - Tagged PDF
- `accessibility_cache/my_document_tags.json` - JSON tags

### Main Scripts

- **`auto_tag_pdf.py`** - Main entry point (USE THIS)
- **`expert_pdf_tagger.py`** - LLM-powered tag generation
- **`create_tagged_pdf_complete.py`** - Structure tree creation
- **`pdf_structure_taxonomy.py`** - Tag type definitions

## Tag Structure

The system creates proper PDF accessibility tags:

```
Document (Root)
  ├── P: "FIBER MONTHLY STATEMENT..."
  ├── Table: "Previous Dues / Payments..."
  ├── Table: "This Month's Summary..."
  └── ...
```

Each tag shows:
- **Type**: P, Table, H1, etc.
- **Title**: First 80 chars of content
- **MCID**: Links to structure

## Output

Open in Adobe Acrobat Pro → View → Tags to see structure tree.

Tags display with:
- Proper tag names (P, Table, H1, etc.)
- Content descriptions
- Hierarchical structure
- MCID references

## Requirements

- Python 3.8+
- Google Gemini API key
- PyMuPDF, pikepdf, pdfplumber, google-generativeai

## Support
For issues or questions, see USAGE_GUIDE.md
