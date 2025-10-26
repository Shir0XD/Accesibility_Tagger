"""Quick check of PDF structure"""
import pikepdf

pdf_path = "output/COE_advanced.pdf"

with pikepdf.open(pdf_path) as pdf:
    print("\n" + "="*70)
    print(f"Checking: {pdf_path}")
    print("="*70 + "\n")
    
    # Check MarkInfo
    if '/MarkInfo' in pdf.Root:
        marked = pdf.Root['/MarkInfo'].get('/Marked', False)
        print(f"✓ Marked: {marked}")
    else:
        print("⚠ Marked: False (not set)")
    
    # Check StructTreeRoot
    if '/StructTreeRoot' in pdf.Root:
        struct_tree = pdf.Root['/StructTreeRoot']
        print(f"✓ StructTreeRoot exists!")
        
        if '/K' in struct_tree:
            kids = struct_tree['/K']
            print(f"✓ Structure elements: {len(kids)} kids")
            
            # Show first few
            print("\nFirst 3 structure elements:")
            for i in range(min(3, len(kids))):
                try:
                    kid = kids[i]
                    if '/S' in kid:
                        struct_type = str(kid['/S'])
                        print(f"  {i+1}. Type: {struct_type}")
                    else:
                        print(f"  {i+1}. <no type>")
                except Exception as e:
                    print(f"  {i+1}. Error: {e}")
        else:
            print("⚠ No /K (kids) array")
    else:
        print("⚠ StructTreeRoot: Not found")
    
    print("\n" + "="*70)
    print("\nNow check in Acrobat Pro:")
    print("  1. Open the PDF")
    print("  2. View → Show/Hide → Tags (Navigation Pane)")
    print("  3. See if structure tree appears!")
    print("="*70 + "\n")

