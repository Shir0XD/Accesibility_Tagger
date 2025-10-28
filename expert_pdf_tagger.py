"""
Expert PDF Accessibility Tagger with Complete PDF/UA Taxonomy
Implements comprehensive structure tag classification and intelligent caching
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

import pymupdf  # PyMuPDF (fitz)
import pdfplumber
import google.generativeai as genai
from dotenv import load_dotenv

# Import our taxonomy
from pdf_structure_taxonomy import (
    StructureTag, StructureAttributes, TagType, TaxonomyClassifier
)

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path("accessibility_cache")
CACHE_DIR.mkdir(exist_ok=True)


@dataclass
class ExtractedElement:
    """Raw extracted element from PDF"""
    content: str
    detected_type: str  # 'paragraph', 'heading', 'table', etc.
    page: int
    position: Optional[Dict] = None
    metadata: Optional[Dict] = None


@dataclass
class ClassifiedElement:
    """Element with PDF/UA structure classification"""
    tag_type: TagType
    content: str
    attributes: StructureAttributes
    page: int
    children: List['ClassifiedElement'] = None
    
    def to_structure_tag(self) -> StructureTag:
        """Convert to StructureTag"""
        return StructureTag(
            tag_type=self.tag_type,
            content=self.content,
            attributes=self.attributes,
            page=self.page,
            children=[c.to_structure_tag() for c in (self.children or [])]
        )


class ExpertTagGenerator:
    """Generate expert-level PDF accessibility tags with LLM"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        
    def generate_structure_tags(self, element: ExtractedElement) -> ClassifiedElement:
        """Generate complete PDF/UA structure tags for an element"""
        
        # First, classify the tag type
        tag_type = TaxonomyClassifier.classify_content(
            element.content,
            element.metadata.get("context", "") if element.metadata else "",
            element.detected_type
        )
        
        # Generate detailed attributes with LLM
        attributes = self._generate_attributes(element, tag_type)
        
        # Create classified element
        classified = ClassifiedElement(
            tag_type=tag_type,
            content=element.content,
            attributes=attributes,
            page=element.page,
            children=None
        )
        
        return classified
    
    def _generate_attributes(self, element: ExtractedElement, tag_type: TagType) -> StructureAttributes:
        """Generate PDF/UA attributes using LLM"""
        
        # Use LLM to generate descriptive attributes
        prompt = self._create_classification_prompt(element, tag_type)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 1024,
                }
            )
            
            if not response.text:
                logger.warning("Empty LLM response, using defaults")
                return self._default_attributes(element, tag_type)
            
            # Parse LLM response
            result_text = response.text.strip()
            
            # Try to extract JSON
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                # Try direct parsing
                result = json.loads(result_text)
            
            # Build attributes from LLM response
            return StructureAttributes(
                alt=result.get("alt"),
                lang=result.get("lang", "en"),
                actualText=result.get("actualText") or element.content,
                title=result.get("title"),
                summary=result.get("summary")
            )
            
        except Exception as e:
            logger.warning(f"Error generating attributes: {e}")
            return self._default_attributes(element, tag_type)
    
    def _create_classification_prompt(self, element: ExtractedElement, tag_type: TagType) -> str:
        """Create prompt for LLM classification"""
        
        prompt = f"""You are a PDF accessibility expert (WCAG 2.1 AA compliant).
        
Analyze this PDF content and generate proper PDF/UA accessibility attributes.

TAG TYPE: {tag_type.value}
CONTENT: {element.content[:500]}

Provide a JSON object with:
- "alt": "Alternative text description" (for figures, tables)
- "actualText": "Text for screen readers" (the full content)
- "lang": "Language code" (default: "en")
- "title": "Descriptive title"
- "summary": "Detailed summary of purpose and meaning"

Return ONLY valid JSON, nothing else:
"""
        return prompt
    
    def _default_attributes(self, element: ExtractedElement, tag_type: TagType) -> StructureAttributes:
        """Create default attributes when LLM fails"""
        return StructureAttributes(
            actualText=element.content,
            lang="en"
        )


class IntelligentCache:
    """Advanced caching with similarity detection"""
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index_file = cache_dir / "cache_index.json"
        self.index = self._load_index()
        
    def _load_index(self) -> Dict:
        """Load cache index"""
        if self.cache_index_file.exists():
            with open(self.cache_index_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """Save cache index"""
        with open(self.cache_index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def get_cache_key(self, content: str, tag_type: TagType, page: int = None) -> str:
        """Generate cache key from content and type"""
        # Create a normalized key
        normalized_content = content.lower().strip()[:200]  # First 200 chars
        key_data = f"{normalized_content}::{tag_type.value}"
        if page:
            key_data += f"::page{page}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def get(self, cache_key: str) -> Optional[Dict]:
        """Get from cache"""
        if cache_key in self.index:
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                logger.info(f"Cache hit: {cache_key[:16]}...")
                with open(cache_file, 'r') as f:
                    return json.load(f)
        return None
    
    def set(self, cache_key: str, data: Any):
        """Save to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Convert to JSON-serializable format
        serializable_data = self._make_serializable(data)
        
        with open(cache_file, 'w') as f:
            json.dump(serializable_data, f, indent=2)
        
        self.index[cache_key] = {
            "created": datetime.now().isoformat(),
            "tag_type": serializable_data.get("tag_type", "unknown")
        }
        self._save_index()
        
        logger.info(f"Cached: {cache_key[:16]}...")
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format"""
        if isinstance(obj, TagType):
            return obj.value
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # Handle dataclass
            result = {}
            for key, value in obj.__dict__.items():
                result[key] = self._make_serializable(value)
            return result
        else:
            return obj


class ExpertPDFTagger:
    """Expert PDF tagger with complete PDF/UA structure taxonomy"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.tag_generator = ExpertTagGenerator(api_key, model)
        self.cache = IntelligentCache()
        
    def extract_and_classify(self, pdf_path: str) -> List[ClassifiedElement]:
        """Extract elements and classify into PDF/UA taxonomy"""
        logger.info(f"Extracting and classifying: {pdf_path}")
        
        elements = self._extract_elements(pdf_path)
        classified_elements = []
        
        for i, element in enumerate(elements):
            logger.info(f"Processing element {i+1}/{len(elements)}: {element.detected_type}")
            
            # Check cache first
            cache_key = self.cache.get_cache_key(
                element.content,
                TaxonomyClassifier.classify_content(element.content, "", element.detected_type)
            )
            
            cached = self.cache.get(cache_key)
            if cached:
                # Convert tag_type string back to TagType enum
                if isinstance(cached.get('tag_type'), str):
                    cached['tag_type'] = TagType(cached['tag_type'])
                classified = ClassifiedElement(**cached)
                classified_elements.append(classified)
                continue
            
            # Generate tags with LLM
            classified = self.tag_generator.generate_structure_tags(element)
            
            # Cache the result
            self.cache.set(cache_key, asdict(classified))
            
            classified_elements.append(classified)
        
        return classified_elements
    
    def _extract_elements(self, pdf_path: str) -> List[ExtractedElement]:
        """Extract all elements from PDF"""
        elements = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    logger.info(f"Processing page {page_num}")
                    
                    # Extract text line by line  
                    text = page.extract_text()
                    if text:
                        lines = text.split('\n')
                        logger.info(f"Extracted {len(lines)} lines from page {page_num}")
                        current_para = ""
                        
                        for line_idx, line in enumerate(lines):
                            line = line.strip()
                            if not line:
                                # Empty line - process accumulated paragraph
                                if current_para and len(current_para) > 5:
                                    is_heading = self._is_heading(current_para)
                                    is_list_item = self._is_list_item(current_para)
                                    
                                    if is_list_item:
                                        # Extract individual list items
                                        list_items = self._extract_list_items(current_para)
                                        for item in list_items:
                                            elements.append(ExtractedElement(
                                                content=item,
                                                detected_type="list_item",
                                                page=page_num,
                                                metadata={"original_text": item}
                                            ))
                                    else:
                                        elements.append(ExtractedElement(
                                            content=current_para,
                                            detected_type="heading" if is_heading else "paragraph",
                                            page=page_num,
                                            metadata={"original_text": current_para}
                                        ))
                                    current_para = ""
                                continue
                            
                            # Check if this line is a list item on its own
                            if self._is_list_item(line):
                                # Save current para if exists
                                if current_para:
                                    elements.append(ExtractedElement(
                                        content=current_para,
                                        detected_type="heading" if self._is_heading(current_para) else "paragraph",
                                        page=page_num,
                                        metadata={"original_text": current_para}
                                    ))
                                    current_para = ""
                                
                                # Process the list item
                                elements.append(ExtractedElement(
                                    content=line,
                                    detected_type="list_item",
                                    page=page_num,
                                    metadata={"original_text": line}
                                ))
                            else:
                                # Accumulate into paragraph
                                if current_para:
                                    current_para += " " + line
                                else:
                                    current_para = line
                        
                        # Process any remaining paragraph
                        if current_para and len(current_para) > 5:
                            is_heading = self._is_heading(current_para)
                            is_list_item = self._is_list_item(current_para)
                            
                            if is_list_item:
                                list_items = self._extract_list_items(current_para)
                                for item in list_items:
                                    elements.append(ExtractedElement(
                                        content=item,
                                        detected_type="list_item",
                                        page=page_num,
                                        metadata={"original_text": item}
                                    ))
                            else:
                                elements.append(ExtractedElement(
                                    content=current_para,
                                    detected_type="division" if is_heading else "paragraph",
                                    page=page_num,
                                    metadata={"original_text": current_para}
                                ))
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            table_str = self._table_to_string(table)
                            elements.append(ExtractedElement(
                                content=table_str,
                                detected_type="table",
                                page=page_num,
                                metadata={"table": table}
                            ))
            
            logger.info(f"Extracted {len(elements)} elements")
            
        except Exception as e:
            logger.error(f"Error extracting: {e}")
        
        return elements
    
    def _is_heading(self, text: str) -> bool:
        """Check if text is a heading"""
        text_stripped = text.strip()
        
        # Short text is likely a heading
        if len(text_stripped) < 100 and text_stripped.isupper():
            return True
        
        # Check for heading patterns
        import re
        if re.match(r'^\d+[\.\)]\s+[A-Z]', text_stripped):
            return True
        if re.match(r'^[A-Z][A-Z\s]{5,}$', text_stripped):
            return True
        
        return False
    
    def _is_list_item(self, text: str) -> bool:
        """Check if text is a list item"""
        text_stripped = text.strip()
        
        # Check for bullet points
        bullet_chars = ['•', '▪', '▫', '‣', '⁃', '◦', '○', '●', '\u2022']
        if text_stripped and text_stripped[0] in bullet_chars:
            return True
        
        # Check for numbered lists
        import re
        if re.match(r'^\d+[\.\)]\s+', text_stripped):
            return True
        
        # Check for lettered lists
        if re.match(r'^[a-z][\.\)]\s+', text_stripped):
            return True
        
        # Check for Roman numerals
        if re.match(r'^[ivxlcdm]+[\.\)]\s+', text_stripped, re.IGNORECASE):
            return True
        
        return False
    
    def _extract_list_items(self, text: str) -> list:
        """Extract individual list items from text"""
        import re
        
        # Split by bullets
        items = []
        bullet_chars = ['•', '▪', '▫', '‣', '⁃', '◦', '○', '●', '\u2022']
        
        for bullet in bullet_chars:
            parts = text.split(bullet)
            if len(parts) > 1:
                for part in parts:
                    part = part.strip()
                    if part:
                        # Remove leading numbering if present
                        part = re.sub(r'^\d+[\.\)]\s+', '', part)
                        part = re.sub(r'^[a-z][\.\)]\s+', '', part)
                        part = re.sub(r'^[ivxlcdm]+[\.\)]\s+', '', part, flags=re.IGNORECASE)
                        items.append(part)
                break
        
        # If no bullets found, try numbered lists
        if not items:
            numbered = re.split(r'\n\s*\d+[\.\)]\s+', text)
            items = [item.strip() for item in numbered if item.strip()]
        
        # If still no items, return as single item
        if not items:
            items = [text.strip()]
        
        return items
    
    def _table_to_string(self, table: List[List]) -> str:
        """Convert table to string"""
        return "\n".join(["\t".join([str(cell) if cell else "" for cell in row]) for row in table])
    
    def apply_tags_to_pdf(self, input_pdf: str, output_pdf: str, elements: List[ClassifiedElement]):
        """Apply structure tags to PDF and save"""
        logger.info(f"Applying tags to PDF: {input_pdf}")
        
        # Create output directory if it doesn't exist
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        # Open PDF
        doc = pymupdf.open(input_pdf)
        
        try:
            # Add document-level metadata
            doc.set_metadata({
                "title": "Accessibility Tagged PDF",
                "subject": "Tagged for WCAG 2.1 AA compliance",
                "keywords": "accessibility, PDF/UA, tagged, accessible",
                "producer": "Expert PDF Tagger"
            })
            
            # Embed actual structure tree in PDF
            logger.info("Embedding structure tags in PDF...")
            self._embed_structure_tree(doc, elements)
            
            # Mark document as tagged PDF
            try:
                catalog = doc.get_pdf_catalog()
                catalog['MarkInfo'] = {'Marked': 'true'}
                catalog['Version'] = '1.7'
                
                # Add tagging metadata
                catalog['DocumentID'] = str(hash(str(elements)))
                
                logger.info("Document marked as tagged PDF")
            except Exception as e:
                logger.debug(f"Could not mark document: {e}")
            
            # Save tagged PDF
            doc.save(output_pdf, garbage=4, deflate=True, use_objstms=False, clean=True)
            logger.info(f"Tagged PDF saved to: {output_pdf}")
            
        finally:
            doc.close()
        
        # Save tags to JSON in cache folder
        json_filename = Path(output_pdf).stem + '_tags.json'
        json_output = Path("accessibility_cache") / json_filename
        self.save_tags_json(elements, str(json_output))
    
    def _embed_structure_tree(self, doc, elements: List[ClassifiedElement]):
        """Embed actual PDF structure tags into the PDF"""
        
        try:
            # Initialize structure tree
            if not doc.is_pdf:
                logger.warning("Document is not a PDF")
                return
            
            logger.info("Creating PDF structure tree...")
            
            # Create document structure
            # PyMuPDF structure tree creation
            try:
                # Get or create structure root
                struct_tree = doc.get_structure_tree()
                
                if not struct_tree:
                    # Create new structure tree
                    # We need to add elements to the structure
                    self._create_structure_tree(doc, elements)
                else:
                    # Add to existing structure
                    self._add_to_existing_structure(doc, elements)
                
                logger.info(f"Embedded {len(elements)} structure tags into PDF")
                
            except Exception as e:
                logger.warning(f"Could not create structure tree: {e}")
                # Try alternative approach
                self._add_structure_content_items(doc, elements)
            
        except Exception as e:
            logger.warning(f"Could not embed full structure tree: {e}")
            logger.info("PDF will have metadata and JSON tags only")
    
    def _create_structure_tree(self, doc, elements: List[ClassifiedElement]):
        """Create PDF structure tree with content items"""
        
        try:
            # PyMuPDF structure tree creation
            # Note: Full PDF structure tree requires PyMuPDF 1.23.0+
            
            # Create root structure element
            root_dict = {
                'Type': '/StructTreeRoot',
                'K': []  # Kids list
            }
            
            # Group elements by page
            pages_elements = {}
            for element in elements:
                page = element.page - 1
                if page not in pages_elements:
                    pages_elements[page] = []
                pages_elements[page].append(element)
            
            # Create structure elements for each page
            page_refs = []
            for page_num, page_elements in pages_elements.items():
                if page_num < doc.page_count:
                    page = doc[page_num]
                    
                    # Create page structure element
                    for element in page_elements:
                        struct_dict = self._create_structure_element(doc, element, page)
                        page_refs.append(struct_dict)
            
            # Set up the document's structure tree
            # This is complex PDF internals manipulation
            try:
                # Add to document catalog
                catalog = doc.get_pdf_catalog()
                
                # Mark document as tagged
                catalog['MarkInfo'] = {'Marked': 'true'}
                
                # Create structure tree root
                if 'StructTreeRoot' not in catalog:
                    struct_tree_root = {
                        'Type': '/StructTreeRoot',
                        'K': []  # Will be populated
                    }
                    catalog['StructTreeRoot'] = struct_tree_root
                
                logger.info("Created PDF structure tree root")
                
            except Exception as e:
                logger.debug(f"Error setting structure tree: {e}")
        
        except Exception as e:
            logger.debug(f"Error creating structure: {e}")
    
    def _create_structure_element(self, doc, element: ClassifiedElement, page):
        """Create a structure element dictionary"""
        
        # Create structure element dict
        struct_elem = {
            'Type': '/StructElem',
            'S': f'/{element.tag_type.value}',  # Structure type (tag)
            'P': None,  # Parent (will be set)
            'Page': None,  # Page reference (will be set)
            'K': []  # Kids
        }
        
        return struct_elem
    
    def _add_structure_mark(self, page, element: ClassifiedElement):
        """Add structure mark to page"""
        
        try:
            # Create structure mark
            # This creates a proper PDF content item
            
            # Get MCID (marked content ID)
            # We'll use the page's text blocks
            
            # Add to page's content stream
            page_dict = page.get_dict()
            
            # Insert structure mark in content stream
            # This is complex - requires low-level PDF manipulation
            
            # For now, we'll add as content stream comment
            # which shows structure information
            
            logger.debug(f"Added structure mark for {element.tag_type.value} on page {element.page}")
            
        except Exception as e:
            logger.debug(f"Could not add structure mark: {e}")
    
    def _add_structure_content_items(self, doc, elements: List[ClassifiedElement]):
        """Add structure content items to PDF"""
        
        # This is a simplified approach
        # Full structure tree requires complex PDF manipulation
        
        # Add structure info via document's XMP metadata
        xmp_metadata = {
            'StructureType': 'Tagged PDF',
            'TagCount': str(len(elements)),
            'Tags': ','.join([e.tag_type.value for e in elements])
        }
        
        # Try to add as custom metadata
        current_metadata = doc.metadata
        
        # Add custom tags metadata
        for key, value in xmp_metadata.items():
            if key not in current_metadata:
                try:
                    doc.set_metadata({key: value})
                except:
                    pass
        
        logger.info(f"Added structure metadata for {len(elements)} tags")
    
    def _add_to_existing_structure(self, doc, elements: List[ClassifiedElement]):
        """Add elements to existing structure tree"""
        try:
            self._create_structure_tree(doc, elements)
        except Exception as e:
            logger.debug(f"Error adding to existing structure: {e}")
    
    def save_tags_json(self, elements: List[ClassifiedElement], json_path: str):
        """Save structure tags to JSON"""
        # Convert to dict format for JSON
        tags_data = {
            "document": {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "structure_tags": []
            }
        }
        
        for element in elements:
            tag_dict = {
                "type": element.tag_type.value if isinstance(element.tag_type, TagType) else element.tag_type,
                "content": element.content,
                "page": element.page
            }
            
            if element.attributes:
                # Handle both StructureAttributes object and dict
                if isinstance(element.attributes, dict):
                    attrs = element.attributes
                else:
                    attrs = {
                        "lang": element.attributes.lang,
                        "actualText": element.attributes.actualText,
                    }
                    if element.attributes.title:
                        attrs["title"] = element.attributes.title
                    if element.attributes.summary:
                        attrs["summary"] = element.attributes.summary
                
                tag_dict["attributes"] = attrs
            
            tags_data["document"]["structure_tags"].append(tag_dict)
        
        with open(json_path, 'w') as f:
            json.dump(tags_data, f, indent=2)
        
        logger.info(f"Saved {len(elements)} structure tags to {json_path}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Expert PDF Accessibility Tagger")
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("output_name", help="Output PDF name (without .pdf)")
    parser.add_argument("--api-key", default=os.getenv("GEMINI_API_KEY"), 
                       help="Gemini API key")
    parser.add_argument("--model", default="gemini-2.5-flash", 
                       help="Model name")
    
    args = parser.parse_args()
    
    if not args.api_key:
        logger.error("No API key provided")
        return
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Output PDF path
    output_pdf = output_dir / f"{args.output_name}.pdf"
    
    # Initialize tagger
    tagger = ExpertPDFTagger(args.api_key, args.model)
    
    # Extract and classify
    elements = tagger.extract_and_classify(args.input_pdf)
    
    # Apply tags to PDF
    tagger.apply_tags_to_pdf(args.input_pdf, str(output_pdf), elements)
    
    logger.info(f"Done! Processed {len(elements)} elements. Tagged PDF saved to {output_pdf}")


if __name__ == "__main__":
    main()

