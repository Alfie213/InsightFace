// --- Получаем ссылки на элементы DOM ---
const mainPage = document.getElementById('mainPage');
const advicePage = document.getElementById('advicePage');
const tipDetailPage = document.getElementById('tipDetailPage');

const imageUploadInput = document.getElementById('imageUpload');

// --- Элементы для блока анализа симметрии ---
const symmetryAnalysisBlock = document.getElementById('symmetryAnalysisBlock');
const symmetryImageContainer = document.getElementById('symmetryImageContainer');
const symmetryImagePreview = document.getElementById('symmetryImagePreview');
const symmetryLoadingIndicator = document.getElementById('symmetryLoadingIndicator');
const symmetryLoadingMessage = document.getElementById('symmetryLoadingMessage');
const symmetryZoomHint = document.getElementById('symmetryZoomHint');
const downloadSymmetryImageButton = document.getElementById('downloadSymmetryImageButton');
const symmetryResultsContainer = document.getElementById('symmetryResultsContainer'); // Текстовый блок
const symmetryIndexDisplay = document.getElementById('symmetryIndex');
const symmetryDescriptionDisplay = document.getElementById('symmetryDescription');

// --- Элементы для блока анализа формы лица ---
const faceShapeAnalysisBlock = document.getElementById('faceShapeAnalysisBlock');
const faceShapeImageContainer = document.getElementById('faceShapeImageContainer');
const faceShapeImagePreview = document.getElementById('faceShapeImagePreview');
const faceShapeLoadingIndicator = document.getElementById('faceShapeLoadingIndicator');
const faceShapeLoadingMessage = document.getElementById('faceShapeLoadingMessage');
const faceShapeZoomHint = document.getElementById('faceShapeZoomHint');
const downloadFaceShapeImageButton = document.getElementById('downloadFaceShapeImageButton');
const faceShapeResultsContainer = document.getElementById('faceShapeResultsContainer'); // Текстовый блок
const faceShapeNameDisplay = document.getElementById('faceShapeNameDisplay');
const faceShapeDescriptionDisplay = document.getElementById('faceShapeDescriptionDisplay');

// --- НОВЫЕ Элементы для вкладок анализа ---
const analysisTabsContainer = document.getElementById('analysisTabs');
const tabSymmetry = document.getElementById('tabSymmetry');
const tabFaceShape = document.getElementById('tabFaceShape');

const categoryButtonsContainer = document.getElementById('categoryButtonsContainer');

// --- ЭЛЕМЕНТЫ ДЛЯ СООБЩЕНИЙ ОБ ОШИБКАХ ---
const errorMessageContainer = document.getElementById('errorMessageContainer');
const errorMessageText = document.getElementById('errorMessageText');

// --- ЭЛЕМЕНТЫ МОДАЛЬНОГО ОКНА ЗУМА ---
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
let lastSuccessfulSymmetryImageUrl = "#";
let lastSuccessfulFaceShapeImageUrl = "#";
let lastErrorOriginalImageUrl = "#";

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

    // Логика отображения блоков анализа после возвращения на главную страницу
    // Теперь она должна учитывать, что есть вкладки
    if (lastSuccessfulSymmetryImageUrl !== "#") {
        analysisTabsContainer.classList.remove('hidden'); // Показываем вкладки
        // При возвращении на главную, по умолчанию показываем вкладку симметрии
        switchAnalysisTab('symmetry');

        // Убедимся, что все элементы внутри активной вкладки видны
        symmetryImagePreview.src = lastSuccessfulSymmetryImageUrl;
        symmetryImagePreview.classList.remove('hidden');
        symmetryZoomHint.classList.remove('hidden');
        downloadSymmetryImageButton.classList.remove('hidden');
        symmetryResultsContainer.classList.remove('hidden');

        // Элементы для FaceShape будут показаны только при активации вкладки "Форма"
        // Но при этом мы должны убедиться, что они заполнены, чтобы при переключении сразу отобразились
        faceShapeImagePreview.src = lastSuccessfulFaceShapeImageUrl;
        // faceShapeImagePreview.classList.remove('hidden'); // Скрыто по умолчанию
        // faceShapeZoomHint.classList.remove('hidden'); // Скрыто по умолчанию
        // downloadFaceShapeImageButton.classList.remove('hidden'); // Скрыто по умолчанию
        // faceShapeResultsContainer.classList.remove('hidden'); // Скрыто по умолчанию

        categoryButtonsContainer.classList.remove('hidden');

    } else if (lastErrorOriginalImageUrl !== "#") {
        // Если была ошибка, но есть оригинал, то показываем блоки анализа, но без результатов
        // и без кнопок вкладок
        analysisTabsContainer.classList.add('hidden'); // Скрываем вкладки, если была ошибка

        symmetryAnalysisBlock.classList.remove('hidden');
        symmetryImagePreview.src = lastErrorOriginalImageUrl;
        symmetryImagePreview.classList.remove('hidden');

        faceShapeAnalysisBlock.classList.remove('hidden');
        faceShapeImagePreview.src = lastErrorOriginalImageUrl;
        faceShapeImagePreview.classList.remove('hidden');

        // Все остальные элементы анализа и кнопок должны быть скрыты
        symmetryZoomHint.classList.add('hidden');
        downloadSymmetryImageButton.classList.add('hidden');
        faceShapeZoomHint.classList.add('hidden');
        downloadFaceShapeImageButton.classList.add('hidden');
        symmetryResultsContainer.classList.add('hidden');
        faceShapeResultsContainer.classList.add('hidden');
        categoryButtonsContainer.classList.add('hidden');
    } else {
        // Если вообще нет изображений
        analysisTabsContainer.classList.add('hidden'); // Скрываем вкладки
        symmetryAnalysisBlock.classList.add('hidden');
        faceShapeAnalysisBlock.classList.add('hidden');
        categoryButtonsContainer.classList.add('hidden');
    }

    // Убедимся, что индикаторы загрузки всегда скрыты
    symmetryLoadingIndicator.classList.add('hidden');
    symmetryLoadingMessage.classList.add('hidden');
    faceShapeLoadingIndicator.classList.add('hidden');
    faceShapeLoadingMessage.classList.add('hidden');

    lastErrorOriginalImageUrl = "#"; // Сбрасываем флаг ошибки
}

function goBackToAdvicePage() {
    showPage(advicePage);
    if (currentCategory) {
        showAdviceList(currentCategory);
    }
}

// --- НОВАЯ ФУНКЦИЯ: Переключение вкладок анализа ---
function switchAnalysisTab(activeTabId) {
    tabSymmetry.classList.remove('active');
    tabFaceShape.classList.remove('active');

    symmetryAnalysisBlock.classList.add('hidden');
    faceShapeAnalysisBlock.classList.add('hidden');

    if (activeTabId === 'symmetry') {
        tabSymmetry.classList.add('active');
        symmetryAnalysisBlock.classList.remove('hidden');
    } else if (activeTabId === 'faceShape') {
        tabFaceShape.classList.add('active');
        faceShapeAnalysisBlock.classList.remove('hidden');
    }
}

// --- Обработчики кликов по вкладкам ---
tabSymmetry.addEventListener('click', () => switchAnalysisTab('symmetry'));
tabFaceShape.addEventListener('click', () => switchAnalysisTab('faceShape'));


// --- Обработчик загрузки изображения ---
imageUploadInput.addEventListener('change', async function(event) {
    console.log("Событие 'change' сработало.");
    const file = event.target.files[0];
    hideErrorMessage();

    // Скрываем все элементы анализа и кнопок в самом начале, включая вкладки
    analysisTabsContainer.classList.add('hidden');
    symmetryAnalysisBlock.classList.add('hidden');
    faceShapeAnalysisBlock.classList.add('hidden');
    categoryButtonsContainer.classList.add('hidden');

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

        // Если валидация прошла, показываем контейнеры анализа и спиннеры/сообщения
        // (они будут скрыты при переключении вкладок, но мы их показываем для загрузки)
        symmetryAnalysisBlock.classList.remove('hidden');
        symmetryImagePreview.classList.add('hidden'); // Скрываем изображение, если было
        symmetryLoadingIndicator.classList.remove('hidden');
        symmetryLoadingMessage.classList.remove('hidden');

        faceShapeAnalysisBlock.classList.remove('hidden');
        faceShapeImagePreview.classList.add('hidden'); // Скрываем изображение, если было
        faceShapeLoadingIndicator.classList.remove('hidden');
        faceShapeLoadingMessage.classList.remove('hidden');

        // Скрываем подсказки, кнопки скачивания и текстовые блоки анализа
        symmetryZoomHint.classList.add('hidden');
        downloadSymmetryImageButton.classList.add('hidden');
        symmetryResultsContainer.classList.add('hidden');

        faceShapeZoomHint.classList.add('hidden');
        downloadFaceShapeImageButton.classList.add('hidden');
        faceShapeResultsContainer.classList.add('hidden');

        // Очищаем предыдущие данные
        lastSuccessfulSymmetryImageUrl = "#";
        lastSuccessfulFaceShapeImageUrl = "#";
        lastErrorOriginalImageUrl = "#";
        symmetryImagePreview.src = "#";
        faceShapeImagePreview.src = "#";
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

                // Обработанные изображения
                lastSuccessfulSymmetryImageUrl = `data:image/jpeg;base64,${result.symmetry_image}`;
                lastSuccessfulFaceShapeImageUrl = `data:image/jpeg;base64,${result.face_shape_image}`;

                // symmetryImagePreview.src = lastSuccessfulSymmetryImageUrl; // Заполняем, но показываем позже
                // faceShapeImagePreview.src = lastSuccessfulFaceShapeImageUrl; // Заполняем, но показываем позже

                // Результаты симметрии
                symmetryIndexDisplay.textContent = `Индекс симметрии: ${result.symmetry_data.index}%`;
                symmetryDescriptionDisplay.textContent = result.symmetry_data.description;

                // Отображаем форму лица
                if (result.face_shape) {
                    faceShapeNameDisplay.textContent = result.face_shape.name;
                    faceShapeDescriptionDisplay.textContent = result.face_shape.description;
                } else {
                    faceShapeNameDisplay.textContent = "Не определено";
                    faceShapeDescriptionDisplay.textContent = "Не удалось определить форму лица.";
                }

                // Скрываем спиннеры и сообщения
                symmetryLoadingIndicator.classList.add('hidden');
                symmetryLoadingMessage.classList.add('hidden');
                faceShapeLoadingIndicator.classList.add('hidden');
                faceShapeLoadingMessage.classList.add('hidden');

                // *** НОВАЯ ЛОГИКА ОТОБРАЖЕНИЯ ПОСЛЕ УСПЕШНОГО АНАЛИЗА ***
                // Показываем контейнер вкладок
                analysisTabsContainer.classList.remove('hidden');
                // Переключаемся на вкладку "Симметрия" по умолчанию
                switchAnalysisTab('symmetry');

                // Теперь, когда вкладка симметрии активна, мы показываем ее содержимое
                symmetryImagePreview.src = lastSuccessfulSymmetryImageUrl;
                symmetryImagePreview.classList.remove('hidden');
                symmetryResultsContainer.classList.remove('hidden');
                symmetryZoomHint.classList.remove('hidden');
                downloadSymmetryImageButton.classList.remove('hidden');

                // Для вкладки формы лица, ее содержимое будет показано только при ее активации
                faceShapeImagePreview.src = lastSuccessfulFaceShapeImageUrl; // Изображение загружено, но не показано

                // Показываем кнопки категорий
                categoryButtonsContainer.classList.remove('hidden');

            } else {
                const errorData = await response.json();
                console.error('Ошибка сервера:', errorData.error);
                showErrorMessage(`Ошибка: ${errorData.error}`);

                // В случае ошибки, показываем оригинальное изображение, если оно вернулось
                if (errorData.original_image) {
                    lastErrorOriginalImageUrl = `data:image/jpeg;base64,${errorData.original_image}`;

                    // Здесь мы не показываем вкладки, а сразу выводим блоки анализа с ошибкой
                    analysisTabsContainer.classList.add('hidden');

                    symmetryAnalysisBlock.classList.remove('hidden');
                    symmetryImagePreview.src = lastErrorOriginalImageUrl;
                    symmetryImagePreview.classList.remove('hidden');

                    faceShapeAnalysisBlock.classList.remove('hidden');
                    faceShapeImagePreview.src = lastErrorOriginalImageUrl;
                    faceShapeImagePreview.classList.remove('hidden');

                    // Все остальные элементы анализа и кнопок должны быть скрыты
                    symmetryZoomHint.classList.add('hidden');
                    downloadSymmetryImageButton.classList.add('hidden');
                    faceShapeZoomHint.classList.add('hidden');
                    downloadFaceShapeImageButton.classList.add('hidden');
                    symmetryResultsContainer.classList.add('hidden');
                    faceShapeResultsContainer.classList.add('hidden');
                    categoryButtonsContainer.classList.add('hidden');

                } else {
                    resetMainPageStateAfterError();
                }
                // Скрываем индикаторы, даже если есть оригинальное изображение
                symmetryLoadingIndicator.classList.add('hidden');
                symmetryLoadingMessage.classList.add('hidden');
                faceShapeLoadingIndicator.classList.add('hidden');
                faceShapeLoadingMessage.classList.add('hidden');
            }
        } catch (error) {
            console.error('Произошла ошибка сети или сервера:', error);
            showErrorMessage('Не удалось связаться с сервером. Пожалуйста, убедитесь, что бэкенд запущен, и попробуйте еще раз.');
            resetMainPageStateAfterError();
        }

    } else {
        console.log("Файл не выбран или отменен.");
        // Если было успешно обработанное фото, восстанавливаем его
        if (lastSuccessfulSymmetryImageUrl !== "#") {
            goBackToMainPage();
        } else {
            resetMainPageState();
        }
    }
});

// Вспомогательная функция для полного сброса состояния главной страницы
function resetMainPageState() {
    lastSuccessfulSymmetryImageUrl = "#";
    lastSuccessfulFaceShapeImageUrl = "#";
    lastErrorOriginalImageUrl = "#";

    analysisTabsContainer.classList.add('hidden'); // Скрываем вкладки
    symmetryAnalysisBlock.classList.add('hidden');
    faceShapeAnalysisBlock.classList.add('hidden');
    categoryButtonsContainer.classList.add('hidden');

    // Сброс всех внутренних элементов симметрии
    symmetryImagePreview.src = "#";
    symmetryImagePreview.classList.add('hidden');
    symmetryLoadingIndicator.classList.add('hidden');
    symmetryLoadingMessage.classList.add('hidden');
    symmetryZoomHint.classList.add('hidden');
    downloadSymmetryImageButton.classList.add('hidden');
    symmetryResultsContainer.classList.add('hidden');
    symmetryIndexDisplay.textContent = "Индекс симметрии: --%";
    symmetryDescriptionDisplay.textContent = "";

    // Сброс всех внутренних элементов формы лица
    faceShapeImagePreview.src = "#";
    faceShapeImagePreview.classList.add('hidden');
    faceShapeLoadingIndicator.classList.add('hidden');
    faceShapeLoadingMessage.classList.add('hidden');
    faceShapeZoomHint.classList.add('hidden');
    downloadFaceShapeImageButton.classList.add('hidden');
    faceShapeResultsContainer.classList.add('hidden');
    faceShapeNameDisplay.textContent = "--";
    faceShapeDescriptionDisplay.textContent = "";

    hideErrorMessage();
}

// Вспомогательная функция для сброса состояния главной страницы ПОСЛЕ ОШИБКИ
// Она НЕ скрывает контейнер errorMessageContainer
function resetMainPageStateAfterError() {
    lastSuccessfulSymmetryImageUrl = "#";
    lastSuccessfulFaceShapeImageUrl = "#";
    // lastErrorOriginalImageUrl НЕ сбрасывается здесь, если оно было получено

    analysisTabsContainer.classList.add('hidden'); // Скрываем вкладки
    symmetryAnalysisBlock.classList.add('hidden');
    faceShapeAnalysisBlock.classList.add('hidden');
    categoryButtonsContainer.classList.add('hidden');

    // Сброс всех внутренних элементов симметрии
    symmetryImagePreview.src = "#";
    symmetryImagePreview.classList.add('hidden');
    symmetryLoadingIndicator.classList.add('hidden');
    symmetryLoadingMessage.classList.add('hidden');
    symmetryZoomHint.classList.add('hidden');
    downloadSymmetryImageButton.classList.add('hidden');
    symmetryResultsContainer.classList.add('hidden');
    symmetryIndexDisplay.textContent = "Индекс симметрии: --%";
    symmetryDescriptionDisplay.textContent = "";

    // Сброс всех внутренних элементов формы лица
    faceShapeImagePreview.src = "#";
    faceShapeImagePreview.classList.add('hidden');
    faceShapeLoadingIndicator.classList.add('hidden');
    faceShapeLoadingMessage.classList.add('hidden');
    faceShapeZoomHint.classList.add('hidden');
    downloadFaceShapeImageButton.classList.add('hidden');
    faceShapeResultsContainer.classList.add('hidden');
    faceShapeNameDisplay.textContent = "--";
    faceShapeDescriptionDisplay.textContent = "";

    // НЕ скрываем hideErrorMessage() здесь! Сообщение должно остаться
}


// --- Обработчики для Зума (с учетом двух изображений) ---
symmetryImagePreview.addEventListener('click', () => {
    // Проверяем, активна ли вкладка симметрии
    if (tabSymmetry.classList.contains('active') && lastSuccessfulSymmetryImageUrl !== "#" && !symmetryImagePreview.classList.contains('hidden')) {
        zoomedImage.src = lastSuccessfulSymmetryImageUrl;
        imageZoomModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    } else if (tabSymmetry.classList.contains('active') && lastErrorOriginalImageUrl !== "#" && !symmetryImagePreview.classList.contains('hidden')) {
        zoomedImage.src = lastErrorOriginalImageUrl;
        imageZoomModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
});

faceShapeImagePreview.addEventListener('click', () => {
    // Проверяем, активна ли вкладка формы лица
    if (tabFaceShape.classList.contains('active') && lastSuccessfulFaceShapeImageUrl !== "#" && !faceShapeImagePreview.classList.contains('hidden')) {
        zoomedImage.src = lastSuccessfulFaceShapeImageUrl;
        imageZoomModal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    } else if (tabFaceShape.classList.contains('active') && lastErrorOriginalImageUrl !== "#" && !faceShapeImagePreview.classList.contains('hidden')) {
        zoomedImage.src = lastErrorOriginalImageUrl;
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

// Скачивание изображения симметрии
downloadSymmetryImageButton.addEventListener('click', () => {
    if (lastSuccessfulSymmetryImageUrl !== "#") {
        const a = document.createElement('a');
        a.href = lastSuccessfulSymmetryImageUrl;
        a.download = 'face_symmetry_analysis.jpg';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } else if (lastErrorOriginalImageUrl !== "#") {
        const a = document.createElement('a');
        a.href = lastErrorOriginalImageUrl;
        a.download = 'original_image_symmetry_error.jpg'; // Имя файла, если это оригинал из ошибки
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
});

// Скачивание изображения формы лица
downloadFaceShapeImageButton.addEventListener('click', () => {
    if (lastSuccessfulFaceShapeImageUrl !== "#") {
        const a = document.createElement('a');
        a.href = lastSuccessfulFaceShapeImageUrl;
        a.download = 'face_shape_analysis.jpg';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } else if (lastErrorOriginalImageUrl !== "#") {
        const a = document.createElement('a');
        a.href = lastErrorOriginalImageUrl;
        a.download = 'original_image_shape_error.jpg'; // Имя файла, если это оригинал из ошибки
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
    resetMainPageState(); // Сбрасываем все состояния, включая скрытие вкладок
});