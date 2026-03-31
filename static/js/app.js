// Run code only after the page has fully loaded
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Find all important HTML elements
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const resetBtn = document.getElementById('reset-btn');
    const viewBtn = document.getElementById('view-meta-btn');
    const removeBtn = document.getElementById('remove-meta-btn');
    
    let currentFile = null;

    // 2. Handle File Selection
    // Clicking our 'Browse' button actually clicks the hidden file input
    browseBtn.onclick = () => fileInput.click();
    
    fileInput.onchange = (event) => {
        if (event.target.files.length > 0) {
            currentFile = event.target.files[0];
            
            // Show the file name and switch interface views
            document.getElementById('file-name').textContent = currentFile.name;
            document.getElementById('file-preview').style.display = 'block';
            document.getElementById('drop-zone').style.display = 'none';
        }
    };

    // 3. Handle Reset (X button)
    resetBtn.onclick = () => {
        currentFile = null;
        fileInput.value = ''; // Clear file input
        
        // Hide preview and results, show upload zone again
        document.getElementById('file-preview').style.display = 'none';
        document.getElementById('results-section').style.display = 'none';
        document.getElementById('drop-zone').style.display = 'block';
    };

    // 4. Handle "View Metadata"
    viewBtn.onclick = async () => {
        if (!currentFile) return;

        // Prepare file to send
        const formData = new FormData();
        formData.append('file', currentFile);

        // Send file to Python server
        const response = await fetch('/api/metadata', { method: 'POST', body: formData });
        const data = await response.json();
        
        // Show results table
        document.getElementById('results-section').style.display = 'block';
        const tbody = document.getElementById('metadata-body');
        tbody.innerHTML = ''; // Clear previous

        // If no metadata found
        if (data.count === 0) {
            tbody.innerHTML = `<tr><td colspan="2">No hidden data found!</td></tr>`;
            return;
        }

        // Add a table row for each metadata item
        for (const [key, value] of Object.entries(data.metadata)) {
            tbody.innerHTML += `<tr><td><strong>${key}</strong></td><td>${value}</td></tr>`;
        }
    };

    // 5. Handle "Remove & Download"
    removeBtn.onclick = async () => {
        if (!currentFile) return;

        // Prepare file to send
        const formData = new FormData();
        formData.append('file', currentFile);

        // Send file to Python server's remove route
        const response = await fetch('/api/remove', { method: 'POST', body: formData });
        
        if (response.ok) {
            // Get the cleaned file back from server
            const blob = await response.blob();
            
            // Create a temporary link to download the file
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = "clean_" + currentFile.name;
            
            // Force download and cleanup
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(downloadUrl);
            
            alert("Success! Cleaned file downloaded.");
        } else {
            alert("Error removing metadata.");
        }
    };
});
