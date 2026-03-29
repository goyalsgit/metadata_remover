import os
import io
import tempfile
import shutil
from PIL import Image, ExifTags
from pypdf import PdfReader, PdfWriter
import ffmpeg
import imageio_ffmpeg

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

def _is_video(filename, source):
    """Helper method to determine if the input is a Video file."""
    video_exts = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
    if filename and str(filename).lower().endswith(video_exts):
        return True
    if isinstance(source, str) and source.lower().endswith(video_exts):
        return True
    if hasattr(source, 'filename') and source.filename.lower().endswith(video_exts):
        return True
    if hasattr(source, 'name') and source.name.lower().endswith(video_exts):
        return True
    return False

def read_metadata(input_source, filename=""):
    """
    Reads metadata from a Video, PDF, or Image.
    """
    # ====== PDF LOGIC ======
    if _is_pdf(filename, input_source):
        try:
            reader = PdfReader(input_source)
            meta = reader.metadata
            if not meta: return None
            return {str(k).strip('/'): str(v) for k, v in meta.items()}
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    # ====== VIDEO LOGIC ======
    if _is_video(filename, input_source):
        temp_path = None
        try:
            # We need a physical file to probe video with ffmpeg
            temp_path = _save_to_temp_file(input_source)
            probe = ffmpeg.probe(temp_path, cmd=imageio_ffmpeg.get_ffmpeg_exe())
            
            readable_data = {}
            if 'format' in probe and 'tags' in probe['format']:
                tags = probe['format']['tags']
                for k, v in tags.items():
                    readable_data[f"Video Base: {k}"] = v
                    
            for stream in probe.get('streams', []):
                s_type = stream.get('codec_type', 'unknown').capitalize()
                for k, v in stream.get('tags', {}).items():
                    readable_data[f"{s_type} Track: {k}"] = v
                    
            return readable_data if readable_data else None
            
        except Exception as e:
            print(f"Error reading Video metadata: {e}")
            return None
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    # ====== IMAGE LOGIC ======
    try:
        image = Image.open(input_source)
        readable_data = {}
        
        # 1. Standard EXIF
        exif = image.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except Exception:
                        value = "<Binary Data>"
                readable_data[tag_name] = value
                
            # GPS Sub-dictionary
            gps_info = exif.get_ifd(ExifTags.IFD.GPSInfo) if hasattr(exif, 'get_ifd') else {}
            for key, val in gps_info.items():
                tag_name = ExifTags.GPSTAGS.get(key, key)
                readable_data[f"GPS {tag_name}"] = val
                
        # 2. Extract embedded text tags (usually in PNGs)
        if hasattr(image, "text") and image.text:
            for k, v in image.text.items():
                readable_data[f"PNG Text: {k}"] = v
                
        # 3. Extract info tags (common for JPEGs and other headers)
        for k, v in image.info.items():
            if k in ['Title', 'Author', 'Description', 'Comment', 'XML:com.adobe.xmp', 'Software', 'dpi']:
                if isinstance(v, bytes):
                    continue
                # If XML is huge, truncate it just to show it exists but limit length
                if isinstance(v, str) and len(v) > 200:
                    v = v[:200] + " ... <truncated>"
                readable_data[f"Info: {k}"] = v
                
        return readable_data if readable_data else None
                
    except Exception as e:
        print(f"Error reading Image metadata: {e}")
        return None

def _save_to_temp_file(source):
    """Takes a stream or path and creates a temporary disk file for ffmpeg."""
    fd, temp_path = tempfile.mkstemp(suffix=".tmp")
    os.close(fd)
    
    if isinstance(source, str):
        shutil.copy2(source, temp_path)
    else:
        # Seek to start if it's a file stream
        if hasattr(source, 'seek'):
            source.seek(0)
        with open(temp_path, 'wb') as f:
            f.write(source.read())
        if hasattr(source, 'seek'):
            source.seek(0)
    return temp_path

def remove_metadata(input_source, output_destination, filename=""):
    """
    Removes metadata from a Video, PDF, or Image.
    """
    # ====== PDF LOGIC ======
    if _is_pdf(filename, input_source):
        try:
            reader = PdfReader(input_source)
            writer = PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.add_metadata({})
            writer.write(output_destination)
            return True
        except Exception as e:
            print(f"Error removing PDF metadata: {e}")
            return False

    # ====== VIDEO LOGIC ======
    if _is_video(filename, input_source):
        in_temp = None
        out_temp = None
        try:
            in_temp = _save_to_temp_file(input_source)
            # Find exact extension if possible to preserve video container
            ext = os.path.splitext(filename if filename else str(input_source))[1].lower()
            if not ext or ext not in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                ext = '.mp4'
                
            fd, out_temp = tempfile.mkstemp(suffix=ext)
            os.close(fd)
            
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            
            # Use ffmpeg to clear metadata mapping
            (
                ffmpeg
                .input(in_temp)
                .output(out_temp, vcodec='copy', acodec='copy', map_metadata='-1')
                .run(cmd=ffmpeg_exe, overwrite_output=True, quiet=True)
            )
            
            # Write out to output_destination
            if isinstance(output_destination, str):
                shutil.copy2(out_temp, output_destination)
            else:
                with open(out_temp, 'rb') as f:
                    output_destination.write(f.read())
                    
            return True
        except Exception as e:
            print(f"Error removing Video metadata: {e}")
            return False
        finally:
            if in_temp and os.path.exists(in_temp):
                os.remove(in_temp)
            if out_temp and os.path.exists(out_temp):
                os.remove(out_temp)

    # ====== IMAGE LOGIC ======
    try:
        image = Image.open(input_source)
        clean_image = Image.new(image.mode, image.size)
        clean_image.putdata(image.getdata())
        clean_image.save(output_destination, format=image.format or 'JPEG')
        return True
    except Exception as e:
        print(f"Error removing Image metadata: {e}")
        return False
