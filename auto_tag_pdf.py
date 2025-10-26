"""
Automatic PDF Tagging Script
Input: Untagged PDF
Output: Tagged PDF with structure tree

This script combines expert classification with structure tree creation in one workflow.
"""

import os
import sys
import json
import logging
from pathlib import Path
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def tag_pdf(input_pdf: str, output_name: str):
    """
    Automatically tag a PDF with structure tree visible in Acrobat Pro.
    
    Args:
        input_pdf: Path to input (untagged) PDF
        output_name: Name for output files (without .pdf)
    
    Returns:
        str: Path to tagged PDF
    """
    
    logger.info("="*70)
    logger.info("PDF Accessibility Tagging - Complete Workflow")
    logger.info("="*70)
    
    # Step 1: Generate JSON tags
    logger.info("\n[Step 1/2] Generating expert JSON tags...")
    json_file = generate_json_tags(input_pdf, output_name)
    
    # Step 2: Create tagged PDF with structure tree
    logger.info("\n[Step 2/2] Creating tagged PDF with MCID structure tree...")
    tagged_pdf = create_tagged_pdf_from_json(input_pdf, json_file, output_name)
    
    logger.info("\n" + "="*70)
    logger.info("✅ COMPLETE! Tagged PDF created successfully")
    logger.info("="*70)
    logger.info(f"\nOutput file: {tagged_pdf}")
    logger.info("\nNext steps:")
    logger.info("  1. Open the PDF in Adobe Acrobat Pro")
    logger.info("  2. View → Show/Hide → Tags (Navigation Pane)")
    logger.info("  3. Verify structure tree is visible")
    logger.info("\nAll structure elements are now visible in Acrobat Pro!")
    
    return tagged_pdf


def generate_json_tags(input_pdf: str, output_name: str) -> str:
    """Generate JSON tags using expert tagger via subprocess"""
    
    # Run expert_tagger as subprocess
    logger.info(f"Running: python expert_pdf_tagger.py \"{input_pdf}\" \"{output_name}\"")
    
    result = subprocess.run(
        [sys.executable, "expert_pdf_tagger.py", input_pdf, output_name],
        capture_output=True,
        text=True,
        timeout=120  # 2 minute timeout
    )
    
    if result.returncode != 0:
        logger.error(f"Error running expert_tagger: {result.stderr}")
        raise RuntimeError(f"Failed to generate JSON tags: {result.stderr}")
    
    # Check for created files
    json_file = Path("accessibility_cache") / f"{output_name}_tags.json"
    
    if not json_file.exists():
        logger.error(f"JSON file not created: {json_file}")
        raise FileNotFoundError(f"JSON tags not created: {json_file}")
    
    logger.info(f"✓ Generated JSON tags: {json_file}")
    
    return str(json_file)


def create_tagged_pdf_from_json(input_pdf: str, json_file: str, output_name: str) -> str:
    """Create tagged PDF from JSON tags using advanced MCID version"""
    
    # Output path
    output_pdf = Path("output") / f"{output_name}_tagged.pdf"
    
    # Run hierarchical version for better structure
    logger.info(f"Running: python create_tagged_pdf_hierarchical.py \"{input_pdf}\" \"{json_file}\" \"{output_pdf}\"")
    
    result = subprocess.run(
        [sys.executable, "create_tagged_pdf_hierarchical.py", input_pdf, json_file, str(output_pdf)],
        capture_output=True,
        text=True,
        timeout=60  # 1 minute timeout
    )
    
    if result.returncode != 0:
        logger.error(f"Error creating tagged PDF: {result.stderr}")
        raise RuntimeError(f"Failed to create tagged PDF: {result.stderr}")
    
    logger.info(f"✓ Created tagged PDF with MCID: {output_pdf}")
    
    return str(output_pdf)


def main():
    """Main entry point"""
    
    if len(sys.argv) < 3:
        print("\n" + "="*70)
        print("Automatic PDF Accessibility Tagging")
        print("="*70)
        print("\nUsage:")
        print(f"  python {sys.argv[0]} <input.pdf> <output_name>")
        print("\nExample:")
        print(f'  python {sys.argv[0]} "Sample PDF/COE-Sample.pdf" "COE_tagged"')
        print("\nThis will create:")
        print("  - output/COE_tagged_tagged.pdf (tagged PDF)")
        print("  - accessibility_cache/COE_tagged_tags.json (JSON tags)")
        print("\n" + "="*70 + "\n")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_name = sys.argv[2]
    
    # Check if input file exists
    if not Path(input_pdf).exists():
        logger.error(f"❌ Input file not found: {input_pdf}")
        sys.exit(1)
    
    # Create tagged PDF
    tag_pdf(input_pdf, output_name)


if __name__ == "__main__":
    main()

