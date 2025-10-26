"""
Test the tagged PDF output to see if titles are showing
"""

import pikepdf

pdf_path = "output/test_with_titles_tagged.pdf"

with pikepdf.open(pdf_path) as pdf:
    print("\n" + "="*70)
    print(f"Checking: {pdf_path}")
    print("="*70 + "\n")
    
    # Check structure tree
    if '/StructTreeRoot' in pdf.Root:
        struct_tree = pdf.Root['/StructTreeRoot']
        kids = struct_tree['/K']
        
        print(f"Structure elements: {len(kids)}")
        
        # Show first few with their titles
        print("\nFirst 5 structure elements with titles:")
        for i in range(min(5, len(kids))):
            try:
                kid = kids[i]
                tag_type = str(kid.get('/S', ''))
                
                # Get title
                title = kid.get('/T', 'No title')
                
                print(f"\n  {i+1}. Type: {tag_type}")
                print(f"     Title: {title}")
                
            except Exception as e:
                print(f"  {i+1}. Error: {e}")
        
        print("\n" + "="*70)
        print("Check in Acrobat Pro - tags should now have text!")
        print("="*70)

