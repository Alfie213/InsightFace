// Получаем ссылки на элементы DOM
const mainPage = document.getElementById('mainPage');
const advicePage = document.getElementById('advicePage');
const tipDetailPage = document.getElementById('tipDetailPage');

const imageUploadInput = document.getElementById('imageUpload');
const imagePreviewContainer = document.getElementById('imagePreviewContainer');
const previewImage = document.getElementById('previewImage');
const loadingIndicator = document.getElementById('loadingIndicator');
const categoryButtonsContainer = document.getElementById('categoryButtonsContainer');

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

let currentCategory = ''; // Для отслеживания текущей категории советов
let processedImageUrl = "#"; // Новая переменная для хранения URL обработанного изображения

// --- Функции навигации ---
function showPage(pageElement) {
    const pages = [mainPage, advicePage, tipDetailPage];
    pages.forEach(p => p.classList.add('hidden'));
    pageElement.classList.remove('hidden');
}

function goBackToMainPage() {
    showPage(mainPage);

    // Если есть обработанное изображение, показываем контейнер предпросмотра
    if (processedImageUrl !== "#") {
        imagePreviewContainer.classList.remove('hidden');
        previewImage.classList.remove('hidden');
        previewImage.src = processedImageUrl; // Восстанавливаем обработанное изображение
        categoryButtonsContainer.classList.remove('hidden'); // И кнопки категорий
    } else {
        // Если обработанного фото нет, скрываем предпросмотр и кнопки
        imagePreviewContainer.classList.add('hidden');
        previewImage.classList.add('hidden');
        previewImage.src = "#";
        categoryButtonsContainer.classList.add('hidden');
    }
    loadingIndicator.classList.add('hidden'); // Убедимся, что спиннер скрыт
}

function goBackToAdvicePage() {
    showPage(advicePage);
    // Восстанавливаем список советов для текущей категории
    if (currentCategory) {
        showAdviceList(currentCategory);
    }
}

// --- Обработчик загрузки изображения ---
imageUploadInput.addEventListener('change', async function(event) {
    const file = event.target.files[0];

    if (file) {
        // 1. Показываем контейнер предпросмотра
        imagePreviewContainer.classList.remove('hidden');
        // 2. Скрываем изображение, показываем спиннер загрузки
        previewImage.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        categoryButtonsContainer.classList.add('hidden'); // Скрываем кнопки категорий

        // Очищаем предыдущее обработанное изображение, пока идет загрузка нового
        processedImageUrl = "#";
        previewImage.src = "#";

        // 3. (Опционально) Отображаем загруженное фото на фронтенде сразу, если нужно
        // const reader = new FileReader();
        // reader.onload = function(e) {
        //     previewImage.src = e.target.result;
        //     previewImage.classList.remove('hidden');
        // };
        // reader.readAsDataURL(file);

        // 4. Отправляем фото на бэкенд для обработки
        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('http://localhost:5000/process-image', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const blob = await response.blob();
                const imageUrl = URL.createObjectURL(blob);

                processedImageUrl = imageUrl; // Сохраняем URL обработанного изображения
                previewImage.src = imageUrl; // Отображаем обработанное изображение

                previewImage.classList.remove('hidden'); // Показываем изображение
                loadingIndicator.classList.add('hidden'); // Скрываем спиннер
                categoryButtonsContainer.classList.remove('hidden'); // Показываем кнопки категорий
            } else {
                const errorData = await response.json();
                console.error('Ошибка при обработке изображения:', errorData.error);
                alert('Ошибка при обработке изображения: ' + errorData.error);
                // В случае ошибки скрываем все и возвращаемся к исходному состоянию
                processedImageUrl = "#"; // Сбрасываем URL
                previewImage.src = "#";
                previewImage.classList.add('hidden');
                loadingIndicator.classList.add('hidden');
                imagePreviewContainer.classList.add('hidden');
            }
        } catch (error) {
            console.error('Произошла ошибка сети или сервера:', error);
            alert('Не удалось связаться с сервером. Пожалуйста, убедитесь, что бэкенд запущен, и попробуйте еще раз.');
            // В случае ошибки скрываем все и возвращаемся к исходному состоянию
            processedImageUrl = "#"; // Сбрасываем URL
            previewImage.src = "#";
            previewImage.classList.add('hidden');
            loadingIndicator.classList.add('hidden');
            imagePreviewContainer.classList.add('hidden');
        }

    } else {
        // Если файл не выбран, скрываем предпросмотр, если нет обработанного фото
        if (processedImageUrl === "#") {
            imagePreviewContainer.classList.add('hidden');
            previewImage.src = "#";
        }
        previewImage.classList.add('hidden'); // Скрываем, если выбирали, но отменили
        loadingIndicator.classList.add('hidden');
        categoryButtonsContainer.classList.add('hidden'); // Скрываем кнопки, так как нет нового фото для обработки
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
    adviceButtonsContainer.innerHTML = ''; // Очищаем предыдущие кнопки

    const advices = adviceData[category];
    if (advices) {
        advices.forEach((advice, index) => {
            const button = document.createElement('button');
            button.classList.add('advice-button');
            button.textContent = advice.title;
            button.dataset.index = index; // Сохраняем индекс для доступа к данным
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

// Инициализация: убедимся, что при загрузке страницы видна только основная страница
document.addEventListener('DOMContentLoaded', () => {
    // При старте приложения нужно убедиться, что все скрыто
    // и показана только кнопка загрузки.
    mainPage.classList.remove('hidden'); // Показываем главную страницу
    advicePage.classList.add('hidden');
    tipDetailPage.classList.add('hidden');

    imagePreviewContainer.classList.add('hidden'); // Скрываем контейнер предпросмотра
    previewImage.classList.add('hidden'); // Скрываем изображение
    loadingIndicator.classList.add('hidden'); // Скрываем спиннер
    categoryButtonsContainer.classList.add('hidden'); // Скрываем кнопки категорий

    // Сбрасываем URL, чтобы при первой загрузке не было старого изображения
    processedImageUrl = "#";
});