"""
PDF Structure Taxonomy for PDF/UA compliance
Implements the complete structure element taxonomy for accessible PDFs
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum


class TagType(Enum):
    """PDF Structure Tag Types"""
    
    # Document Structure
    DOCUMENT = "Document"
    PART = "Part"
    ART = "Art"
    SECT = "Sect"
    DIV = "Div"
    
    # Headings
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    H5 = "H5"
    H6 = "H6"
    
    # Text Elements
    P = "P"  # Paragraph
    QUOTE = "Quote"
    NOTE = "Note"
    SPAN = "Span"
    
    # Lists
    L = "L"  # List
    LI = "LI"  # List Item
    LBL = "Lbl"  # Label
    LBODY = "LBody"  # List Body
    
    # Tables
    TABLE = "Table"
    TR = "TR"  # Table Row
    TH = "TH"  # Table Header Cell
    TD = "TD"  # Table Data Cell
    THEAD = "THead"
    TBODY = "TBody"
    TFOOT = "TFoot"
    
    # Figures & Figures
    FIGURE = "Figure"
    CAPTION = "Caption"
    FORMULA = "Formula"
    
    # Links & References
    LINK = "Link"
    REFERENCE = "Reference"
    
    # Forms
    FORM = "Form"
    ANNOT = "Annot"
    
    # Special
    ARTIFACT = "Artifact"
    TOC = "TOC"  # Table of Contents
    TOCI = "TOCI"  # TOC Item
    INDEX = "Index"
    
    # Ruby Annotations
    RUBY = "Ruby"
    RB = "RB"  # Ruby Base
    RT = "RT"  # Ruby Text
    RP = "RP"  # Ruby Pronunciation


@dataclass
class StructureAttributes:
    """Attributes for PDF structure elements"""
    
    alt: Optional[str] = None
    lang: Optional[str] = None
    actualText: Optional[str] = None
    title: Optional[str] = None
    checked: Optional[str] = None
    columnSpan: Optional[int] = None
    headers: Optional[List[str]] = None
    id: Optional[str] = None
    name: Optional[str] = None
    next: Optional[str] = None
    prev: Optional[str] = None
    role: Optional[str] = None
    rowSpan: Optional[int] = None
    summary: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class StructureTag:
    """Represents a PDF structure tag with its properties"""
    
    tag_type: TagType
    content: str
    attributes: Optional[StructureAttributes] = None
    children: Optional[List['StructureTag']] = None
    page: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        result = {
            "type": self.tag_type.value,
            "content": self.content,
        }
        
        if self.attributes:
            result["attributes"] = self.attributes.to_dict()
        
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        
        if self.page is not None:
            result["page"] = self.page
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StructureTag':
        """Create from dictionary"""
        tag = cls(
            tag_type=TagType(data["type"]),
            content=data["content"],
            page=data.get("page")
        )
        
        if "attributes" in data:
            tag.attributes = StructureAttributes(**data["attributes"])
        
        if "children" in data:
            tag.children = [cls.from_dict(child) for child in data["children"]]
        
        return tag


class TaxonomyClassifier:
    """Classify content into PDF structure taxonomy"""
    
    # Content patterns for classification
    HEADING_PATTERNS = [
        r'^(#+|\d+\.?\s+[A-Z])',  # Markdown or numbered headings
        r'^[A-Z][A-Z ]{5,}$',  # ALL CAPS headings
        r'^Chapter \d+',  # Chapter headings
        r'^Section \d+',  # Section headings
    ]
    
    LIST_INDICATORS = ['•', '▪', '‣', '-', '*', '○', '◦']
    NUMBERED_LIST_PATTERN = r'^\d+[\.\)]\s+'
    
    TABLE_INDICATORS = ['\t', '|', '---', '===']
    
    # Mapping from generic types to specific taxonomy
    TYPE_MAPPING = {
        'paragraph': TagType.P,
        'heading': TagType.H1,
        'heading1': TagType.H1,
        'heading2': TagType.H2,
        'heading3': TagType.H3,
        'heading4': TagType.H4,
        'heading5': TagType.H5,
        'heading6': TagType.H6,
        'list': TagType.L,
        'list_item': TagType.LI,
        'table': TagType.TABLE,
        'table_row': TagType.TR,
        'table_cell': TagType.TD,
        'table_header': TagType.TH,
        'figure': TagType.FIGURE,
        'caption': TagType.CAPTION,
        'formula': TagType.FORMULA,
        'link': TagType.LINK,
        'quote': TagType.QUOTE,
        'note': TagType.NOTE,
    }
    
    @classmethod
    def classify_content(cls, content: str, context: str = "", 
                        detected_type: str = "") -> TagType:
        """Classify content into appropriate tag type"""
        
        # Check for specific detected types first
        if detected_type in cls.TYPE_MAPPING:
            return cls.TYPE_MAPPING[detected_type]
        
        # Auto-detect based on content
        content_upper = content.upper().strip()
        
        # Check for headings
        if any(pattern.startswith('^') and len(content_upper.split()) <= 10 
               for pattern in cls.HEADING_PATTERNS):
            # Determine heading level
            if content_upper.startswith('CHAPTER') or content_upper.startswith('PART'):
                return TagType.H1
            elif content_upper.startswith('SECTION'):
                return TagType.H2
            elif len(content_upper) > 50:
                return TagType.H6
            else:
                return TagType.H1  # Default to H1
        
        # Check for paragraphs (default)
        return TagType.P
    
    @classmethod
    def suggest_heading_level(cls, content: str, context: str = "") -> int:
        """Suggest heading level 1-6 based on content"""
        content_upper = content.upper().strip()
        word_count = len(content_upper.split())
        
        if content_upper.startswith('CHAPTER') or content_upper.startswith('PART'):
            return 1
        elif content_upper.startswith('SECTION') or word_count <= 5:
            return 2
        elif word_count <= 10 and content_upper.isupper():
            return 3
        elif word_count <= 15:
            return 4
        elif word_count <= 20:
            return 5
        else:
            return 6
    
    @classmethod
    def classify_list_type(cls, content: str) -> Dict:
        """Classify list and determine if ordered or unordered"""
        import re
        
        # Check for numbered items
        if re.search(r'\d+[\.\)]\s+', content):
            return {
                "list_type": "ordered",
                "style": "decimal"
            }
        
        # Check for lettered items
        elif re.search(r'[a-z][\.\)]\s+', content, re.IGNORECASE):
            return {
                "list_type": "ordered",
                "style": "alpha"
            }
        
        # Check for bullet points
        elif any(indicator in content for indicator in cls.LIST_INDICATORS):
            return {
                "list_type": "unordered",
                "style": "disc"
            }
        
        # Default to unordered
        return {
            "list_type": "unordered",
            "style": "disc"
        }
    
    @classmethod
    def classify_table_structure(cls, table_data: List[List]) -> Dict:
        """Classify table structure and identify headers"""
        if not table_data:
            return {}
        
        headers = []
        has_header = False
        
        # Check first row for headers (typically all caps or short phrases)
        first_row = table_data[0]
        if all(isinstance(cell, str) and 
               (cell.isupper() or len(cell.split()) <= 5) 
               for cell in first_row if cell):
            headers = first_row
            has_header = True
        
        return {
            "header_count": len(headers),
            "headers": headers,
            "has_header": has_header,
            "row_count": len(table_data),
            "column_count": len(table_data[0]) if table_data else 0
        }
    
    @classmethod
    def extract_formula(cls, content: str) -> Optional[Dict]:
        """Extract mathematical formula if present"""
        import re
        
        # Look for common formula patterns
        formula_patterns = [
            r'\$\$.*?\$\$',  # LaTeX block math
            r'\$.*?\$',  # LaTeX inline math
            r'\\\[.*?\\\]',  # LaTeX display
            r'\\\(.*?\\\)',  # LaTeX inline
            r'[A-Za-z]\s*[=<>]\s*[A-Za-z\d\s\+\-\*/\(\)]+',  # Equations
        ]
        
        for pattern in formula_patterns:
            match = re.search(pattern, content)
            if match:
                return {
                    "type": "Formula",
                    "formula": match.group(0),
                    "raw_text": content
                }
        
        return None

