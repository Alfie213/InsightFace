document.getElementById('imageUpload').addEventListener('change', async function(event) {
    const previewImage = document.getElementById('previewImage');
    const file = event.target.files[0];

    if (file) {
        // Шаг 1: Отображаем загруженное фото на фронтенде сразу, до обработки
        // Это дает пользователю немедленную обратную связь.
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            previewImage.classList.remove('hidden');
        };
        reader.readAsDataURL(file);

        // Шаг 2: Отправляем фото на бэкенд для обработки
        const formData = new FormData(); // FormData используется для отправки файлов через HTTP. [1, 2, 3]
        formData.append('image', file); // 'image' - это имя поля, которое ожидает Flask-сервер в request.files['image']. [1]

        try {
            // Отправляем POST-запрос на наш Flask-сервер
            // Убедитесь, что URL соответствует адресу, на котором запущен ваш бэкенд (например, http://localhost:5000)
            const response = await fetch('http://localhost:5000/process-image', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                // Если запрос успешен, получаем ответ как Blob (бинарные данные изображения). [4]
                const blob = await response.blob();
                // Создаем URL-объект, который ссылается на Blob. [4]
                const imageUrl = URL.createObjectURL(blob);
                // Обновляем src элемента <img>, чтобы показать обработанное изображение
                previewImage.src = imageUrl;
                previewImage.classList.remove('hidden');
            } else {
                // Если сервер вернул ошибку, пытаемся прочитать её как JSON
                const errorData = await response.json();
                console.error('Ошибка при обработке изображения:', errorData.error);
                alert('Ошибка при обработке изображения: ' + errorData.error);
                // В случае ошибки скрываем изображение или показываем заглушку
                previewImage.src = "#";
                previewImage.classList.add('hidden');
            }
        } catch (error) {
            // Обработка сетевых ошибок или ошибок сервера, которые не вернули JSON
            console.error('Произошла ошибка сети или сервера:', error);
            alert('Не удалось связаться с сервером. Пожалуйста, убедитесь, что бэкенд запущен, и попробуйте еще раз.');
            previewImage.src = "#";
            previewImage.classList.add('hidden');
        }

    } else {
        // Если файл не был выбран (например, пользователь отменил диалог выбора файла)
        previewImage.src = "#";
        previewImage.classList.add('hidden');
    }
});