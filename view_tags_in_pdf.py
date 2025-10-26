"""
View structure tags embedded in a tagged PDF
"""

import sys
import pymupdf


def view_tags_in_pdf(pdf_path: str):
    """View all structure tags in a PDF"""
    
    print(f"\n{'='*70}")
    print(f"Viewing Structure Tags in: {pdf_path}")
    print(f"{'='*70}\n")
    
    try:
        doc = pymupdf.open(pdf_path)
        
        # Check metadata
        metadata = doc.metadata
        print("📄 PDF Metadata:")
        print(f"  Title: {metadata.get('title', 'N/A')}")
        print(f"  Subject: {metadata.get('subject', 'N/A')}")
        print(f"  Producer: {metadata.get('producer', 'N/A')}")
        
        # Check all pages for annotations
        total_annotations = 0
        all_tags = []
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            annots = page.annots()
            
            for annot in annots:
                # Check if this is a structure tag annotation
                annot_info = annot.info
                title = annot_info.get('title', '')
                
                if 'Tag' in title:
                    total_annotations += 1
                    content = annot_info.get('content', '')
                    
                    # Extract tag type
                    if 'Type:' in content:
                        tag_info = content.split('Type:')[1].split('\n')[0].strip()
                    else:
                        tag_info = title
                    
                    all_tags.append({
                        'page': page_num + 1,
                        'type': tag_info,
                        'title': title
                    })
        
        print(f"\n📋 Structure Tags Found: {total_annotations}")
        
        if all_tags:
            print("\n📊 Tag Breakdown by Page:")
            for i, tag in enumerate(all_tags, 1):
                print(f"  {i}. Page {tag['page']}: {tag['type']}")
                print(f"     Title: {tag['title']}")
        
        # Check for text annotations
        print(f"\n🔍 Checking for embedded structure data...")
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            annots = list(page.annots())
            
            if annots:
                print(f"  Page {page_num + 1}: {len(annots)} annotations")
                for annot in annots:
                    annot_type = annot.type[1] if annot.type else "Unknown"
                    print(f"    - {annot_type}: {annot.info.get('title', 'N/A')}")
        
        doc.close()
        
        print(f"\n{'='*70}")
        print("✅ Tag verification complete!")
        print("="*70)
        print("\n💡 Note: Full structure tree embedding requires advanced PDF manipulation.")
        print("   The JSON tags file contains the complete tag structure.")
        print(f"   Check: accessibility_cache/{Path(pdf_path).stem}_tags.json")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python view_tags_in_pdf.py <pdf_path>")
        print("Example: python view_tags_in_pdf.py output/tagged_coe.pdf")
        sys.exit(1)
    
    from pathlib import Path
    view_tags_in_pdf(sys.argv[1])

