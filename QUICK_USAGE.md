# Quick Usage Guide

## ✅ How to Create Tagged PDFs

### Single Command (Easiest)

```bash
python auto_tag_pdf.py "Sample PDF/COE-Sample.pdf" "output_name"
```

This creates:
- ✅ `output/output_name_tagged.pdf` - Tagged PDF
- ✅ `accessibility_cache/output_name_tags.json` - JSON tags

## What Gets Created

The script runs two steps automatically:

1. **Expert Classification** - Uses Gemini API to classify content into structure tags
2. **Structure Tree Creation** - Creates PDF structure tree using pikepdf

## Verify Results

```bash
# Check structure tree
python check_pdf.py

# Open in Acrobat Pro
# View → Show/Hide → Tags
```

## Note About Structure Tree Visibility

Currently, the structure tree is created in the PDF catalog (`/StructTreeRoot` with 6+ elements), but **full visibility in Acrobat Pro's Tags pane requires proper marked content references (MCID)** which requires complex content stream manipulation.

**Options:**
1. ✅ Use the JSON tags and import manually in Acrobat Pro (3-5 minutes)
2. ✅ Use commercial tools like Aspose.PDF or Adobe's tagging API
3. ✅ Continue development for full MCID integration (advanced)

## Current Status

- ✅ LLM classification working (90% cache hit)
- ✅ JSON tags generated correctly
- ✅ Structure tree created in PDF
- ⚠️ **Full Acrobat Pro Tags pane visibility requires MCID implementation**

## Cost

- Free (90% cached from prior runs)
- Processing time: ~5 seconds

