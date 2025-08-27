document.getElementById('imageUpload').addEventListener('change', function(event) {
    const previewImage = document.getElementById('previewImage');
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();

        reader.onload = function(e) {
            previewImage.src = e.target.result;
            previewImage.classList.remove('hidden');
        };

        reader.readAsDataURL(file);
    } else {
        previewImage.src = "#";
        previewImage.classList.add('hidden');
    }
});