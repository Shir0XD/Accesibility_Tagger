"""
Create Tagged PDF with Structure Tree using pikepdf
Manual creation of /StructTreeRoot and structure elements
"""

import json
import logging
from pathlib import Path
import pikepdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tagged_pdf(input_pdf: str, json_tags_file: str, output_pdf: str):
    """Create tagged PDF from JSON structure tags"""
    
    logger.info(f"Creating tagged PDF...")
    
    # Load JSON tags
    with open(json_tags_file, 'r') as f:
        data = json.load(f)
    
    tags = data['document']['structure_tags']
    logger.info(f"Loaded {len(tags)} structure tags")
    
    # Open PDF
    pdf = pikepdf.open(input_pdf)
    
    try:
        # Mark as tagged
        pdf.Root.MarkInfo = pikepdf.Dictionary({'/Marked': True})
        logger.info("✓ Marked PDF")
        
        # Create structure tree root
        kids_array = pikepdf.Array([])
        parent_tree = pikepdf.Dictionary({'/Nums': pikepdf.Array([])})
        
        struct_tree_root = pikepdf.Dictionary({
            '/Type': pikepdf.Name.StructTreeRoot,
            '/K': kids_array,
            '/ParentTree': parent_tree
        })
        
        # Add to catalog - THIS IS THE KEY
        pdf.Root.StructTreeRoot = struct_tree_root
        logger.info("✓ Added StructTreeRoot to catalog")
        
        # Create structure elements
        for i, tag in enumerate(tags):
            create_element(pdf, kids_array, tag, i)
        
        logger.info(f"✓ Added {len(kids_array)} elements")
        logger.info(f"Kids in root: {len(struct_tree_root['/K'])}")
        
        # Force commit the changes to the catalog
        pdf.Root['/StructTreeRoot'] = struct_tree_root
        pdf.Root['/MarkInfo'] = pikepdf.Dictionary({'/Marked': True})
        
        logger.info("✓ Committed changes to catalog")
        
        # Save with all changes
        pdf.save(output_pdf, compress_streams=False, normalize_content=True)
        logger.info(f"✓ Saved: {output_pdf}")
        
    finally:
        pdf.close()


def create_element(pdf, kids_array, tag: dict, index: int):
    """Create a structure element and add to kids array"""
    
    tag_type = tag['type']
    attrs = tag.get('attributes', {})
    
    # Create element data
    elem_data = {
        '/Type': pikepdf.Name.StructElem,
        '/S': tag_type,  # Structure type (H1, P, Table, etc.)
        '/K': pikepdf.Array([])
    }
    
    # Add attributes
    if attrs.get('lang'):
        elem_data['/Lang'] = attrs['lang']
    if attrs.get('actualText'):
        elem_data['/Alt'] = attrs['actualText']
    if attrs.get('title'):
        elem_data['/T'] = attrs['title']
    
    # Create as indirect object and add to kids
    elem_dict = pikepdf.Dictionary(elem_data)
    elem_ref = pdf.make_indirect(elem_dict)
    kids_array.append(elem_ref)
    
    logger.debug(f"Created {tag_type} element for page {tag.get('page')}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python create_tagged_pdf_v2.py <input> <json> <output>")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    json_file = sys.argv[2]  
    output = sys.argv[3]
    
    create_tagged_pdf(input_pdf, json_file, output)
    
    print("\nDone! Check in Acrobat Pro -> Tags pane")

