document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('converter-form');
    const fileInput = document.getElementById('files');
    const fileList = document.getElementById('fileList');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const qualitySlider = document.getElementById('quality');
    const qualityValue = document.getElementById('quality-value');

    fileInput.addEventListener('change', function(e) {
        fileList.innerHTML = '';
        for(let i = 0; i < this.files.length; i++) {
            const file = this.files[i];
            const fileSize = (file.size / (1024 * 1024)).toFixed(2);
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.textContent = `${file.name} (${fileSize}MB)`;
            fileList.appendChild(fileItem);
        }
    });

    qualitySlider.addEventListener('input', function(e) {
        qualityValue.textContent = this.value;
    });

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        errorMessage.style.display = 'none';
        loading.style.display = 'block';

        const formData = new FormData(this);

        fetch('/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => Promise.reject(err));
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'converted_images.zip';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        })
        .catch(error => {
            errorMessage.textContent = error.error || 'An error occurred during conversion';
            errorMessage.style.display = 'block';
        })
        .finally(() => {
            loading.style.display = 'none';
        });
    });
});