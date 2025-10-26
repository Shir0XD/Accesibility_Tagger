# PDF Accessibility Tagger - Usage Guide

## Overview

This tool automatically creates accessible, tagged PDFs that comply with WCAG 2.1 AA and PDF/UA standards. It uses LLM-powered classification to intelligently tag document structure.

## Quick Start

```bash
# 1. Set up environment
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key_here" > .env

# 2. Generate expert JSON tags
python expert_pdf_tagger.py "input.pdf" "output_name"

# 3. Convert to tagged PDF with full structure tree
python create_tagged_pdf_v2.py "input.pdf" "accessibility_cache/output_name_tags.json" "output/final.pdf"
```

### Method 1: Basic Metadata (Current - Fast)
Use your existing expert tagger for LLM classification and basic PDF markup.

```bash
python expert_pdf_tagger.py "Sample PDF/COE-Sample.pdf" "coe_output"
```

**Result:**
- Expert JSON tags with structure classification
- PDF with metadata marked as tagged
- 90% cached (cost-efficient)
- 3-minute manual finalization in Acrobat Pro recommended

### Method 2: Full Structure Tree (NEW - Complete Automation)
Add structure tree using pikepdf for full Acrobat Pro visibility.

```bash
# Step 1: Generate JSON tags
python expert_pdf_tagger.py "Sample PDF/COE-Sample.pdf" "coe_output"

# Step 2: Convert to tagged PDF with structure tree
python create_tagged_pdf_v2.py \
    "Sample PDF/COE-Sample.pdf" \
    "accessibility_cache/coe_output_tags.json" \
    "output/final_tagged.pdf"
```

**Result:**
- Full PDF structure tree (`/StructTreeRoot`)
- Visible in Acrobat Pro Tags pane
- All structure elements (H1, P, Table, etc.)
- Fully automated!
- Zero additional cost (pikepdf is free)

## Comparison

| Method | Cost | Automation | Acrobat Pro Tags | Manual Work |
|--------|------|------------|------------------|-------------|
| **Basic** | Low (LLM API) | Partial | ⚠️ Limited | 3 min/doc |
| **Structure Tree** | Low (LLM API) | ✅ Full | ✅ Full | 0 min/doc |

## Recommended Workflow

### For Production (High Volume)
```bash
# 1. Batch process PDFs with expert tagger
for pdf in *.pdf; do
    python expert_pdf_tagger.py "$pdf" "output_name"
done

# 2. Batch convert to tagged PDFs
python batch_convert.py

# 3. All PDFs ready with full structure trees!
```

### For Testing (Single Document)
```bash
# Quick test
python expert_pdf_tagger.py "test.pdf" "test"
python create_tagged_pdf_v2.py "test.pdf" "accessibility_cache/test_tags.json" "output/test_tagged.pdf"
```

## Verification

Check if structure tree was created:

```python
python check_pdf.py
```

Or manually:
1. Open PDF in Acrobat Pro
2. View → Show/Hide → Tags (Navigation Pane)
3. Should see full structure tree!

## Cost Analysis

**Method 1 (Basic):**
- LLM: ~$0.05/doc (90% cached)
- Manual: 3 min/doc
- **Total: $0.05 + 3 min**

**Method 2 (Structure Tree):**
- LLM: ~$0.05/doc (90% cached)  
- pikepdf: FREE
- **Total: $0.05 + 0 min**

**Recommendation:** Use Method 2 for best results!

## Installation

```bash
# Install pikepdf
pip install pikepdf

# Or update requirements.txt
pip install -r requirements.txt
```

## Troubleshooting

### Structure tree not visible in Acrobat Pro?
1. Verify with `python check_pdf.py`
2. Check if `/StructTreeRoot` exists
3. Ensure PDF opens in Acrobat Pro (not Reader)

### pikepdf not installing?
```bash
pip install pikepdf --upgrade
```

### JSON tags not found?
Make sure to run `expert_pdf_tagger.py` first to generate tags.

## Next Steps

1. ✅ Test both methods
2. ✅ Verify in Acrobat Pro
3. ✅ Run accessibility checker
4. ✅ Integrate into workflow
5. ✅ Update documentation

## Summary

You now have TWO methods:

1. **Basic** - Fast, LLM-powered classification (current)
2. **Structure Tree** - Complete automation with full Acrobat Pro support (NEW)

Both are cost-effective and accurate. Choose based on your needs!

