// Получаем ссылки на элементы DOM
const mainPage = document.getElementById('mainPage');
const advicePage = document.getElementById('advicePage');
const tipDetailPage = document.getElementById('tipDetailPage');

const imageUploadInput = document.getElementById('imageUpload');
const imagePreviewContainer = document.getElementById('imagePreviewContainer');
const previewImage = document.getElementById('previewImage');
const loadingIndicator = document.getElementById('loadingIndicator');
const loadingMessage = document.getElementById('loadingMessage');
const categoryButtonsContainer = document.getElementById('categoryButtonsContainer');

// ЭЛЕМЕНТЫ ДЛЯ СООБЩЕНИЙ ОБ ОШИБКАХ
const errorMessageContainer = document.getElementById('errorMessageContainer');
const errorMessageText = document.getElementById('errorMessageText');

// ЭЛЕМЕНТЫ ДЛЯ СИММЕТРИИ
const symmetryResultsContainer = document.getElementById('symmetryResultsContainer');
const symmetryIndexDisplay = document.getElementById('symmetryIndex');
const symmetryDescriptionDisplay = document.getElementById('symmetryDescription');

// ЭЛЕМЕНТЫ ДЛЯ ФОРМЫ ЛИЦА
const faceShapeResultsContainer = document.getElementById('faceShapeResultsContainer');
const faceShapeNameDisplay = document.getElementById('faceShapeName');
const faceShapeDescriptionDisplay = document.getElementById('faceShapeDescription');


// ЭЛЕМЕНТЫ ДЛЯ ЗУМА И СКАЧИВАНИЯ
const zoomHint = document.getElementById('zoomHint');
const downloadImageButton = document.getElementById('downloadImageButton');
const imageZoomModal = document.getElementById('imageZoomModal');
const zoomedImage = document.getElementById('zoomedImage');
const closeZoomModalButton = document.getElementById('closeZoomModal');


const advicePageTitle = document.getElementById('advicePageTitle');
const adviceButtonsContainer = document.getElementById('adviceButtonsContainer');

const tipDetailPageTitle = document.getElementById('tipDetailPageTitle');
const tipDetailText = document.getElementById('tipDetailText');

// Данные для советов (могут быть загружены с бэкенда позже)
const adviceData = {
    mind: [
        { title: "Разум Совет 1", text: "Разум Совет 1 подразумевает сосредоточение на осознанности и медитации для улучшения ментального благополучия." },
        { title: "Разум Совет 2", text: "Разум Совет 2: Практикуйте позитивное мышление и ведите дневник благодарности для укрепления духа." },
        { title: "Разум Совет 3", text: "Разум Совет 3: Регулярное изучение нового и решение головоломок помогает поддерживать остроту ума." },
        { title: "Разум Совет 4", text: "Разум Совет 4: Достаточный сон и качественный отдых критически важны для восстановления когнитивных функций." },
    ],
    body: [
        { title: "Тело Совет 1", text: "Тело Совет 1 подразумевает сбалансированное питание, богатое фруктами, овощами и цельными злаками." },
        { title: "Тело Совет 2", text: "Тело Совет 2: Регулярные физические упражнения, такие как ходьба, бег или плавание, укрепляют сердечно-сосудистую систему." },
        { title: "Тело Совет 3", text: "Тело Совет 3: Питье достаточного количества воды в течение дня поддерживает гидратацию и общее состояние здоровья." },
        { title: "Тело Совет 4", text: "Тело Совет 4: Избегайте длительного сидения, делайте короткие перерывы для разминки." },
    ],
    face: [
        { title: "Лицо Совет 1", text: "Лицо Совет 1 подразумевает ежедневное очищение и увлажнение кожи для поддержания её здоровья и сияния." },
        { title: "Лицо Совет 2", text: "Лицо Совет 2: Защита кожи от солнца с помощью солнцезащитного крема предотвращает преждевременное старение и повреждения." },
        { title: "Лицо Совет 3", text: "Лицо Совет 3: Регулярный массаж лица может улучшить кровообращение и тонус кожи." },
        { title: "Лицо Совет 4", text: "Лицо Совет 4: Достаточное количество сна способствует регенерации клеток кожи и уменьшает отечность." },
    ],
    faq: [
        { title: "Что это за приложение?", text: "Это приложение для анализа лица, которое предоставляет персонализированные советы по улучшению вашего благополучия." },
        { title: "Как оно работает?", text: "Вы загружаете фотографию, наш ИИ анализирует её и предлагает рекомендации в различных категориях." },
        { title: "Безопасно ли это?", text: "Ваши фотографии обрабатываются анонимно и не сохраняются на сервере после обработки." },
        { title: "Могу ли я получить более подробные советы?", text: "Нажмите на любую категорию, чтобы увидеть список советов, а затем выберите конкретный совет для получения подробной информации." },
    ]
};

let currentCategory = '';
let processedImageUrl = "#";
let lastErrorProcessedImage = "#";


// --- Вспомогательная функция для отображения ошибки ---
function showErrorMessage(message) {
    errorMessageText.textContent = message;
    errorMessageContainer.classList.remove('hidden');
    console.error("Отображено сообщение об ошибке:", message);
}

// --- Вспомогательная функция для скрытия ошибки ---
function hideErrorMessage() {
    errorMessageText.textContent = '';
    errorMessageContainer.classList.add('hidden');
}

// --- Функции навигации ---
function showPage(pageElement) {
    hideErrorMessage();
    const pages = [mainPage, advicePage, tipDetailPage];
    pages.forEach(p => p.classList.add('hidden'));
    pageElement.classList.remove('hidden');
}

function goBackToMainPage() {
    showPage(mainPage);
    hideErrorMessage();

    if (processedImageUrl !== "#" && lastErrorProcessedImage === "#") {
        imagePreviewContainer.classList.remove('hidden');
        previewImage.classList.remove('hidden');
        previewImage.src = processedImageUrl;
        categoryButtonsContainer.classList.remove('hidden');
        symmetryResultsContainer.classList.remove('hidden');
        faceShapeResultsContainer.classList.remove('hidden');
        zoomHint.classList.remove('hidden');
        downloadImageButton.classList.remove('hidden');
    } else {
        imagePreviewContainer.classList.add('hidden');
        previewImage.classList.add('hidden');
        previewImage.src = "#";
        categoryButtonsContainer.classList.add('hidden');
        symmetryResultsContainer.classList.add('hidden');
        faceShapeResultsContainer.classList.add('hidden');
        zoomHint.classList.add('hidden');
        downloadImageButton.classList.add('hidden');
    }
    loadingIndicator.classList.add('hidden');
    loadingMessage.classList.add('hidden');
    lastErrorProcessedImage = "#";
}

function goBackToAdvicePage() {
    showPage(advicePage);
    if (currentCategory) {
        showAdviceList(currentCategory);
    }
}

// --- Обработчик загрузки изображения ---
imageUploadInput.addEventListener('change', async function(event) {
    console.log("Событие 'change' сработало.");
    const file = event.target.files[0];
    hideErrorMessage();

    imagePreviewContainer.classList.add('hidden');
    previewImage.classList.add('hidden');
    loadingIndicator.classList.add('hidden');
    loadingMessage.classList.add('hidden');
    categoryButtonsContainer.classList.add('hidden');
    symmetryResultsContainer.classList.add('hidden');
    faceShapeResultsContainer.classList.add('hidden');
    zoomHint.classList.add('hidden');
    downloadImageButton.classList.add('hidden');

    if (file) {
        console.log("Файл выбран:", file.name, "Тип:", file.type, "Размер:", file.size, "байт");
        // --- КЛИЕНТСКАЯ ВАЛИДАЦИЯ ---
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const maxSizeMB = 5;
        const maxSizeBytes = maxSizeMB * 1024 * 1024;

        if (!allowedTypes.includes(file.type)) {
            showErrorMessage(`Неподдерживаемый тип файла. Пожалуйста, загрузите изображение в формате JPG, PNG или GIF.`);
            event.target.value = '';
            resetMainPageStateAfterError();
            return;
        }

        if (file.size > maxSizeBytes) {
            showErrorMessage(`Файл слишком большой. Максимальный размер файла: ${maxSizeMB} MB.`);
            event.target.value = '';
            resetMainPageStateAfterError();
            return;
        }
        // --- КОНЕЦ КЛИЕНТСКОЙ ВАЛИДАЦИИ ---

        // Если валидация прошла, показываем спиннер и сообщение о загрузке
        imagePreviewContainer.classList.remove('hidden');
        loadingIndicator.classList.remove('hidden');
        loadingMessage.classList.remove('hidden');
        previewImage.classList.add('hidden');

        processedImageUrl = "#";
        lastErrorProcessedImage = "#";
        previewImage.src = "#";
        symmetryIndexDisplay.textContent = "Индекс симметрии: --%";
        symmetryDescriptionDisplay.textContent = "";
        faceShapeNameDisplay.textContent = "--";
        faceShapeDescriptionDisplay.textContent = "";


        // 2. Отправляем фото на бэкенд для обработки
        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('http://localhost:5000/process-image', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const result = await response.json();

                const imageUrl = `data:image/jpeg;base64,${result.processed_image}`;
                processedImageUrl = imageUrl;
                lastErrorProcessedImage = "#";
                previewImage.src = imageUrl;

                symmetryIndexDisplay.textContent = `Индекс симметрии: ${result.symmetry_index}%`;
                symmetryDescriptionDisplay.textContent = result.symmetry_description;

                // Отображаем форму лица
                if (result.face_shape) {
                    faceShapeNameDisplay.textContent = result.face_shape.shape_name;
                    faceShapeDescriptionDisplay.textContent = result.face_shape.description;
                    faceShapeResultsContainer.classList.remove('hidden');
                } else {
                    faceShapeNameDisplay.textContent = "Не определено";
                    faceShapeDescriptionDisplay.textContent = "Не удалось определить форму лица.";
                    faceShapeResultsContainer.classList.remove('hidden');
                }

                previewImage.classList.remove('hidden');
                loadingIndicator.classList.add('hidden');
                loadingMessage.classList.add('hidden');
                symmetryResultsContainer.classList.remove('hidden');
                categoryButtonsContainer.classList.remove('hidden');
                zoomHint.classList.remove('hidden');
                downloadImageButton.classList.remove('hidden');
            } else {
                const errorData = await response.json();
                console.error('Ошибка сервера:', errorData.error);
                showErrorMessage(`Ошибка: ${errorData.error}`);

                if (response.status === 422 && errorData.processed_image) {
                    const imageUrl = `data:image/jpeg;base64,${errorData.processed_image}`;
                    lastErrorProcessedImage = imageUrl;
                    processedImageUrl = "#";

                    previewImage.src = imageUrl;
                    previewImage.classList.remove('hidden');
                    imagePreviewContainer.classList.remove('hidden');

                    symmetryResultsContainer.classList.add('hidden');
                    faceShapeResultsContainer.classList.add('hidden');
                } else {
                    processedImageUrl = "#";
                    lastErrorProcessedImage = "#";
                    resetMainPageStateAfterError();
                }
                loadingIndicator.classList.add('hidden');
                loadingMessage.classList.add('hidden');
            }
        } catch (error) {
            console.error('Произошла ошибка сети или сервера:', error);
            showErrorMessage('Не удалось связаться с сервером. Пожалуйста, убедитесь, что бэкенд запущен, и попробуйте еще раз.');
            processedImageUrl = "#";
            lastErrorProcessedImage = "#";
            resetMainPageStateAfterError();
        }

    } else {
        console.log("Файл не выбран или отменен.");
        if (processedImageUrl !== "#") {
            goBackToMainPage();
        } else {
            resetMainPageState();
        }
    }
});

// Вспомогательная функция для полного сброса состояния главной страницы
function resetMainPageState() {
    processedImageUrl = "#";
    lastErrorProcessedImage = "#";
    previewImage.src = "#";
    previewImage.classList.add('hidden');
    loadingIndicator.classList.add('hidden');
    loadingMessage.classList.add('hidden');
    imagePreviewContainer.classList.add('hidden');
    symmetryResultsContainer.classList.add('hidden');
    faceShapeResultsContainer.classList.add('hidden');
    categoryButtonsContainer.classList.add('hidden');
    zoomHint.classList.add('hidden');
    downloadImageButton.classList.add('hidden');
    symmetryIndexDisplay.textContent = "Индекс симметрии: --%";
    symmetryDescriptionDisplay.textContent = "";
    faceShapeNameDisplay.textContent = "--";
    faceShapeDescriptionDisplay.textContent = "";
    hideErrorMessage();
}

// Вспомогательная функция для сброса состояния главной страницы ПОСЛЕ ОШИБКИ
function resetMainPageStateAfterError() {
    processedImageUrl = "#";
    // lastErrorProcessedImage НЕ сбрасывается здесь, чтобы его можно было использовать для восстановления
    previewImage.src = "#";
    previewImage.classList.add('hidden');
    loadingIndicator.classList.add('hidden');
    loadingMessage.classList.add('hidden');
    imagePreviewContainer.classList.add('hidden');
    symmetryResultsContainer.classList.add('hidden');
    faceShapeResultsContainer.classList.add('hidden');
    categoryButtonsContainer.classList.add('hidden');
    zoomHint.classList.add('hidden');
    downloadImageButton.classList.add('hidden');
    symmetryIndexDisplay.textContent = "Индекс симметрии: --%";
    symmetryDescriptionDisplay.textContent = "";
    faceShapeNameDisplay.textContent = "--";
    faceShapeDescriptionDisplay.textContent = "";
    // НЕ скрываем hideErrorMessage() здесь! Сообщение должно остаться
}


// --- Обработчики для Зума и Скачивания ---
previewImage.addEventListener('click', () => {
    if (processedImageUrl !== "#" && !previewImage.classList.contains('hidden')) {
        zoomedImage.src = processedImageUrl;
        imageZoomModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
});

// Закрытие модального окна по кнопке "X"
closeZoomModalButton.addEventListener('click', () => {
    imageZoomModal.classList.add('hidden');
    document.body.style.overflow = '';
});

// Закрытие модального окна по клику вне изображения (на затемненной области)
imageZoomModal.addEventListener('click', (event) => {
    if (event.target === imageZoomModal) {
        imageZoomModal.classList.add('hidden');
        document.body.style.overflow = '';
    }
});

// Закрытие модального окна при повторном нажатии на увеличенное изображение
zoomedImage.addEventListener('click', () => {
    imageZoomModal.classList.add('hidden');
    document.body.style.overflow = '';
});

// Скачивание изображения
downloadImageButton.addEventListener('click', () => {
    if (processedImageUrl !== "#") {
        const a = document.createElement('a');
        a.href = processedImageUrl;
        a.download = 'face_symmetry_analysis.jpg';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
});


// --- Обработчик кликов по кнопкам категорий (Разум, Тело, Лицо, ?) ---
categoryButtonsContainer.addEventListener('click', (event) => {
    const target = event.target;
    if (target.classList.contains('category-button')) {
        currentCategory = target.dataset.category;
        showAdviceList(currentCategory);
    }
});

function showAdviceList(category) {
    showPage(advicePage);
    // Капитализация первой буквы для заголовка
    advicePageTitle.textContent = category.charAt(0).toUpperCase() + category.slice(1) + ' Советы';
    adviceButtonsContainer.innerHTML = '';

    const advices = adviceData[category];
    if (advices) {
        advices.forEach((advice, index) => {
            const button = document.createElement('button');
            button.classList.add('advice-button');
            button.textContent = advice.title;
            button.dataset.index = index;
            button.addEventListener('click', () => showTipDetail(category, index));
            adviceButtonsContainer.appendChild(button);
        });
    }
}

// --- Отображение детализированного совета ---
function showTipDetail(category, index) {
    showPage(tipDetailPage);
    const advice = adviceData[category][index];
    tipDetailPageTitle.textContent = advice.title;
    tipDetailText.textContent = advice.text;
}

// Инициализация: убесимся, что при загрузке страницы видна только основная страница
document.addEventListener('DOMContentLoaded', () => {
    mainPage.classList.remove('hidden');
    advicePage.classList.add('hidden');
    tipDetailPage.classList.add('hidden');
    resetMainPageState();
});