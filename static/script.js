document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewSection = document.getElementById('preview-section');
    const imagePreview = document.getElementById('image-preview');
    const generateBtn = document.getElementById('generate-btn');
    const loadingSection = document.getElementById('loading');
    const resultSection = document.getElementById('result-section');
    const captionText = document.getElementById('caption-text');

    // Handle click to upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle file selection
    fileInput.addEventListener('change', handleFileSelect);
    dropZone.addEventListener('drop', handleDrop);

    // Handle generate button click
    generateBtn.addEventListener('click', generateCaption);

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight() {
        dropZone.classList.add('dragover');
    }

    function unhighlight() {
        dropZone.classList.remove('dragover');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (validateFile(file)) {
                displayPreview(file);
            }
        }
    }

    function validateFile(file) {
        const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
        if (!validTypes.includes(file.type)) {
            showError('Please upload a valid image file (JPEG, PNG, or GIF)');
            return false;
        }
        if (file.size > 5 * 1024 * 1024) { // 5MB limit
            showError('Image size should be less than 5MB');
            return false;
        }
        return true;
    }

    function displayPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            previewSection.style.display = 'block';
            resultSection.style.display = 'none';
            removeError();
        };
        reader.readAsDataURL(file);
    }

    async function generateCaption() {
        try {
            const formData = new FormData();
            const file = fileInput.files[0];
            if (!file) {
                showError('Please select an image first');
                return;
            }

            formData.append('image', file);
            
            // Show loading state
            loadingSection.style.display = 'block';
            generateBtn.disabled = true;
            
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to generate caption');
            }

            const data = await response.json();
            
            // Display result
            captionText.textContent = data.caption;
            resultSection.style.display = 'block';
            
        } catch (error) {
            showError('An error occurred while generating the caption. Please try again.');
            console.error('Error:', error);
        } finally {
            loadingSection.style.display = 'none';
            generateBtn.disabled = false;
        }
    }

    function showError(message) {
        removeError();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        dropZone.parentNode.insertBefore(errorDiv, dropZone);
    }

    function removeError() {
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }
});
