from PIL import Image, ExifTags
from pypdf import PdfReader, PdfWriter
import io

def _is_pdf(filename, source):
    """Helper method to determine if the input is a PDF file."""
    if filename and str(filename).lower().endswith('.pdf'):
        return True
    if isinstance(source, str) and source.lower().endswith('.pdf'):
        return True
    if hasattr(source, 'filename') and source.filename.lower().endswith('.pdf'):
        return True
    if hasattr(source, 'name') and source.name.lower().endswith('.pdf'):
        return True
    return False

def read_metadata(input_source, filename=""):
    """
    Reads metadata from either an Image or a PDF.
    """
    # ====== PDF LOGIC ======
    if _is_pdf(filename, input_source):
        try:
            reader = PdfReader(input_source)
            meta = reader.metadata
            if not meta: return None
            # Return dictionary cleaning up the weird PDF slashes (e.g. '/Creator' -> 'Creator')
            return {str(k).strip('/'): str(v) for k, v in meta.items()}
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    # ====== IMAGE LOGIC ======
    try:
        image = Image.open(input_source)
        raw_exif = image._getexif()
        
        if not raw_exif:
            return None
            
        readable_data = {}
        for tag_id, value in raw_exif.items():
            tag_name = ExifTags.TAGS.get(tag_id, tag_id)
            readable_data[tag_name] = value
            
        return readable_data
        
    except Exception as e:
        print(f"Error reading Image metadata: {e}")
        return None

def remove_metadata(input_source, output_destination, filename=""):
    """
    Removes metadata from either an Image or a PDF.
    """
    # ====== PDF LOGIC ======
    if _is_pdf(filename, input_source):
        try:
            reader = PdfReader(input_source)
            writer = PdfWriter()
            
            # Copy all the visual pages over successfully
            for page in reader.pages:
                writer.add_page(page)
                
            # Explicitly overwrite the document metadata with an empty dictionary
            writer.add_metadata({})
            
            writer.write(output_destination)
            return True
        except Exception as e:
            print(f"Error removing PDF metadata: {e}")
            return False

    # ====== IMAGE LOGIC ======
    try:
        image = Image.open(input_source)
        pixels = list(image.getdata())
        clean_image = Image.new(image.mode, image.size)
        clean_image.putdata(pixels)
        
        # Save it to the destination (hard drive or memory stream)
        clean_image.save(output_destination, format=image.format or 'JPEG')
        return True
        
    except Exception as e:
        print(f"Error removing Image metadata: {e}")
        return False
