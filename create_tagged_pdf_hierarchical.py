"""
Create Hierarchical Tagged PDF
Mimics the structure of well-tagged PDFs with proper Document -> Sections -> Elements
"""

import json
import logging
from pathlib import Path
import pikepdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_hierarchical_pdf(input_pdf: str, json_tags_file: str, output_pdf: str):
    """Create tagged PDF with proper hierarchical structure"""
    
    logger.info("="*70)
    logger.info("Creating Hierarchical Tagged PDF")
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
        
        # 3. Create hierarchical structure
        # Document -> Sections -> Elements -> Spans
        
        # Create root Document element
        doc_kids_array = pikepdf.Array([])
        doc_elem_data = {
            '/Type': pikepdf.Name.StructElem,
            '/S': pikepdf.Name('/Document'),
            '/T': 'Document',
            '/K': doc_kids_array
        }
        doc_elem = pdf.make_indirect(pikepdf.Dictionary(doc_elem_data))
        kids_array.append(doc_elem)
        logger.info("✓ Created Document root element")
        
        # Create section container
        section_kids_array = pikepdf.Array([])
        section_elem_data = {
            '/Type': pikepdf.Name.StructElem,
            '/S': pikepdf.Name('/Sect'),
            '/T': 'Main Content',
            '/K': section_kids_array
        }
        section_elem = pdf.make_indirect(pikepdf.Dictionary(section_elem_data))
        doc_kids_array.append(section_elem)
        logger.info("✓ Created Section element")
        
        # Create structure elements as children of section
        mcid_counter = 0
        struct_elements = []
        
        for tag in tags:
            struct_elem = create_element_with_nested_spans(pdf, tag, mcid_counter, struct_tree_root)
            struct_elements.append(struct_elem)
            section_kids_array.append(struct_elem)
            mcid_counter += 1
        
        logger.info(f"✓ Created {len(struct_elements)} structure elements")
        
        # 4. Inject MCIDs
        inject_mcids(pdf, tags, struct_elements, parent_tree_nums)
        
        logger.info(f"✓ Injected MCIDs")
        
        # 5. Save
        pdf.save(output_pdf)
        logger.info(f"✓ Saved: {output_pdf}")
        
    finally:
        pdf.close()


def create_element_with_nested_spans(pdf, tag: dict, mcid: int, parent_tree_root):
    """Create structure element with nested spans like well-tagged PDFs"""
    
    tag_type = tag['type']
    content = tag.get('content', '')
    attrs = tag.get('attributes', {})
    
    # Create main element
    elem_kids = pikepdf.Array([])
    elem_data = {
        '/Type': pikepdf.Name.StructElem,
        '/S': tag_type,
        '/P': None,  # Will be set
        '/K': elem_kids
    }
    
    # Add title (first 60 chars of content)
    if content:
        title = ' '.join(content.split())[:60]
        elem_data['/T'] = title
    
    # Create span as child
    if content and tag_type in ['P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6']:
        span_data = {
            '/Type': pikepdf.Name.StructElem,
            '/S': pikepdf.Name('/Span'),
            '/T': content[:60] if content else tag_type,
            '/K': pikepdf.Array([])
        }
        span_ref = pdf.make_indirect(pikepdf.Dictionary(span_data))
        elem_kids.append(span_ref)
    
    # Add attributes
    if attrs.get('lang'):
        elem_data['/Lang'] = attrs['lang']
    
    # Create element
    elem_ref = pdf.make_indirect(pikepdf.Dictionary(elem_data))
    elem_ref['/P'] = parent_tree_root
    
    return elem_ref


def inject_mcids(pdf, tags, struct_elements, parent_tree_nums):
    """Inject MCID mappings"""
    
    for i, (struct_elem, tag) in enumerate(zip(struct_elements, tags)):
        # Add to parent tree
        parent_tree_nums.append(i)  # MCID
        parent_tree_nums.append(struct_elem)  # Reference
        struct_elem['/K'].append(i)  # Add MCID to kids
    
    logger.info(f"✓ Created {len(parent_tree_nums) // 2} MCID mappings")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("\nUsage: python create_tagged_pdf_hierarchical.py <input> <json> <output>")
        print("\nExample:")
        print('  python create_tagged_pdf_hierarchical.py "input.pdf" "tags.json" "tagged.pdf"')
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    json_file = sys.argv[2]
    output = sys.argv[3]
    
    create_hierarchical_pdf(input_pdf, json_file, output)
    
    print("\nDone! Hierarchical PDF created.")
    print("Open in Acrobat Pro -> View -> Tags to verify!")

