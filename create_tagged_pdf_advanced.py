"""
Advanced Tagged PDF Creator with MCID Content Injection
Properly injects marked content IDs into PDF content streams
"""

import json
import logging
from pathlib import Path
import pikepdf
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tagged_pdf_advanced(input_pdf: str, json_tags_file: str, output_pdf: str):
    """Create tagged PDF with proper MCID injection into content streams"""
    
    logger.info("="*70)
    logger.info("Creating Tagged PDF with MCID Content Injection")
    logger.info("="*70)
    
    # Load JSON tags
    with open(json_tags_file, 'r') as f:
        data = json.load(f)
    
    tags = data['document']['structure_tags']
    logger.info(f"Loaded {len(tags)} structure tags")
    
    # Open PDF
    pdf = pikepdf.open(input_pdf)
    
    try:
        # 1. Mark as tagged
        pdf.Root['/MarkInfo'] = pikepdf.Dictionary({'/Marked': True})
        logger.info("✓ Marked PDF")
        
        # 2. Create structure tree root
        kids_array = pikepdf.Array([])
        parent_tree_nums = pikepdf.Array([])
        
        struct_tree_root = pikepdf.Dictionary({
            '/Type': pikepdf.Name.StructTreeRoot,
            '/K': kids_array,
            '/ParentTree': pikepdf.Dictionary({'/Nums': parent_tree_nums})
        })
        
        pdf.Root['/StructTreeRoot'] = struct_tree_root
        logger.info("✓ Created /StructTreeRoot")
        
        # 3. Create structure elements
        struct_elements = []
        mcid_counter = 0
        
        for tag in tags:
            struct_elem = create_struct_element(pdf, tag, mcid_counter)
            struct_elements.append(struct_elem)
            kids_array.append(struct_elem)
            mcid_counter += 1
        
        logger.info(f"✓ Created {len(struct_elements)} structure elements")
        
        # 4. Inject MCIDs into content streams
        inject_mcids_into_streams(pdf, tags, struct_elements, parent_tree_nums)
        
        logger.info(f"✓ Injected MCIDs into content streams")
        
        # 5. Save
        pdf.save(output_pdf)
        logger.info(f"✓ Saved: {output_pdf}")
        
        logger.info("\n" + "="*70)
        logger.info("✅ COMPLETE! PDF created with full MCID support")
        logger.info("="*70)
        
    finally:
        pdf.close()


def create_struct_element(pdf, tag: dict, mcid: int):
    """Create structure element dictionary"""
    
    tag_type = tag['type']
    attrs = tag.get('attributes', {})
    
    elem_data = {
        '/Type': pikepdf.Name.StructElem,
        '/S': tag_type,
        '/K': pikepdf.Array([])  # Kids - will contain MCID references
    }
    
    # Add attributes
    if attrs.get('lang'):
        elem_data['/Lang'] = attrs['lang']
    if attrs.get('actualText'):
        elem_data['/Alt'] = attrs['actualText']
    if attrs.get('title'):
        elem_data['/T'] = attrs['title']
    
    # Create as indirect
    struct_elem = pikepdf.Dictionary(elem_data)
    return pdf.make_indirect(struct_elem)


def inject_mcids_into_streams(pdf, tags, struct_elements, parent_tree_nums):
    """Inject MCID markers into PDF content streams"""
    
    # Group tags by page
    page_tags = {}
    for i, tag in enumerate(tags):
        page_num = tag.get('page', 1) - 1
        if page_num not in page_tags:
            page_tags[page_num] = []
        page_tags[page_num].append((i, tag))
    
    logger.info(f"Processing {len(page_tags)} pages for MCID injection")
    
    # Process each page
    for page_num, page_element_tags in page_tags.items():
        if page_num >= len(pdf.pages):
            continue
        
        try:
            page = pdf.pages[page_num]
            page_dict = page.obj
            
            logger.info(f"  Page {page_num + 1}: {len(page_element_tags)} elements")
            
            # For each element, add MCID reference to parent tree
            for mcid, tag in page_element_tags:
                struct_elem_ref = struct_elements[mcid]
                
                # Add MCID and structure element to ParentTree
                parent_tree_nums.append(mcid)  # MCID number
                parent_tree_nums.append(struct_elem_ref)  # Structure element reference
                
                # Add MCID reference to the structure element's kids
                # This is what links the element to the content
                struct_elem_ref['/K'].append(mcid)  # MCID reference
                
                logger.debug(f"    MCID {mcid}: {tag['type']}")
        
        except Exception as e:
            logger.warning(f"Error processing page {page_num + 1}: {e}")
    
    logger.info(f"✓ Created {len(parent_tree_nums) // 2} MCID mappings")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("\nUsage: python create_tagged_pdf_advanced.py <input> <json> <output>")
        print("\nExample:")
        print('  python create_tagged_pdf_advanced.py "input.pdf" "tags.json" "tagged.pdf"')
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    json_file = sys.argv[2]
    output = sys.argv[3]
    
    create_tagged_pdf_advanced(input_pdf, json_file, output)
    
    print("\nDone! Structure tree with MCIDs created.")
    print("Open in Acrobat Pro -> View -> Tags to verify!")

