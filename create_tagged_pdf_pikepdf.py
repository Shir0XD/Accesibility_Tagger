"""
PDF Accessibility Structure Tree Creation with pikepdf
Creates proper tagged PDF with structure tree
"""

import pikepdf
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tagged_pdf_with_pikepdf(input_pdf: str, json_tags_file: str, output_pdf: str):
    """Create tagged PDF using pikepdf"""
    
    logger.info("="*70)
    logger.info("Creating Tagged PDF with pikepdf")
    logger.info("No element limit - all tags will be processed!")
    logger.info("="*70)
    
    # Load JSON tags
    with open(json_tags_file, 'r') as f:
        data = json.load(f)
    
    tags = data['document']['structure_tags']
    logger.info(f"Loaded {len(tags)} structure tags")
    
    # Open PDF
    pdf = pikepdf.open(input_pdf)
    
    try:
        logger.info("Creating structure tree...")
        
        # Get first page
        page = pdf.pages[0]
        
        # Build hierarchical structure
        structured_tags = build_hierarchy(tags)
        logger.info(f"Built hierarchy with {len(structured_tags)} root elements")
        
        # Create structure elements list
        structure_elements = []
        
        # Process each root-level tag
        for idx, tag_data in enumerate(structured_tags):
            logger.info(f"Processing root element {idx + 1}/{len(structured_tags)}: {tag_data.get('type', 'unknown')}")
            
            # Create structure element with proper PDF references
            struct_elem = create_structure_element(tag_data, pdf, page)
            
            if struct_elem:
                structure_elements.append(struct_elem)
                logger.info(f"✓ Added {tag_data.get('type', 'unknown')}")
        
        # Create structure tree root
        struct_tree_root = pikepdf.Dictionary({
            '/Type': pikepdf.Name('/StructTreeRoot'),
            '/K': pikepdf.Array(structure_elements),
            '/ParentTree': pikepdf.Dictionary({'/Nums': pikepdf.Array([])})
        })
        
        # Add to document catalog
        struct_tree_ref = pdf.make_indirect(struct_tree_root)
        pdf.Root['/StructTreeRoot'] = struct_tree_ref
        
        # Mark document as tagged
        pdf.Root['/MarkInfo'] = pikepdf.Dictionary({'/Marked': True})
        logger.info("✓ Structure tree added to PDF catalog")
        logger.info("✓ Document marked as tagged")
        
        logger.info(f"✓ Created {len(structure_elements)} structure elements")
        
        # Save
        logger.info(f"Saving to: {output_pdf}")
        pdf.save(output_pdf)
        logger.info("✓ Saved")
        
        logger.info("\n" + "="*70)
        logger.info("✅ COMPLETE!")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        pdf.close()


def build_hierarchy(tags):
    """Build hierarchical structure from flat tags - group list items under L tags"""
    
    structured = []
    i = 0
    
    while i < len(tags):
        tag = tags[i].copy()
        
        # If this is a list item
        if tag['type'] == 'LI':
            # Create a List container
            list_tag = {
                'type': 'L',
                'content': '',
                'page': tag['page'],
                'attributes': tag['attributes'].copy() if tag.get('attributes') else {},
                'children': []
            }
            
            # Collect consecutive list items
            while i < len(tags) and tags[i]['type'] == 'LI':
                list_tag['children'].append(tags[i])
                i += 1
            
            structured.append(list_tag)
        else:
            # Regular element (paragraph or heading)
            structured.append(tag)
            i += 1
    
    return structured


def create_structure_element(tag_data: Dict, pdf, page):
    """Create a structure element with proper PDF references"""
    
    try:
        tag_type_str = tag_data.get('type', 'P').replace('/', '').upper()
        content = tag_data.get('content', '')
        
        # Create dictionary for structure element
        elem_dict = {
            '/Type': pikepdf.Name('/StructElem'),
            '/S': pikepdf.Name(f'/{tag_type_str}'),
            '/K': pikepdf.Array([])
        }
        
        # Add attributes
        attrs = tag_data.get('attributes', {})
        if attrs and 'actualText' in attrs:
            elem_dict['/A'] = pikepdf.Dictionary({
                '/ActualText': attrs['actualText']
            })
        
        # Process children if any
        if 'children' in tag_data and tag_data['children']:
            kids_array = pikepdf.Array([])
            for child_data in tag_data['children']:
                if isinstance(child_data, dict):
                    child_elem = create_structure_element(child_data, pdf, page)
                    if child_elem:
                        kids_array.append(child_elem)
            elem_dict['/K'] = kids_array
        
        # Create PDF object
        elem_obj = pdf.make_indirect(pikepdf.Dictionary(elem_dict))
        return elem_obj
        
    except Exception as e:
        logger.error(f"Error creating element: {e}")
        return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python create_tagged_pdf_pikepdf.py <input> <json> <output>")
        sys.exit(1)
    
    create_tagged_pdf_with_pikepdf(sys.argv[1], sys.argv[2], sys.argv[3])
    print("\nDone!")
