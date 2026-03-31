import os, io, tempfile, shutil
from PIL import Image, ExifTags
from pypdf import PdfReader, PdfWriter
import ffmpeg, imageio_ffmpeg

def _get_extension(filename, file_obj):
    """Helper to find what type of file we are dealing with."""
    if filename:
        return os.path.splitext(filename)[1].lower()
    if hasattr(file_obj, 'filename'):
        return os.path.splitext(file_obj.filename)[1].lower()
    return ''

def _save_to_temp_disk(file_obj):
    """Saves a file from memory to the hard drive temporarily (needed for videos)."""
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    if hasattr(file_obj, 'seek'): 
        file_obj.seek(0)
    with open(temp_path, 'wb') as f:
        f.write(file_obj.read())
    if hasattr(file_obj, 'seek'): 
        file_obj.seek(0)
    return temp_path

def read_metadata(file_obj, filename=""):
    """Reads visible hidden data from a file."""
    ext = _get_extension(filename, file_obj)

    # 1. Handle PDF Files
    if ext == '.pdf':
        try:
            reader = PdfReader(file_obj)
            meta = reader.metadata
            if not meta: return None
            # Convert all metadata labels and values to strings
            return {str(k).strip('/'): str(v) for k, v in meta.items()}
        except Exception:
            return None

    # 2. Handle Video Files 
    if ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
        temp_path = _save_to_temp_disk(file_obj)
        try:
            # Use ffmpeg to probe the video for tags
            probe = ffmpeg.probe(temp_path, cmd=imageio_ffmpeg.get_ffmpeg_exe())
            data = probe.get('format', {}).get('tags', {})
            return data if data else None
        except Exception:
            return None
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)

    # 3. Handle Image Files 
    try:
        image = Image.open(file_obj)
        readable_data = {}
        
        # Get standard EXIF tags (like camera model, date taken)
        exif = image.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                readable_data[tag_name] = str(value)
                
            if hasattr(exif, 'get_ifd'):
                # Get advanced EXIF tags (like ISO, Shutter Speed)
                exif_info = exif.get_ifd(ExifTags.IFD.Exif)
                for tag_id, value in exif_info.items():
                    tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                    readable_data[tag_name] = str(value)
                    
                # Get GPS tags
                gps_info = exif.get_ifd(ExifTags.IFD.GPSInfo)
                for tag_id, value in gps_info.items():
                    tag_name = ExifTags.GPSTAGS.get(tag_id, tag_id)
                    readable_data[f"GPS {tag_name}"] = str(value)
                    
        return readable_data if readable_data else None
    except Exception:
        return None

def remove_metadata(file_obj, output_obj, filename=""):
    """Deletes metadata and saves a clean version to output_obj."""
    ext = _get_extension(filename, file_obj)

    # 1. Handle PDF Files
    if ext == '.pdf':
        try:
            reader = PdfReader(file_obj)
            writer = PdfWriter()
            
            # Copy all pages over 
            for page in reader.pages:
                writer.add_page(page)
                
            # Add an empty dictionary instead of metadata
            writer.add_metadata({}) 
            writer.write(output_obj)
            return True
        except Exception:
            return False

    # 2. Handle Video Files
    if ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
        in_temp = _save_to_temp_disk(file_obj)
        out_temp = in_temp + "_clean" + ext
        
        try:
            # Tell ffmpeg to copy video/audio (-c copy) and drop tags (-map_metadata -1)
            (
                ffmpeg
                .input(in_temp)
                .output(out_temp, vcodec='copy', acodec='copy', map_metadata='-1')
                .run(cmd=imageio_ffmpeg.get_ffmpeg_exe(), overwrite_output=True, quiet=True)
            )
            
            # Save the clean video back to our output destination
            with open(out_temp, 'rb') as f:
                output_obj.write(f.read())
            return True
        except Exception:
            return False
        finally:
            if os.path.exists(in_temp): os.remove(in_temp)
            if os.path.exists(out_temp): os.remove(out_temp)

    # 3. Handle Image Files
    try:
        image = Image.open(file_obj)
        
        # Create a brand new blank image with same size
        clean_image = Image.new(image.mode, image.size)
        
        # Copy ONLY the visual pixels (leaves metadata behind)
        clean_image.putdata(image.getdata()) 
        
        # Save it
        clean_image.save(output_obj, format=image.format or 'JPEG')
        return True
    except Exception:
        return False
