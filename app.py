import io
from flask import Flask, request, jsonify, render_template, send_file
from metadata_remover import read_metadata, remove_metadata

app = Flask(__name__)

# 1. Homepage Route
@app.route('/')
def index():
    return render_template('index.html')

# 2. View Metadata Route
@app.route('/api/metadata', methods=['POST'])
def view_metadata():
    # Get the uploaded file
    file = request.files['file']
    
    # Read the metadata
    metadata = read_metadata(file, file.filename)
    
    if metadata:
        # Convert all values to strings for JSON
        clean_metadata = {str(k): str(v) for k, v in metadata.items()}
        return jsonify({'metadata': clean_metadata, 'count': len(clean_metadata)})
    else:
        return jsonify({'metadata': {}, 'count': 0})

# 3. Remove Metadata Route
@app.route('/api/remove', methods=['POST'])
def remove_data():
    # Get the uploaded file
    file = request.files['file']
    
    # Create an empty memory space to hold the cleaned file
    memory_file = io.BytesIO()
    
    # Remove metadata and save strictly to memory_file
    success = remove_metadata(file, memory_file, file.filename)
    
    if not success:
        return jsonify({'error': 'Failed to remove metadata'}), 500
        
    # Go back to the start of the memory file before sending
    memory_file.seek(0)
    
    # Send the clean file back to the browser for download
    return send_file(
        memory_file, 
        as_attachment=True, 
        download_name=f"clean_{file.filename}"
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
