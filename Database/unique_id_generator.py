import hashlib
import json
from datetime import datetime
from pathlib import Path
import PyPDF2
import uuid

class PDFIdentifier:
    def __init__(self, storage_path='pdf_metadata.json'):
        self.storage_path = storage_path
        self.metadata = self._load_metadata()
    
    def _load_metadata(self):
        """Load existing metadata from JSON file."""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_metadata(self):
        """Save metadata to JSON file."""
        with open(self.storage_path, 'w') as f:
            json.dump(self.metadata, f, indent=4)
    
    def _calculate_pdf_hash(self, pdf_path):
        """Calculate SHA-256 hash of PDF content."""
        sha256_hash = hashlib.sha256()
        with open(pdf_path, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b''):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _get_pdf_metadata(self, pdf_path):
        """Extract metadata from PDF."""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            return {
                'page_count': len(reader.pages),
                'file_size': Path(pdf_path).stat().st_size,
                'content_hash': self._calculate_pdf_hash(pdf_path),
                'last_modified': datetime.fromtimestamp(
                    Path(pdf_path).stat().st_mtime
                ).isoformat()
            }
    
    def generate_id(self, pdf_path):
        """Generate or retrieve unique ID for PDF."""
        # Extract current PDF metadata
        current_metadata = self._get_pdf_metadata(pdf_path)
        
        # Check for existing PDFs with matching content hash
        for stored_id, stored_data in self.metadata.items():
            if stored_data['content_hash'] == current_metadata['content_hash']:
                print(f"Exact content match found. Returning existing ID: {stored_id}")
                return stored_id
        
        # Generate new unique ID
        new_id = ''.join(filter(str.isalpha, str(uuid.uuid4())))[:8]
        
        # Store metadata
        self.metadata[new_id] = {
            'filename': Path(pdf_path).name,
            **current_metadata,
            'created_at': datetime.now().isoformat()
        }
        
        # Save updated metadata
        self._save_metadata()
        
        print(f"New PDF detected. Generated ID: {new_id}")
        return new_id
    
