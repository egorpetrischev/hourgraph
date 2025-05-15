<!-- TemplatePage.vue -->
<template>
  <div class="template-container">
    <div class="header-actions">
      <h1 class="page-title">Шаблон расписания</h1>
      <button type="button" class="add-template-btn" @click="openAddModal()">Добавить занятие</button>
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
      <span class="current-day">{{ weekdayNames[currentDayIndex] }}</span>
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
      
      <div 
        class="week-scroll-container" 
        ref="weekScrollContainer"
      >
        <!-- Основное представление шаблона -->
        <div class="template-grid">
          <div
            v-for="(day, index) in weekdayColumns"
            :key="day.code"
            class="weekday-column"
            :class="{ 'active-day': index === currentDayIndex }"
          >
            <div class="weekday-header">{{ day.name }}</div>
            <div class="lessons-container">
              <div v-if="loading" class="loading-state">
                <p>Загрузка занятий...</p>
              </div>
              <div v-else-if="getFilteredLessons(day.code).length === 0" class="empty-state">
                <p>Нет занятий</p>
              </div>
              <div v-else class="lessons-list">
                <div
                  v-for="lesson in getFilteredLessons(day.code)"
                  :key="lesson.id"
                  class="lesson-card"
                >
                  <div class="lesson-time">
                    {{ formatTime(lesson.start_time) }} - {{ formatTime(lesson.end_time) }}
                  </div>
                  <div class="lesson-info">
                    <span v-if="lesson.student_details">
                      {{ lesson.student_details.name }} {{ lesson.student_details.surname }}
                    </span>
                    <span v-else-if="lesson.student_group_details">
                      Группа: {{ lesson.student_group_details.name }}
                    </span>
                  </div>
                  <div class="lesson-comment" v-if="lesson.comment">
                    {{ lesson.comment }}
                  </div>
                  <div class="lesson-actions">
                    <button type="button" class="details-btn" @click="openDetailsModal(lesson)">Подробнее</button>
                    <button type="button" class="delete-btn" @click="confirmDelete(lesson)">Удалить</button>
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
            <label for="weekday">День недели*</label>
            <select id="weekday" v-model="currentLesson.weekday" required>
              <option v-for="day in weekdayColumns" :key="day.code" :value="day.code">
                {{ day.name }}
              </option>
            </select>
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
            <button type="button" class="cancel-btn" @click="closeModal">Отмена</button>
            <button
              type="submit"
              class="save-btn"
              :disabled="!isFormValid || timeConflictError"
            >
              Сохранить
            </button>
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
import {ref, computed, onMounted, watch, onUnmounted} from 'vue';
import axios from 'axios';

// Состояние загрузки
const loading = ref(true);
const loadingStudents = ref(false);
const loadingGroups = ref(false);

// Список занятий
const lessons = ref([]);

// Список студентов и групп
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
const currentDayIndex = ref(0);

// Отслеживание прогресса скролла
const weekScrollContainer = ref(null);
const scrollProgress = ref(0);

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

onMounted(() => {
  if (weekScrollContainer.value) {
    weekScrollContainer.value.addEventListener('scroll', updateScrollProgress);
  }
});

onUnmounted(() => {
  if (weekScrollContainer.value) {
    weekScrollContainer.value.removeEventListener('scroll', updateScrollProgress);
  }
});

// Текущее занятие для редактирования/удаления
const currentLesson = ref({
  id: null,
  student: null,
  student_group: null,
  start_time: '',
  end_time: '',
  weekday: 'MO',
  comment: ''
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

// Валидация времени
const isFormValid = computed(() => {
  if (isGroupLesson.value) {
    return !!currentLesson.value.student_group &&
           !!currentLesson.value.start_time &&
           !!currentLesson.value.end_time &&
           !!currentLesson.value.weekday;
  } else {
    return !!currentLesson.value.student &&
           !!currentLesson.value.start_time &&
           !!currentLesson.value.end_time &&
           !!currentLesson.value.weekday;
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

// Получение данных с сервера
const fetchTemplates = async () => {
  try {
    loading.value = true;
    const response = await axios.get(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/lesson-templates/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    lessons.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке шаблонов занятий:', error);
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

// Фильтрация занятий по дню недели
const getFilteredLessons = (weekday) => {
  return lessons.value
    .filter(lesson => lesson.weekday === weekday)
    .sort((a, b) => a.start_time.localeCompare(b.start_time));
};

// Форматирование времени (HH:MM:SS -> HH:MM)
const formatTime = (time) => {
  if (!time) return '';
  return time.substring(0, 5);
};

// Навигация для мобильных устройств
const navigateDay = (direction) => {
  const newIndex = currentDayIndex.value + direction;
  if (newIndex >= 0 && newIndex <= 6) {
    currentDayIndex.value = newIndex;
  }
};

// Проверка конфликтов по времени
const checkTimeConflict = () => {
  const { weekday, start_time, end_time, id } = currentLesson.value;

  // Если время начала или конца не заданы, выходим
  if (!start_time || !end_time) return false;

  const startTime = new Date(`2000-01-01T${start_time}`);
  const endTime = new Date(`2000-01-01T${end_time}`);

  // Проверяем, что время конца после времени начала
  if (endTime <= startTime) return true;

  // Проверяем на пересечение с другими занятиями в тот же день
  return lessons.value.some(lesson => {
    // Пропускаем текущее занятие при редактировании
    if (isEditing.value && lesson.id === id) return false;

    // Проверяем только занятия того же дня
    if (lesson.weekday !== weekday) return false;

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
  currentLesson.value = {
    id: null,
    student: null,
    student_group: null,
    start_time: '',
    end_time: '',
    weekday: 'MO',
    comment: ''
  };
  timeConflictError.value = false;

  await Promise.all([fetchStudents(), fetchGroups()]);

  showModal.value = true;
};

const openDetailsModal = async (lesson) => {
  isEditing.value = true;
  // Копируем занятие в текущее
  currentLesson.value = { ...lesson };

  // Определяем тип занятия (индивидуальное/групповое)
  isGroupLesson.value = !!lesson.student_group;

  // Корректируем формат времени для input type="time"
  currentLesson.value.start_time = formatTime(lesson.start_time);
  currentLesson.value.end_time = formatTime(lesson.end_time);

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

  try {
    if (isEditing.value) {
      // Обновление существующего занятия
      await axios.put(
        `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/lesson-templates/${lessonData.id}/`,
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
        `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/lesson-templates/`,
        lessonData,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
    }

    // Обновляем список занятий
    await fetchTemplates();
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
    await axios.delete(
      `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/lesson-templates/${lessonToDelete.value.id}/`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    );

    // Обновляем список занятий
    await fetchTemplates();
    cancelDelete();
  } catch (error) {
    console.error('Ошибка при удалении занятия:', error);
  }
};

// Отслеживание изменений времени для проверки конфликтов
watch(
  () => [currentLesson.value.start_time, currentLesson.value.end_time, currentLesson.value.weekday],
  () => {
    if (currentLesson.value.start_time && currentLesson.value.end_time && currentLesson.value.weekday) {
      timeConflictError.value = checkTimeConflict();
    }
  }
);

// Инициализация при загрузке компонента
onMounted(() => {
  fetchTemplates();
});
</script>

<style scoped>
.template-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 2rem;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  color: #2D2D2D;
  margin: 0;
  font-size: 1.5rem;
}

.add-template-btn {
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

.add-template-btn:hover {
  background-color: #5D2DE0;
}

.add-template-btn:active {
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
  opacity: 0.3;
  cursor: not-allowed;
  box-shadow: none;
}

.template-grid {
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
}

.lesson-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.lesson-time {
  font-weight: 600;
  color: #6E3AFF;
  margin-bottom: 0.5rem;
}

.lesson-info {
  margin-bottom: 0.5rem;
}

.lesson-comment {
  font-size: 0.75rem;
  color: #757575;
  margin-bottom: 0.75rem;
}

.lesson-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.details-btn, .delete-btn {
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
}

.details-btn {
  background-color: #F0EBFF;
  color: #6E3AFF;
  border: 1px solid #F0EBFF;
}

.details-btn:hover, .details-btn:active {
  background-color: #E4D9FF;
}

.delete-btn {
  background-color: transparent;
  color: #FF3A6E;
  border: 1px solid #FF3A6E;
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

.options-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  margin-top: 0.5rem;
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
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
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

/* Медиа-запросы для мобильных устройств */
@media (max-width: 768px) {
    /* Убираем кнопки прокрутки */
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
  .template-grid {
    display: block;
    width: 100%;
  }

  .weekday-column {
    display: none;
  }

  .weekday-column.active-day {
    display: flex;
  }


  .weekday-navigation.mobile-only {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    background-color: #F0EBFF;
    padding: 0.75rem;
    border-radius: 6px;
  }

  .weekday-navigation .weekday-header {
    display: none; /* Скрываем дублирующий заголовок */
  }

  .current-day {
    font-weight: 600;
    font-size: 1rem;
    min-width: 120px;
    text-align: center;
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

  /* Скрываем дублирующий заголовок в колонке */
  .weekday-column .weekday-header {
    display: none;
  }

    .template-container {
        padding: 1rem;
    }

    .header-actions {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }

    .template-grid {
        display: block;
    }

    .weekday-column {
        display: none;
    }

    .weekday-column.active-day {
        display: flex;
    }

    .weekday-navigation {
        display: flex;
    }

    .mobile-only {
        display: flex;
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
}
</style>