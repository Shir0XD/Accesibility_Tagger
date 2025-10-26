# How to Tag COE-Sample.pdf

## Method 1: Full Structure Tree (Recommended)

This creates a PDF with full structure tree visible in Acrobat Pro.

```bash
# Step 1: Generate expert JSON tags
python expert_pdf_tagger.py "Sample PDF/COE-Sample.pdf" "COE_tagged"

# Step 2: Convert to tagged PDF with full structure tree
python create_tagged_pdf_v2.py \
    "Sample PDF/COE-Sample.pdf" \
    "accessibility_cache/COE_tagged_tags.json" \
    "output/COE_tagged_final.pdf"
```

## Method 2: Basic Tagging

Just generates JSON tags and basic PDF metadata.

```bash
python expert_pdf_tagger.py "Sample PDF/COE-Sample.pdf" "COE_tagged"
```

## Verify Results

```bash
# Check structure tree
python check_pdf.py

# Then open in Acrobat Pro
# View → Show/Hide → Tags (Navigation Pane)
```

## Files Created

- `output/COE_tagged_final.pdf` - Tagged PDF with structure tree
- `accessibility_cache/COE_tagged_tags.json` - Complete structure tags
- `output/COE_tagged.pdf` - Basic tagged PDF

