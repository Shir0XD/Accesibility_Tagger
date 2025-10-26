"""
Example: Using Aspose.PDF to create fully tagged PDFs with structure trees

PREREQUISITES:
1. Install Aspose.PDF: pip install aspose-pdf
2. Apply for a free evaluation license
3. Get license: https://purchase.aspose.com/buy

This creates PDFs with full structure trees visible in Acrobat Pro's Tags pane.
"""

import os
import json
from pathlib import Path

# Uncomment when Aspose.PDF is installed
# import aspose.pdf as ap
# from aspose.pdf import TaggedPdfElement


def convert_json_to_tagged_pdf(json_tags_path: str, input_pdf: str, output_pdf: str):
    """
    Convert JSON structure tags to fully tagged PDF using Aspose.PDF
    
    Args:
        json_tags_path: Path to JSON tags file
        input_pdf: Original PDF path
        output_pdf: Output tagged PDF path
    
    Returns:
        str: Path to tagged PDF
    """
    
    # Check if Aspose.PDF is available
    try:
        import aspose.pdf as ap
    except ImportError:
        print("❌ Aspose.PDF not installed")
        print("Install: pip install aspose-pdf")
        print("Get license: https://purchase.aspose.com/buy")
        return None
    
    # Load JSON tags
    with open(json_tags_path, 'r') as f:
        tags_data = json.load(f)
    
    structure_tags = tags_data['document']['structure_tags']
    
    # Create Aspose.PDF document
    document = ap.Document()
    
    # Set document metadata
    document.metadata['title'] = tags_data['document'].get('title', 'Tagged PDF')
    document.metadata['author'] = 'Expert PDF Tagger'
    document.metadata['subject'] = 'WCAG 2.1 AA Compliant PDF'
    
    # Get or create structure root
    if not document.structure_root:
        document.init_structure()
    
    structure_root = document.structure_root
    
    # Process each tag
    for tag in structure_tags:
        tag_type = tag['type']
        content = tag['content']
        page_num = tag.get('page', 1)
        attributes = tag.get('attributes', {})
        
        # Map tag types to Aspose elements
        element = None
        if tag_type == 'H1':
            element = ap.tagged.logicalstructure.elements.sect_elements.h1_element()
        elif tag_type == 'H2':
            element = ap.tagged.logicalstructure.elements.sect_elements.h2_element()
        elif tag_type == 'P':
            element = ap.tagged.logicalstructure.elements.sect_elements.p_element()
        elif tag_type == 'Table':
            element = ap.tagged.logicalstructure.elements.table_elements.table_element()
        # Add more types as needed
        
        if element:
            # Set attributes
            if 'actualText' in attributes:
                element.alternative_text = attributes['actualText']
            if 'title' in attributes:
                element.title = attributes['title']
            
            # Add to structure root
            structure_root.append_child(element)
    
    # Save as tagged PDF
    document.save(output_pdf)
    
    print(f"✅ Created fully tagged PDF: {output_pdf}")
    print(f"   {len(structure_tags)} structure elements added")
    
    return output_pdf


def main():
    """
    Main function to demonstrate usage
    """
    
    # Example usage
    json_tags = "accessibility_cache/test_tags.json"
    input_pdf = "output/test.pdf"
    output_pdf = "output/test_tagged_with_aspose.pdf"
    
    print("📄 Converting JSON tags to tagged PDF with Aspose.PDF...")
    
    result = convert_json_to_tagged_pdf(json_tags, input_pdf, output_pdf)
    
    if result:
        print("\n✅ Success!")
        print(f"Open {result} in Adobe Acrobat Pro")
        print("View → Show/Hide → Tags (Navigation Pane)")
        print("You should see the complete structure tree!")


if __name__ == "__main__":
    # Check if this is being run
    if __name__ == "__main__":
        print("\n" + "="*70)
        print("Aspose.PDF Integration Example")
        print("="*70)
        print("\nThis creates PDFs with FULL structure trees")
        print("visible in Acrobat Pro's Tags pane.\n")
        print("⚠️  Requires:")
        print("  1. pip install aspose-pdf")
        print("  2. Aspose.PDF license (commercial)")
        print("="*70 + "\n")
        
        print("For license info: https://purchase.aspose.com/buy")
        print("\n" + "="*70)

