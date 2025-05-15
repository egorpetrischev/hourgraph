<!-- SchedulePage.vue -->
<template>
  <div class="schedule-container">
    <div class="header-actions">
      <h1 class="page-title">Расписание</h1>
      <div class="date-selector">
        <button type="button" class="nav-week-btn" @click="changeWeek(-1)">
          &laquo; Предыдущая неделя
        </button>
        <div class="date-range">{{ formatDateRange(startWeek, endWeek) }}</div>
        <button type="button" class="nav-week-btn" @click="changeWeek(1)">
          Следующая неделя &raquo;
        </button>
          
        <button type="button" class="nav-week-btn" @click="goToToday">
          Сегодня
        </button>

        <input
          type="date"
          class="nav-week-date-picker"
          :value="selectedDate"
          @change="onDatePicked"
        />
      </div>
      <button type="button" class="add-lesson-btn" @click="openAddModal()">Добавить занятие</button>
    </div>

    <!-- Навигация для мобильных устройств -->
    <div class="weekday-navigation mobile-only">
      <button
        type="button"
        class="nav-arrow"
        @click="navigateDay(-1)"
        :disabled="currentDayIndex === 0"
      >
        &#8592;
      </button>
      <span class="current-day">{{ weekdayNames[currentDayIndex] }} {{ formatDayDate(getDayDate(currentDayIndex)) }}</span>
      <button
        type="button"
        class="nav-arrow"
        @click="navigateDay(1)"
        :disabled="currentDayIndex === 6"
      >
        &#8594;
      </button>
    </div>

    <div class="week-scroll-wrapper">
      <button
        class="scroll-nav left"
        @click="scrollWeek(-300)"
        :disabled="scrollProgress === 0"
      ></button>

      <div class="week-scroll-container" ref="weekScrollContainer">
        <!-- Основное представление расписания -->
        <div class="schedule-grid">
          <div
            v-for="(day, index) in weekdayColumns"
            :key="day.code"
            class="weekday-column"
            :class="{ 'active-day': index === currentDayIndex && currentDayIndex !== -1, 'mobile-active-day': isMobileView && (index === initialDayIndex && initialDayIndex !== -1) }"
          >
            <div class="weekday-header">
              {{ day.name }} {{ formatDayDate(getDayDate(index)) }}
            </div>
            <div class="lessons-container">
              <div v-if="loading" class="loading-state">
                <p>Загрузка занятий...</p>
              </div>
              <div v-else-if="getFilteredLessons(day.code, getDayDate(index)).length === 0" class="empty-state">
                <p>Нет занятий</p>
              </div>
              <div v-else class="lessons-list">
                <div
                  v-for="lesson in getFilteredLessons(day.code, getDayDate(index))"
                  :key="lesson.id + (lesson.isTemplate ? 'T' : 'L')"
                  class="lesson-card"
                  :class="{
                    'lesson-completed': lesson.status === 'CO',
                    'lesson-canceled': lesson.status === 'CA',
                    'lesson-template': lesson.isTemplate
                  }"
                >
                  <div class="lesson-time">
                    {{ formatTime(lesson.start_time) }} - {{ formatTime(lesson.end_time) }}
                    <span v-if="lesson.isTemplate" class="template-badge">Шаблон</span>
                  </div>
                  <div class="lesson-info">
                    <span v-if="lesson.student_details">
                      {{ lesson.student_details.name }} {{ lesson.student_details.surname }}
                    </span>
                    <span v-else-if="lesson.student_group_details">
                      Группа: {{ lesson.student_group_details.name }}
                    </span>
                  </div>
                  <div class="lesson-actions">
                    <button type="button" class="details-btn" @click="openDetailsModal(lesson)">Подробнее</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <button
        class="scroll-nav right"
        @click="scrollWeek(300)"
        :disabled="scrollProgress === 100"
      ></button>
    </div>

    <!-- Модальное окно для добавления/редактирования занятия -->
    <div class="modal" v-if="showModal" @click.self="closeModal">
      <div class="modal-overlay" @click.stop="closeModal"></div>
      <div class="modal-content">
        <h2>{{ isEditing ? 'Редактирование занятия' : 'Добавление нового занятия' }}</h2>
        <form @submit.prevent="saveLesson">
          <div class="form-group">
            <label for="date">Дата*</label>
            <input
              type="date"
              id="date"
              v-model="currentLesson.date"
              required
              :min="startWeek"
              :max="endWeek"
            >
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="start_time">Время начала*</label>
              <input type="time" id="start_time" v-model="currentLesson.start_time" required>
            </div>
            <div class="form-group">
              <label for="end_time">Время конца*</label>
              <input type="time" id="end_time" v-model="currentLesson.end_time" required>
            </div>
          </div>

          <div class="form-group">
            <label for="lesson_type">Тип занятия*</label>
            <div class="toggle-container">
              <span :class="{ active: !isGroupLesson }">Индивидуальное</span>
              <label class="toggle-switch">
                <input type="checkbox" v-model="isGroupLesson">
                <span class="slider round"></span>
              </label>
              <span :class="{ active: isGroupLesson }">Групповое</span>
            </div>
          </div>

          <div class="form-group" v-if="!isGroupLesson">
            <label for="student">Студент*</label>
            <div v-if="loadingStudents" class="loading-state">
              <p>Загрузка студентов...</p>
            </div>
            <div v-else>
              <div class="search-select">
                <input
                  type="text"
                  v-model="studentSearchQuery"
                  placeholder="Поиск студента..."
                  class="search-input"
                >
                <div class="options-container">
                  <div v-if="filteredStudents.length === 0" class="empty-options">
                    <p>Студенты не найдены</p>
                  </div>
                  <div
                    v-for="student in filteredStudents"
                    :key="student.id"
                    class="option"
                    :class="{ selected: currentLesson.student === student.id }"
                    @click="selectStudent(student)"
                  >
                    {{ student.name }} {{ student.surname }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-group" v-if="isGroupLesson">
            <label for="group">Группа*</label>
            <div v-if="loadingGroups" class="loading-state">
              <p>Загрузка групп...</p>
            </div>
            <div v-else>
              <div class="search-select">
                <input
                  type="text"
                  v-model="groupSearchQuery"
                  placeholder="Поиск группы..."
                  class="search-input"
                >
                <div class="options-container">
                  <div v-if="filteredGroups.length === 0" class="empty-options">
                    <p>Группы не найдены</p>
                  </div>
                  <div
                    v-for="group in filteredGroups"
                    :key="group.id"
                    class="option"
                    :class="{ selected: currentLesson.student_group === group.id }"
                    @click="selectGroup(group)"
                  >
                    {{ group.name }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label for="comment">Комментарий</label>
            <textarea id="comment" v-model="currentLesson.comment" rows="3"></textarea>
          </div>

          <div v-if="timeConflictError" class="error-message">
            Указанное время пересекается с другим занятием в этот день либо Вы выбрали невозможный промежуток.
          </div>

          <div class="modal-actions">
            <div class="first-row">
              <button type="button" class="cancel-btn" @click="closeModal">Отмена</button>

              <div class="status-actions" v-if="isEditing && !currentLesson.isTemplate">
                <button
                  type="button"
                  class="status-btn cancel-lesson-btn"
                  @click="setLessonStatus('CA')"
                  :disabled="currentLesson.status === 'CA'"
                >
                  Отменить занятие
                </button>
                <button
                  type="button"
                  class="status-btn complete-lesson-btn"
                  @click="setLessonStatus('CO')"
                  :disabled="currentLesson.status === 'CO'"
                >
                  Завершить
                </button>
              </div>
            </div>

            <div class="second-row primary-actions">
              <button
                type="button"
                class="delete-btn"
                v-if="isEditing && !currentLesson.isTemplate"
                @click="confirmDelete(currentLesson)"
              >
                Удалить
              </button>
              <button
                type="submit"
                class="save-btn"
                :disabled="!isFormValid || timeConflictError"
              >
                Сохранить
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно для подтверждения удаления -->
    <div class="modal" v-if="showDeleteConfirm" @click.self="cancelDelete">
      <div class="modal-overlay" @click.stop="cancelDelete"></div>
      <div class="modal-content confirm-modal">
        <h2>Подтверждение удаления</h2>
        <p>Вы действительно хотите удалить это занятие?</p>
        <div class="modal-actions">
          <button type="button" class="cancel-btn" @click="cancelDelete">Отмена</button>
          <button type="button" class="delete-confirm-btn" @click="deleteLesson">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, watch, onUnmounted, nextTick} from 'vue';
import axios from 'axios';

// Состояние загрузки
const loading = ref(true);
const loadingStudents = ref(false);
const loadingGroups = ref(false);

// Данные о неделе
const startWeek = ref('');
const endWeek = ref('');

// Списки данных
const templates = ref([]);
const lessons = ref([]);
const students = ref([]);
const groups = ref([]);

// Поиск студентов и групп
const studentSearchQuery = ref('');
const groupSearchQuery = ref('');

// Состояние модальных окон
const showModal = ref(false);
const showDeleteConfirm = ref(false);
const isEditing = ref(false);
const isGroupLesson = ref(false);
const timeConflictError = ref(false);

// Текущая мобильная навигация
const initialDayIndex = ref(-1); // используется для отображения активного дня (если это текущая неделя)
const mobileDayIndex = ref(0);   // используется только в мобильной навигации

const currentDayIndex = computed(() => isMobileView.value ? mobileDayIndex.value : initialDayIndex.value);
const isMobileView = ref(window.innerWidth <= 768);

const updateIsMobileView = () => {
  isMobileView.value = window.innerWidth <= 768;
};

// Отслеживание прогресса скролла
const weekScrollContainer = ref(null);
const scrollProgress = ref(0);

const scrollToCurrentDay = () => {
  if (isMobileView.value || initialDayIndex.value === -1) return;

  nextTick(() => {
    if (weekScrollContainer.value) {
      const container = weekScrollContainer.value;
      const dayColumn = container.querySelectorAll('.weekday-column')[initialDayIndex.value];

      if (dayColumn) {
        // Вычисляем позицию для центрирования
        const containerWidth = container.clientWidth;
        const dayLeft = dayColumn.offsetLeft;
        const dayWidth = dayColumn.offsetWidth;
        const scrollTo = dayLeft - (containerWidth / 2) + (dayWidth / 2);

        container.scrollTo({
          left: scrollTo,
          behavior: 'smooth'
        });
      }
    }
  });
};

// Текущее занятие для редактирования/удаления
const currentLesson = ref({
  id: null,
  student: null,
  student_group: null,
  start_time: '',
  end_time: '',
  date: '',
  status: 'TB',
  comment: '',
  isTemplate: false
});

// Занятие для удаления
const lessonToDelete = ref(null);

// Константы для дней недели
const weekdayColumns = [
  { name: 'Понедельник', code: 'MO' },
  { name: 'Вторник', code: 'TU' },
  { name: 'Среда', code: 'WE' },
  { name: 'Четверг', code: 'TH' },
  { name: 'Пятница', code: 'FR' },
  { name: 'Суббота', code: 'SA' },
  { name: 'Воскресенье', code: 'SU' }
];

const weekdayNames = weekdayColumns.map(day => day.name);

// Получение дат для дней недели
const getDayDate = (dayIndex) => {
  if (!startWeek.value) return '';

  const monday = new Date(startWeek.value);
  const dayDate = new Date(monday);
  dayDate.setDate(monday.getDate() + dayIndex);

  return dayDate.toISOString().split('T')[0];
};

// Форматирование даты дня недели (ДД.ММ)
const formatDayDate = (dateString) => {
  if (!dateString) return '';

  const [year, month, day] = dateString.split('-');
  return `${day}.${month}.${year}`;
};

// Форматирование диапазона дат (ДД.ММ.ГГГГ - ДД.ММ.ГГГГ)
const formatDateRange = (startDate, endDate) => {
  if (!startDate || !endDate) return '';

  const formatDate = (dateStr) => {
    const [year, month, day] = dateStr.split('-');
    return `${day}.${month}.${year}`;
  };

  return `${formatDate(startDate)} - ${formatDate(endDate)}`;
};

// Функция смены недели
const changeWeek = (direction) => {
  const currentMonday = new Date(startWeek.value);
  currentMonday.setDate(currentMonday.getDate() + (7 * direction));

  const newMondayStr = formatDate(currentMonday);

  const today = new Date();
  const todayDay = today.getDay();
  const mondayOffset = todayDay === 0 ? -6 : 1 - todayDay;
  const thisMonday = new Date(today);
  thisMonday.setDate(today.getDate() + mondayOffset);
  const thisMondayStr = formatDate(thisMonday);

  currentDayIndex.value = 0;

  if (newMondayStr === thisMondayStr) {
    fetchWeekSchedule(); // текущая неделя
  } else {
    fetchWeekSchedule(newMondayStr); // другая неделя
  }
};

const selectedDate = ref(new Date().toISOString().split('T')[0]);

// Кнопка "Сегодня"
const goToToday = () => {
  selectedDate.value = new Date().toISOString().split('T')[0];
  fetchWeekSchedule(); // Без аргумента — загрузит текущую неделю
};

const formatDate = (date) => {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// Календарь: выбираем дату
const onDatePicked = (event) => {
  const pickedDateStr = event.target.value;
  if (pickedDateStr) {
    selectedDate.value = pickedDateStr;

    const pickedDate = new Date(pickedDateStr);
    const today = new Date();

    const dayOfWeek = pickedDate.getDay(); // 0 (вс) – 6 (сб)
    const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
    const pickedMonday = new Date(pickedDate);
    pickedMonday.setDate(pickedDate.getDate() + mondayOffset);

    const todayDay = today.getDay();
    const todayMondayOffset = todayDay === 0 ? -6 : 1 - todayDay;
    const todayMonday = new Date(today);
    todayMonday.setDate(today.getDate() + todayMondayOffset);

    const pickedMondayStr = formatDate(pickedMonday);
    const todayMondayStr = formatDate(todayMonday);

    if (pickedMondayStr === todayMondayStr) {
      fetchWeekSchedule();
    } else {
      fetchWeekSchedule(pickedMondayStr);
    }
  }
};

// Прокрутка контейнера с днями недели
const scrollWeek = (offset) => {
  if (weekScrollContainer.value) {
    weekScrollContainer.value.scrollBy({
      left: offset,
      behavior: 'smooth'
    });
  }
};

const updateScrollProgress = () => {
  if (weekScrollContainer.value) {
    const { scrollLeft, scrollWidth, clientWidth } = weekScrollContainer.value;
    const progress = (scrollLeft / (scrollWidth - clientWidth)) * 100;
    scrollProgress.value = Math.round(progress);
  }
};

// Навигация для мобильных устройств
const navigateDay = (direction) => {
  const newIndex = mobileDayIndex.value + direction;
  if (newIndex >= 0 && newIndex <= 6) {
    mobileDayIndex.value = newIndex;
  }
};

watch(isMobileView, (isMobile) => {
  if (isMobile) {
    mobileDayIndex.value = initialDayIndex.value !== -1 ? initialDayIndex.value : 0;
  }
});

// Валидация формы
const isFormValid = computed(() => {
  if (isGroupLesson.value) {
    return !!currentLesson.value.student_group &&
           !!currentLesson.value.start_time &&
           !!currentLesson.value.end_time &&
           !!currentLesson.value.date;
  } else {
    return !!currentLesson.value.student &&
           !!currentLesson.value.start_time &&
           !!currentLesson.value.end_time &&
           !!currentLesson.value.date;
  }
});

// Фильтрация студентов и групп
const filteredStudents = computed(() => {
  if (!studentSearchQuery.value) return students.value;

  const query = studentSearchQuery.value.toLowerCase();
  return students.value.filter(student =>
    student.name.toLowerCase().includes(query) ||
    (student.surname && student.surname.toLowerCase().includes(query))
  );
});

const filteredGroups = computed(() => {
  if (!groupSearchQuery.value) return groups.value;

  const query = groupSearchQuery.value.toLowerCase();
  return groups.value.filter(group =>
    group.name.toLowerCase().includes(query)
  );
});

// Получение всех занятий для конкретного дня
const getFilteredLessons = (weekday, date) => {
  if (!date) return [];

  // Сначала собираем обычные занятия на эту дату
  const dayLessons = lessons.value
    .filter(lesson =>
      lesson.date === date &&
      lesson.status !== 'DE'
    )
    .map(lesson => ({ ...lesson, isTemplate: false }));

  // Находим шаблонные занятия для этого дня недели,
  // которые не конфликтуют с реальными занятиями
  const dayTemplates = templates.value
    .filter(template => {
      const template_weekday = template.weekday;
      if (template_weekday !== weekday) return false;

      // Проверяем, есть ли "удаленный" урок с таким же временем и студентом/группой
      const hasDeletedMatch = lessons.value.some(lesson =>
        lesson.date === date &&
        lesson.status === 'DE' &&
        lesson.start_time === template.start_time &&
        lesson.end_time === template.end_time &&
        ((lesson.student && lesson.student === template.student) ||
         (lesson.student_group && lesson.student_group === template.student_group))
      );

      if (hasDeletedMatch) return false;

      // Проверяем, есть ли обычный урок с таким же временем и студентом/группой
      const hasRegularMatch = dayLessons.some(lesson =>
        lesson.start_time === template.start_time &&
        lesson.end_time === template.end_time &&
        ((lesson.student && lesson.student === template.student) ||
         (lesson.student_group && lesson.student_group === template.student_group))
      );

      return !hasRegularMatch;
    })
    .map(template => ({ ...template, isTemplate: true }));

  // Объединяем и сортируем по времени
  return [...dayLessons, ...dayTemplates]
    .sort((a, b) => a.start_time.localeCompare(b.start_time));
};

// Форматирование времени (HH:MM:SS -> HH:MM)
const formatTime = (time) => {
  if (!time) return '';
  return time.substring(0, 5);
};

// Получение данных с сервера
const fetchWeekSchedule = async (date = null) => {
  try {
    loading.value = true;
    const url = date
      ? `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/week/?date=${date}`
      : `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/week/`;

    const response = await axios.get(url, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    startWeek.value = response.data.start_week;
    endWeek.value = response.data.end_week;
    templates.value = response.data.templates;
    lessons.value = response.data.lessons;

    // Получаем текущую дату и день недели
    const today = new Date();
    const todayDate = today.toISOString().split('T')[0];
    const todayDayOfWeek = today.getDay(); // 0 (воскресенье) до 6 (суббота)

    // Преобразуем в наш формат (0-6, где 0 - понедельник)
    const calculatedDayIndex = todayDayOfWeek === 0 ? 6 : todayDayOfWeek - 1;

    // Проверяем, находится ли сегодняшняя дата в пределах загруженной недели
    const isCurrentWeek = todayDate >= startWeek.value && todayDate <= endWeek.value;


    if (isCurrentWeek) {
      initialDayIndex.value = calculatedDayIndex;
      if (isMobileView.value) mobileDayIndex.value = calculatedDayIndex;
    } else {
      initialDayIndex.value = -1;
      if (isMobileView.value) mobileDayIndex.value = 0;
    }

    // Обновляем прогресс скролла после загрузки данных
    setTimeout(() => {
      updateScrollProgress();
      if (!isMobileView.value && isCurrentWeek) {
          scrollToCurrentDay();
      }
    }, 100);

  } catch (error) {
    console.error('Ошибка при загрузке данных недели:', error);
  } finally {
    loading.value = false;
  }
};

const fetchStudents = async () => {
  try {
    loadingStudents.value = true;
    const response = await axios.get(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcards/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    students.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке студентов:', error);
  } finally {
    loadingStudents.value = false;
  }
};

const fetchGroups = async () => {
  try {
    loadingGroups.value = true;
    const response = await axios.get(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcardgroups/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    groups.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке групп:', error);
  } finally {
    loadingGroups.value = false;
  }
};

// Проверка конфликтов по времени
const checkTimeConflict = () => {
  const { date, start_time, end_time, id, isTemplate } = currentLesson.value;

  // Если дата, время начала или конца не заданы, выходим
  if (!date || !start_time || !end_time) return false;

  const startTime = new Date(`2000-01-01T${start_time}`);
  const endTime = new Date(`2000-01-01T${end_time}`);

  // Проверяем, что время конца после времени начала
  if (endTime <= startTime) return true;

  // Получаем все занятия на эту дату (включая шаблонные)
  const dayLessons = getFilteredLessons(
    weekdayColumns.find(day => getDayDate(weekdayColumns.indexOf(day)) === date)?.code,
    date
  );

  // Проверяем на пересечение с другими занятиями
  return dayLessons.some(lesson => {
    // Пропускаем текущее занятие при редактировании
    if (
      (isEditing.value && lesson.id === id && lesson.isTemplate === isTemplate) ||
      (lesson.id === currentLesson.value.templateId) ||
      lesson.status === 'CA' || lesson.status === 'DE'
    ) {
      return false;
    }

    const lessonStart = new Date(`2000-01-01T${lesson.start_time}`);
    const lessonEnd = new Date(`2000-01-01T${lesson.end_time}`);

    // Проверка на пересечение интервалов времени
    return (
      (startTime < lessonEnd && endTime > lessonStart) ||
      (lessonStart < endTime && lessonEnd > startTime)
    );
  });
};

// Обработчики модального окна
const openAddModal = async () => {
  isEditing.value = false;
  isGroupLesson.value = false;

  // Устанавливаем дату текущего дня (или первого дня недели, если текущий день вне недели)
  const todayDate = new Date().toISOString().split('T')[0];
  const isInCurrentWeek = todayDate >= startWeek.value && todayDate <= endWeek.value;

  currentLesson.value = {
    id: null,
    student: null,
    student_group: null,
    start_time: '',
    end_time: '',
    date: isInCurrentWeek ? todayDate : startWeek.value,
    status: 'TB',
    comment: '',
    isTemplate: false
  };

  timeConflictError.value = false;

  await Promise.all([fetchStudents(), fetchGroups()]);

  showModal.value = true;
};

const createTemplateSuppressionLesson = async (template, date) => {
  if (!template || !date) return;

  try {
    // Проверяем, есть ли уже такой DE-урок
    const exists = lessons.value.some(lesson =>
      lesson.status === 'DE' &&
      lesson.date === date &&
      lesson.start_time === template.start_time &&
      lesson.end_time === template.end_time &&
      ((lesson.student && lesson.student === template.student) ||
       (lesson.student_group && lesson.student_group === template.student_group))
    );

    if (exists) return;

    const deletedLesson = {
      student: template.student,
      student_group: template.student_group,
      start_time: template.start_time,
      end_time: template.end_time,
      date: date,
      status: 'DE',
      comment: '[auto-hidden template]'
    };

    await axios.post(
      `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/lessons/`,
      deletedLesson,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    );
  } catch (error) {
    console.error('Ошибка при создании скрывающего урока (DE):', error);
  }
};

const openDetailsModal = async (lesson) => {
  isEditing.value = true;
  // Если это шаблон, то превращаем его в обычный урок
  if (lesson.isTemplate) {
    const weekdayIndex = weekdayColumns.findIndex(day => day.code === lesson.weekday);

    currentLesson.value = {
      ...lesson,
      id: null,                            //  Сброс ID — создаётся новый урок
      date: getDayDate(weekdayIndex),     //  Устанавливаем дату текущей недели
      status: 'TB',
      isTemplate: false,                  //  Уже не шаблон
      templateId: lesson.id               //  Сохраняем ID исходного шаблона (для проверки конфликтов)
    };

    delete currentLesson.value.weekday;   //  Удаляем weekday, он не нужен для обычного урока
  } else {
    // Если обычный урок — просто копируем
    currentLesson.value = { ...lesson };
  }

  // Определяем тип: индивидуальное или групповое
  isGroupLesson.value = !!currentLesson.value.student_group;

  // Приводим время к формату HH:MM
  currentLesson.value.start_time = formatTime(currentLesson.value.start_time);
  currentLesson.value.end_time = formatTime(currentLesson.value.end_time);

  timeConflictError.value = false;

  await Promise.all([fetchStudents(), fetchGroups()]);

  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  timeConflictError.value = false;
};

// Обработчики выбора студента/группы
const selectStudent = (student) => {
  currentLesson.value.student = student.id;
  currentLesson.value.student_group = null;
};

const selectGroup = (group) => {
  currentLesson.value.student_group = group.id;
  currentLesson.value.student = null;
};

// Изменение статуса занятия
const setLessonStatus = async (status) => {
  if (currentLesson.value.isTemplate) return;

  currentLesson.value.status = status;
  await saveLesson();
};

// Сохранение занятия
const saveLesson = async () => {
  // Проверка на конфликты времени
  timeConflictError.value = checkTimeConflict();
  if (timeConflictError.value) return;

  // Формируем данные для отправки
  const lessonData = {
    ...currentLesson.value,
    // При групповом занятии обнуляем студента и наоборот
    student: isGroupLesson.value ? null : currentLesson.value.student,
    student_group: isGroupLesson.value ? currentLesson.value.student_group : null
  };

  // Удаляем поле isTemplate перед отправкой
  delete lessonData.isTemplate;
  delete lessonData.templateId;

  try {
      // Сначала — подавление шаблона, если это было редактирование шаблона
    if (currentLesson.value.templateId) {
      const template = templates.value.find(t => t.id === currentLesson.value.templateId);
      await createTemplateSuppressionLesson(template, currentLesson.value.date);
    }

    if (isEditing.value && lessonData.id) {
      // Обновление существующего занятия
      await axios.put(
        `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/lessons/${lessonData.id}/`,
        lessonData,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
    } else {
      // Добавление нового занятия
      await axios.post(
        `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/lessons/`,
        lessonData,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
    }

    // Обновляем список занятий
    await fetchWeekSchedule(startWeek.value);
    closeModal();
  } catch (error) {
    console.error('Ошибка при сохранении занятия:', error);
  }
};

// Обработчики удаления
const confirmDelete = (lesson) => {
  lessonToDelete.value = lesson;
  showDeleteConfirm.value = true;
};

const cancelDelete = () => {
  lessonToDelete.value = null;
  showDeleteConfirm.value = false;
};

const deleteLesson = async () => {
  try {
    // Если это действительное занятие с ID, отправляем запрос на удаление
    if (lessonToDelete.value && lessonToDelete.value.id) {
      await axios.delete(
        `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/lessons/${lessonToDelete.value.id}/`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      // Обновляем список занятий
      await fetchWeekSchedule(startWeek.value);
    }

    // Закрываем модальные окна
    cancelDelete();
    closeModal();
  } catch (error) {
    console.error('Ошибка при удалении занятия:', error);
  }
};

// Отслеживание изменений во времени для проверки конфликтов
watch(
  [
    () => currentLesson.value.date,
    () => currentLesson.value.start_time,
    () => currentLesson.value.end_time
  ],
  () => {
    timeConflictError.value = checkTimeConflict();
  }
);

// Отслеживание изменений в типе занятия (индивидуальное/групповое)
watch(isGroupLesson, (newValue) => {
  if (newValue) {
    currentLesson.value.student = null;
  } else {
    currentLesson.value.student_group = null;
  }
});

// Отслеживание скролла для обновления прогресса
const initScrollTracking = () => {
  if (weekScrollContainer.value) {
    weekScrollContainer.value.addEventListener('scroll', updateScrollProgress);
  }
};

const handleResize = () => {
    const wasMobile = isMobileView.value;
  // При изменении размера окна обновляем isMobileView
  isMobileView.value = window.innerWidth <= 768;

  // Если перешли из мобильного в десктоп и это текущая неделя
  if (wasMobile && !isMobileView.value && initialDayIndex.value !== -1) {
    scrollToCurrentDay();
  }
};

onMounted(async () => {
  // Загружаем расписание для текущей недели
  await fetchWeekSchedule();

  // Инициализируем отслеживание скролла
  initScrollTracking();

  // Добавляем обработчик изменения размера окна
  window.addEventListener('resize', handleResize);
  window.addEventListener('resize', updateIsMobileView);
  updateIsMobileView(); // чтобы установить актуальное значение сразу
});

onUnmounted(() => {
  // Удаляем обработчики событий при размонтировании компонента
  if (weekScrollContainer.value) {
    weekScrollContainer.value.removeEventListener('scroll', updateScrollProgress);
  }
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('resize', updateIsMobileView);
});
</script>

<style scoped>
.schedule-container {
  max-width: 100%;
  margin: 0 auto;
  padding: 1rem 2rem;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  color: #2D2D2D;
  margin: 0;
  font-size: 1.5rem;
}

.date-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.date-range {
  font-weight: 600;
  min-width: 180px;
  text-align: center;
}

.nav-week-btn {
  background-color: #F0EBFF;
  color: #6E3AFF;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-family: 'Manrope', sans-serif;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  -webkit-tap-highlight-color: rgba(0,0,0,0);
  user-select: none;
  touch-action: manipulation;
}

.nav-week-btn:hover {
  background-color: #E4D9FF;
}

.add-lesson-btn {
  background-color: #6E3AFF;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.75rem 1.5rem;
  font-family: 'Manrope', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  white-space: nowrap;
  -webkit-tap-highlight-color: rgba(0,0,0,0);
  user-select: none;
  touch-action: manipulation;
}

.add-lesson-btn:hover {
  background-color: #5D2DE0;
}

.add-lesson-btn:active {
  background-color: #502BC0;
}

.weekday-navigation {
  display: none;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  background-color: #F0EBFF;
  padding: 0.75rem;
  border-radius: 6px;
}

.nav-arrow {
  background-color: #6E3AFF;
  color: white;
  border: none;
  border-radius: 4px;
  width: 36px;
  height: 36px;
  font-size: 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.nav-arrow:disabled {
  background-color: #CCCCCC;
  cursor: not-allowed;
}

.current-day {
  font-weight: 600;
  font-size: 1rem;
}

.week-scroll-wrapper {
  position: relative;
  margin: 0 40px; /* Оставляем место для кнопок */
}

.week-scroll-container {
  width: 100%;
  overflow-x: auto;
  scroll-behavior: smooth; /* Плавный скролл */
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  padding-bottom: 16px;

  /* Скрываем стандартный скроллбар */
  &::-webkit-scrollbar {
    display: none; /* Chrome/Safari */
  }
}

.scroll-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  background: white;
  border: none;
  border-radius: 50%;
  box-shadow: 0 2px 12px rgba(110, 58, 255, 0.2);
  z-index: 2;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s;
  pointer-events: none;

  /* Иконка стрелки */
  &::before {
    content: '';
    width: 10px;
    height: 10px;
    border: 2px solid #6E3AFF;
    border-left: none;
    border-bottom: none;
  }
}

.week-scroll-wrapper:hover .scroll-nav {
  opacity: 1;
  pointer-events: auto;
}

.scroll-nav.left {
  left: -20px;
  &::before {
    transform: rotate(-135deg) translateX(-1px);
    margin-right: 2px;
  }
}

.scroll-nav.right {
  right: -20px;
  &::before {
    transform: rotate(45deg) translateX(-1px);
    margin-left: 2px;
  }
}

.scroll-nav:hover {
  background: #6E3AFF;
  &::before {
    border-color: white;
  }
}

.scroll-nav:active {
  transform: translateY(-50%) scale(0.95);
}

.scroll-nav:disabled {
  display: none;
}

.schedule-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(200px, 1fr));
  gap: 1rem;
  min-height: 500px;
  width: max-content;
  min-width: 100%;
}

/* Градиенты по краям для индикации скролла */
.week-scroll-container {
  mask-image: linear-gradient(
    to right,
    transparent,
    #000 20px,
    #000 calc(100% - 20px),
    transparent
  );
}

.weekday-column {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.weekday-column.active-day {
  border: 2px solid #6E3AFF;
}

/* Добавляем стиль для неактивного состояния */
.weekday-column:not(.active-day) {
  border: 2px solid transparent;
}

.weekday-header {
  padding: 1rem;
  font-weight: 600;
  background-color: #F0EBFF;
  border-radius: 8px 8px 0 0;
  text-align: center;
}

.lessons-container {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
  max-height: 60vh;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 1rem 0;
  color: #757575;
  font-size: 0.875rem;
}

.lessons-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.lesson-card {
  background-color: #F9F9F9;
  border-radius: 6px;
  padding: 1rem;
  font-size: 0.875rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}

.lesson-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.lesson-completed {
  border-left: 4px solid #35C759;
}

.lesson-canceled {
  border-left: 4px solid #FF3A6E;
  opacity: 0.7;
}

.lesson-template {
  border-left: 4px solid #6E3AFF;
  background-color: #F0EBFF;
}

.template-badge {
  background-color: #6E3AFF;
  color: white;
  border-radius: 4px;
  padding: 0.2rem 0.5rem;
  font-size: 0.7rem;
  margin-left: 0.5rem;
  font-weight: 500;
}

.lesson-time {
  font-weight: 600;
  color: #6E3AFF;
  margin-bottom: 0.5rem;
}

.lesson-info {
  margin-bottom: 0.5rem;
}

.lesson-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.details-btn {
  flex: 1;
  padding: 0.5rem;
  border-radius: 4px;
  font-family: 'Manrope', sans-serif;
  font-weight: 500;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: rgba(0,0,0,0);
  user-select: none;
  touch-action: manipulation;
  background-color: #F0EBFF;
  color: #6E3AFF;
  border: 1px solid #F0EBFF;
}

.details-btn:hover, .details-btn:active {
  background-color: #E4D9FF;
}

/* Стили для статусных кнопок */
.status-actions {
  display: flex;
  gap: 0.5rem;
}

.status-btn {
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-weight: 600;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: rgba(0,0,0,0);
  user-select: none;
  touch-action: manipulation;
}

.cancel-lesson-btn {
  background-color: transparent;
  color: #FF3A6E;
  border: 1px solid #FF3A6E;
}

.cancel-lesson-btn:hover, .cancel-lesson-btn:active {
  background-color: rgba(255, 58, 110, 0.08);
}

.cancel-lesson-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.complete-lesson-btn {
  background-color: transparent;
  color: #35C759;
  border: 1px solid #35C759;
}

.complete-lesson-btn:hover, .complete-lesson-btn:active {
  background-color: rgba(53, 199, 89, 0.08);
}

.complete-lesson-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.primary-actions {
  display: flex;
  gap: 0.5rem;
}

.delete-btn {
  background-color: transparent;
  color: #FF3A6E;
  border: 1px solid #FF3A6E;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.delete-btn:hover, .delete-btn:active {
  background-color: rgba(255, 58, 110, 0.08);
}

/* Модальное окно */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1001;
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #2D2D2D;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2D2D2D;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-size: 0.875rem;
}

.toggle-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.toggle-container span {
  color: #757575;
}

.toggle-container span.active {
  color: #6E3AFF;
  font-weight: 500;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 30px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #E0E0E0;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 22px;
  width: 22px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}

input:checked + .slider {
  background-color: #6E3AFF;
}

input:focus + .slider {
  box-shadow: 0 0 1px #6E3AFF;
}

input:checked + .slider:before {
  transform: translateX(30px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

.search-select {
  position: relative;
}

.search-input {
  margin-bottom: 0.5rem;
}

.options-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
}

.option {
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #F5F5F5;
}

.option:last-child {
  border-bottom: none;
}

.option:hover {
  background-color: #F0EBFF;
}

.option.selected {
  background-color: #F0EBFF;
  color: #6E3AFF;
  font-weight: 500;
}

.empty-options {
  text-align: center;
  padding: 1rem;
  color: #757575;
  font-style: italic;
  font-size: 0.875rem;
}

.error-message {
  color: #FF3A6E;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 2rem;
}

.first-row,
.second-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: space-between;
}

.first-row > .cancel-btn {
  flex: 1 1 auto;
}

.status-actions {
  display: flex;
  gap: 0.5rem;
  flex: 2 1 auto;
  justify-content: flex-end;
}

.primary-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.save-btn, .cancel-btn, .delete-confirm-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  -webkit-tap-highlight-color: rgba(0,0,0,0);
  user-select: none;
  touch-action: manipulation;
}

.save-btn {
  background-color: #6E3AFF;
  color: white;
  border: none;
}

.save-btn:hover, .save-btn:active {
  background-color: #5D2DE0;
}

.save-btn:disabled {
  background-color: #CCCCCC;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #F5F5F5;
  color: #757575;
  border: none;
}

.cancel-btn:hover, .cancel-btn:active {
  background-color: #E0E0E0;
}

.delete-confirm-btn {
  background-color: #FF3A6E;
  color: white;
  border: none;
}

.delete-confirm-btn:hover, .delete-confirm-btn:active {
  background-color: #E02E5A;
}

.confirm-modal {
  max-width: 400px;
}

.nav-week-date-picker {
  background-color: #F0EBFF;
  color: #6E3AFF;
  border: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-family: 'Manrope', sans-serif;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
}

/* Медиа-запросы для мобильных устройств */
@media (max-width: 768px) {
  /* Скрываем кнопки прокрутки */
  .scroll-nav.left,
  .scroll-nav.right {
    display: none !important;
  }

  /* Убираем горизонтальный скролл */
  .week-scroll-container {
    overflow-x: hidden !important;
    mask-image: none !important;
  }

  /* Корректируем отступы */
  .week-scroll-wrapper {
    margin: 0 !important;
  }

  /* Для мобильной навигации по дням */
  .schedule-grid {
    display: block;
    width: 100%;
  }

  /* Скрываем дублирующий заголовок в колонке */
  .weekday-column .weekday-header {
    display: none;
  }

 .weekday-column {
    display: none;
    border: none;
  }

  .weekday-column.active-day {
    display: flex;
    border: 2px solid transparent;
  }

  .weekday-column.mobile-active-day {
      border: 2px solid #6E3AFF;
  }

  .weekday-navigation.mobile-only {
    display: flex;
  }

  .header-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .date-selector {
    width: 100%;
    justify-content: space-between;
  }

  .date-range {
    font-size: 0.875rem;
  }

  .nav-week-btn {
    font-size: 0.75rem;
    padding: 0.5rem 0.75rem;
  }

  .add-lesson-btn {
    width: 100%;
  }

  .mobile-only {
    display: flex !important;
  }

  .modal-content {
    width: 90%;
    margin: 0 auto;
    padding: 1.25rem;
    max-height: 80vh;
  }

  .form-row {
    flex-direction: column;
    gap: 1.25rem;
  }

  .modal-actions {
    flex-direction: column;
  }

  .modal-actions button {
    width: 100%;
  }

  .status-actions {
    width: 100%;
  }

  .primary-actions {
    width: 100%;
  }
}
</style>