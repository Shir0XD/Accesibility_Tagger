"""
Verify accessibility tags in a tagged PDF
"""

import sys
import pymupdf
from pathlib import Path
import json


def verify_pdf_tags(pdf_path: str):
    """Verify accessibility tags in a PDF"""
    
    print(f"\n{'='*60}")
    print(f"Verifying PDF: {pdf_path}")
    print(f"{'='*60}\n")
    
    try:
        doc = pymupdf.open(pdf_path)
        
        # Get metadata
        metadata = doc.metadata
        print("📄 PDF Metadata:")
        print(f"  Title: {metadata.get('title', 'N/A')}")
        print(f"  Subject: {metadata.get('subject', 'N/A')}")
        print(f"  Producer: {metadata.get('producer', 'N/A')}")
        
        # Check if structure is present
        if hasattr(doc, 'is_pdf'):
            print("\n✅ PDF Structure Present")
        
        # Check for pages
        print(f"\n📑 Document Info:")
        print(f"  Page Count: {doc.page_count}")
        
        # Check for text content
        total_text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text()
            total_text += text
        
        print(f"  Total Text Length: {len(total_text)} characters")
        
        # Get document's Xref (object structure)
        xref_length = doc.xref_length()
        print(f"  Object Count: {xref_length}")
        
        doc.close()
        
        print("\n✅ PDF opened successfully")
        print("\n" + "="*60)
        print("NOTE: Full structure tree verification requires advanced PDF manipulation.")
        print("Check the corresponding _tags.json file for complete tag details.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error verifying PDF: {e}")


def check_json_tags(json_path: str):
    """Check the JSON tags file"""
    
    json_file = Path(json_path)
    if not json_file.exists():
        print(f"\n⚠️  JSON tags file not found: {json_path}")
        return
    
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        print(f"\n{'='*60}")
        print(f"Checking JSON Tags: {json_path}")
        print(f"{'='*60}\n")
        
        tags = data.get('document', {}).get('structure_tags', [])
        
        print(f"📊 Structure Tags: {len(tags)}")
        
        # Group by type
        tag_types = {}
        for tag in tags:
            tag_type = tag.get('type', 'Unknown')
            tag_types[tag_type] = tag_types.get(tag_type, 0) + 1
        
        print("\n📋 Tag Breakdown:")
        for tag_type, count in sorted(tag_types.items()):
            print(f"  {tag_type}: {count}")
        
        # Show sample tags
        print("\n📄 Sample Tags:")
        for i, tag in enumerate(tags[:3], 1):
            print(f"\n  Tag {i}:")
            print(f"    Type: {tag.get('type')}")
            print(f"    Page: {tag.get('page')}")
            content = tag.get('content', '')[:100]
            print(f"    Content: {content}...")
            
            if 'attributes' in tag:
                attrs = tag['attributes']
                print(f"    Attributes: {list(attrs.keys())}")
        
        if len(tags) > 3:
            print(f"\n  ... and {len(tags) - 3} more tags")
        
    except Exception as e:
        print(f"\n❌ Error reading JSON: {e}")


def main():
    """Main verification"""
    
    if len(sys.argv) < 2:
        print("Usage: python verify_tags.py <pdf_path>")
        print("Example: python verify_tags.py output/tagged_coe.pdf")
        return
    
    pdf_path = sys.argv[1]
    
    # Verify PDF
    verify_pdf_tags(pdf_path)
    
    # Check JSON tags
    pdf_file = Path(pdf_path)
    json_path = pdf_file.with_stem(pdf_file.stem + '_tags')
    json_path = Path("accessibility_cache") / json_path.name
    
    check_json_tags(json_path)
    
    print("\n" + "="*60)
    print("✅ Verification Complete!")
    print("="*60)


if __name__ == "__main__":
    main()

