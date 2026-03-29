// Wait for the webpage to fully load before running our code
document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Find all our HTML elements ---
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const viewMetaBtn = document.getElementById('view-meta-btn');
    const removeMetaBtn = document.getElementById('remove-meta-btn');
    const fileNameDisplay = document.getElementById('file-name');
    const metadataBody = document.getElementById('metadata-body');
    const resultsSection = document.getElementById('results-section');
    
    // This variable will remember the file the user selected
    let currentImageFile = null;

    // --- 2. Handle File Selection ---
    // Make our pretty button click the ugly hidden file input
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // When the user picks a file, save it and show the filename
    fileInput.addEventListener('change', (event) => {
        const files = event.target.files;
        if (files.length > 0) {
            currentImageFile = files[0];
            fileNameDisplay.textContent = currentImageFile.name;
            
            // Show the preview area (assuming CSS class handling or direct style)
            document.getElementById('file-preview').style.display = 'block';
            document.getElementById('drop-zone').style.display = 'none';
        }
    });

    // --- 3. The "View Metadata" Button ---
    viewMetaBtn.addEventListener('click', async () => {
        if (!currentImageFile) return;

        // Package the image into a digital envelope
        const envelope = new FormData();
        envelope.append('file', currentImageFile);

        // Send it to the Python server!
        const serverReply = await fetch('/api/metadata', {
            method: 'POST',
            body: envelope
        });
        
        // Read the server's JSON answer
        const responseData = await serverReply.json();
        
        // Show the results section
        resultsSection.style.display = 'block';
        metadataBody.innerHTML = ''; // Clear old results

        // If no data was found, tell the user
        if (responseData.count === 0) {
            metadataBody.innerHTML = `<tr><td colspan="2">No hidden data found!</td></tr>`;
            return;
        }

        // Loop through the data and create a table row for each item
        for (const [key, value] of Object.entries(responseData.metadata)) {
            const row = document.createElement('tr');
            row.innerHTML = `<td><strong>${key}</strong></td><td>${value}</td>`;
            metadataBody.appendChild(row);
        }
    });

    // --- 4. The "Remove & Download" Button ---
    removeMetaBtn.addEventListener('click', async () => {
        if (!currentImageFile) return;

        // Package the dirty image
        const envelope = new FormData();
        envelope.append('file', currentImageFile);

        // Send it to the Python server's remove route
        const serverReply = await fetch('/api/remove', {
            method: 'POST',
            body: envelope
        });
        
        if (serverReply.ok) {
            // The server successfully replied with the Clean File data (a Blob)
            const cleanImageBlob = await serverReply.blob();
            
            // Create a temporary link to the clean file in memory
            const downloadLink = document.createElement('a');
            downloadLink.href = window.URL.createObjectURL(cleanImageBlob);
            downloadLink.download = "clean_" + currentImageFile.name; // Name the downloaded file
            
            // Click the link to force the browser to download it
            document.body.appendChild(downloadLink);
            downloadLink.click();
            
            // Clean up the temporary link immediately
            downloadLink.remove();
            window.URL.revokeObjectURL(downloadLink.href);
            
            alert("Success! Cleaned image has been downloaded.");
        } else {
            alert("Error removing metadata.");
        }
    });
});
