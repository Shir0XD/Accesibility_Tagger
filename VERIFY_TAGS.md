# How to Verify Accessibility Tags

## Method 1: Using the Verification Script (Easiest)

```bash
python verify_tags.py output/tagged_pdf.pdf
```

This will show:
- PDF metadata
- Total tags count
- Tag breakdown by type
- Sample tags with attributes

## Method 2: Check JSON Tags File

The system creates a JSON file with all tags:

```bash
# View the tags JSON file
Get-Content "accessibility_cache/tagged_pdf_tags.json"
```

Example output:
```json
{
  "document": {
    "structure_tags": [
      {
        "type": "H1",
        "content": "...",
        "attributes": {
          "lang": "en",
          "actualText": "..."
        },
        "page": 1
      }
    ]
  }
}
```

## Method 3: Adobe Acrobat Pro (Most Comprehensive)

1. Open PDF in Adobe Acrobat Pro
2. Go to **Tools** → **Accessibility**
3. Run **Full Check**
4. View the accessibility report

**Checks:**
- ✅ Tagged document structure
- ✅ Heading hierarchy
- ✅ Alt text for images
- ✅ Table structure
- ✅ Reading order

## Method 4: PAC (PDF Accessibility Checker)

Download from: https://www.pdfa.org/resource/pdf-accessibility-checker-pac/

```bash
# Run PAC to check tags
pac-cli.exe output/tagged_pdf.pdf
```

## Method 5: PDF Accessibility Check in Browser

Use online checker: https://www.accessibilitychecker.org/

1. Upload your PDF
2. Get detailed accessibility report
3. See all tags and structure

## Method 6: Python Script (Advanced)

```python
import pymupdf

doc = pymupdf.open("output/tagged_pdf.pdf")

# Check metadata
print(doc.metadata)

# Check structure (if available)
# Note: Full structure tree requires advanced PDF manipulation
```

## What Tags Should Be Present?

Your PDF should have:

1. **Headings** (H1-H6)
   - Proper hierarchy
   - Descriptive titles

2. **Paragraphs** (P)
   - Complete text content
   - Language attributes

3. **Tables** (Table, TR, TH, TD)
   - Header cells properly tagged
   - Row structure
   - Summary attributes

4. **Figures** (Figure)
   - Alt text placeholders
   - Captions

5. **Metadata**
   - Language specification
   - Title and subject
   - Producer information

## Quick Verification Checklist

- ✅ Tagged PDF created (`output/`)
- ✅ JSON tags file created (`accessibility_cache/`)
- ✅ PDF opens without errors
- ✅ Metadata shows "Accessibility Tagged PDF"
- ✅ Tags JSON has structure tags array

## Note

The expert tagger creates:
- **Metadata-tagged PDF** - Has document-level accessibility info
- **JSON tags file** - Complete tag hierarchy with all details

For full PDF structure tree embedding, you'd need advanced PDF manipulation libraries beyond the scope of this basic implementation.

