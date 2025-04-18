document.addEventListener('DOMContentLoaded', function() {
    // File upload functionality
    setupFileUpload('file1', 'drop-zone-1', 'file1-info', 'file1-name', 'remove-file1');
    setupFileUpload('file2', 'drop-zone-2', 'file2-info', 'file2-name', 'remove-file2');

    // Form submission with loading state
    const uploadForm = document.getElementById('upload-form');
    const loadingDiv = document.getElementById('loading');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Form validation
            if (!uploadForm.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
                uploadForm.classList.add('was-validated');
                return;
            }
            
            // Show loading state
            loadingDiv.classList.remove('d-none');
            
            // Start progress animation
            const progressBar = loadingDiv.querySelector('.progress-bar');
            progressBar.classList.add('progress-animated');
            
            // Submit form
            uploadForm.classList.add('d-none');
        });
    }
});

// Setup file upload functionality for a specific input
function setupFileUpload(fileInputId, dropZoneId, fileInfoId, fileNameId, removeButtonId) {
    const fileInput = document.getElementById(fileInputId);
    const dropZone = document.getElementById(dropZoneId);
    const fileInfo = document.getElementById(fileInfoId);
    const fileName = document.getElementById(fileNameId);
    const removeButton = document.getElementById(removeButtonId);
    
    if (!fileInput || !dropZone || !fileInfo || !fileName || !removeButton) {
        return;
    }
    
    // Handle file selection via input
    fileInput.addEventListener('change', function() {
        handleFileSelection(this.files);
    });
    
    // Handle drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropZone.classList.add('active');
    }
    
    function unhighlight() {
        dropZone.classList.remove('active');
    }
    
    // Handle file drop
    dropZone.addEventListener('drop', function(e) {
        handleFileSelection(e.dataTransfer.files);
    });
    
    // Handle file removal
    removeButton.addEventListener('click', function() {
        fileInput.value = '';
        fileInfo.classList.add('d-none');
        dropZone.classList.remove('d-none');
    });
    
    // Process selected files
    function handleFileSelection(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        
        // Validate file type
        if (file.type !== 'application/pdf') {
            alert('Please select a PDF file.');
            return;
        }
        
        // Display file info
        fileName.textContent = file.name;
        fileInfo.classList.remove('d-none');
        dropZone.classList.add('d-none');
    }
}
