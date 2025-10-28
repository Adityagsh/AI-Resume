import PyPDF2
try:
    from docx import Document
except ImportError:
    raise ImportError("python-docx is required. Install with: pip install python-docx")
import io

class ResumeParser:
    def extract_text(self, uploaded_file):
        """Extract text from PDF or DOCX files"""
        # Get file type from content type or filename
        file_type = getattr(uploaded_file, 'content_type', None) or getattr(uploaded_file, 'type', None)
        filename = getattr(uploaded_file, 'filename', '')
        
        # Determine file type from extension if content type is not available
        if not file_type and filename:
            if filename.lower().endswith('.pdf'):
                file_type = "application/pdf"
            elif filename.lower().endswith('.docx'):
                file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif filename.lower().endswith('.txt'):
                return uploaded_file.read().decode('utf-8')
        
        if file_type == "application/pdf" or (filename and filename.lower().endswith('.pdf')):
            return self._extract_from_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or (filename and filename.lower().endswith('.docx')):
            return self._extract_from_docx(uploaded_file)
        elif file_type == "text/plain" or (filename and filename.lower().endswith('.txt')):
            return uploaded_file.read().decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_type}. Please upload PDF, DOCX, or TXT files.")
    
    def _extract_from_pdf(self, file):
        # amazonq-ignore-next-line
        """Extract text from PDF"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            return "".join(page.extract_text() for page in pdf_reader.pages)
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {str(e)}")
    
    def _extract_from_docx(self, file):
        """Extract text from DOCX"""
        try:
            doc = Document(io.BytesIO(file.read()))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        except Exception as e:
            raise ValueError(f"Error reading DOCX file: {str(e)}")