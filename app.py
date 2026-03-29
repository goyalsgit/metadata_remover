import io
from flask import Flask, request, jsonify, render_template, send_file
from metadata_remover import read_metadata, remove_metadata

# 1. Start our Web Server
app = Flask(__name__)

# 2. Serve the website visually when someone visits the homepage
@app.route('/')
def index():
    return render_template('index.html')

# 3. Handle the "View Metadata" button
@app.route('/api/metadata', methods=['POST'])
def api_metadata():
    # Grab the uploaded file from the user
    uploaded_file = request.files['file']
    
    # Read the data, passing the filename so it knows if it's a PDF
    try:
        metadata = read_metadata(uploaded_file, uploaded_file.filename)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

    # Ensure everything is neatly formatted as text before sending back
    if metadata:
        safe_meta = {str(k): str(v) for k, v in metadata.items()}
        return jsonify({'metadata': safe_meta, 'count': len(metadata)})
    else:
        return jsonify({'metadata': {}, 'count': 0, 'message': 'No metadata found'})

# 4. Handle the "Remove & Download" button
@app.route('/api/remove', methods=['POST'])
def api_remove():
    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    
    # Invisible memory buffer (no temporary hard drive files needed!)
    memory_canvas = io.BytesIO()
    
    try:
        # Erase data and save the clean file into our memory canvas
        remove_metadata(uploaded_file, memory_canvas, filename)
        
        # Rewind the canvas back to the beginning so the user can download it
        memory_canvas.seek(0)
        
        # Determine the correct file type so the browser knows how to download it
        if filename.lower().endswith('.pdf'):
            download_mimetype = 'application/pdf'
        else:
            download_mimetype = uploaded_file.mimetype
        
        # Send the clean file directly from memory to the user's browser!
        return send_file(
            memory_canvas, 
            as_attachment=True, 
            download_name=f"clean_{filename}",
            mimetype=download_mimetype
        )
    except Exception as error:
        return jsonify({'error': str(error)}), 500

# 5. Turn the server on!
if __name__ == '__main__':
    app.run(debug=True, port=5000)
