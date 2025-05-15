<!-- GroupsComponent.vue -->
<template>
  <div class="groups-container">
    <div class="search-bar">
      <input type="text" v-model="searchQuery" placeholder="Поиск групп..." class="search-input">
      <button type="button" class="add-group-btn" @click.stop="openAddModal">Добавить группу</button>
    </div>

    <div class="groups-list">
      <div v-if="loading" class="loading-state">
        <p>Загрузка групп...</p>
      </div>
      <div v-else-if="groups.length === 0" class="empty-state">
        <p>Группы не найдены</p>
      </div>
      <div v-else class="group-cards">
        <div v-for="group in filteredGroups" :key="group.id" class="group-card">
          <div class="group-info">
            <h3>{{ group.name }}</h3>
            <p class="student-count">Студентов: {{ group.students.length }}</p>
          </div>
          <div class="group-actions">
            <button type="button" class="details-btn" @click.stop="openDetailsModal(group)">Подробнее</button>
            <button type="button" class="delete-btn" @click.stop="confirmDelete(group)">Удалить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно для добавления/редактирования группы -->
    <div class="modal" v-if="showModal" @click.self="closeModal">
      <div class="modal-overlay" @click.stop="closeModal"></div>
      <div class="modal-content">
        <h2>{{ isEditing ? 'Редактирование группы' : 'Добавление новой группы' }}</h2>
        <form @submit.prevent="saveGroup">
          <div class="form-group">
            <label for="name">Название группы*</label>
            <input type="text" id="name" v-model="currentGroup.name" required>
          </div>
          <div class="form-group">
            <label for="comment">Комментарий</label>
            <input type="text" id="comment" v-model="currentGroup.comment">
          </div>

          <div class="form-group">
            <label class="students-label">Студенты*</label>
            <div v-if="loadingStudents" class="loading-students">
              <p>Загрузка списка студентов...</p>
            </div>
            <div v-else>
              <!-- Улучшенный интерфейс выбора студентов -->
              <div class="students-selection-container">
                <!-- Поиск студентов -->
                <div class="student-search">
                  <input
                    type="text"
                    v-model="studentSearchQuery"
                    placeholder="Поиск студентов..."
                    class="student-search-input"
                  >
                </div>

                <!-- Отображение выбранных студентов -->
                <div class="selected-students-section" v-if="selectedStudentIds.length > 0">
                  <p class="selected-count">Выбрано студентов: {{ selectedStudentIds.length }}</p>
                  <div class="selected-students-list">
                    <div
                      v-for="studentId in selectedStudentIds"
                      :key="studentId"
                      class="selected-student-tag"
                    >
                      {{ getStudentName(studentId) }}
                      <button
                        type="button"
                        class="remove-student-btn"
                        @click="removeSelectedStudent(studentId)"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Список доступных студентов с поиском -->
                <div class="available-students-section">
                  <div v-if="filteredStudents.length === 0" class="no-students-message">
                    <p>Нет подходящих студентов</p>
                  </div>
                  <div v-else class="student-list">
                    <div
                      v-for="student in filteredStudents"
                      :key="student.id"
                      class="student-item"
                      :class="{ 'student-selected': isStudentSelected(student.id) }"
                      @click="toggleStudentSelection(student.id)"
                    >
                      <span class="student-name">{{ student.name }} {{ student.surname }}</span>
                      <span class="selection-indicator">
                        {{ isStudentSelected(student.id) ? '✓' : '+' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <p v-if="selectedStudentIds.length === 0" class="validation-error">
                Выберите хотя бы одного студента
              </p>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click.stop="closeModal">Отмена</button>
            <button type="submit" class="save-btn" :disabled="selectedStudentIds.length === 0">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно для подтверждения удаления -->
    <div class="modal" v-if="showDeleteConfirm" @click.self="cancelDelete">
      <div class="modal-overlay" @click.stop="cancelDelete"></div>
      <div class="modal-content confirm-modal">
        <h2>Подтверждение удаления</h2>
        <p>Вы действительно хотите удалить группу "{{ groupToDelete?.name }}"?</p>
        <div class="modal-actions">
          <button type="button" class="cancel-btn" @click.stop="cancelDelete">Отмена</button>
          <button type="button" class="delete-confirm-btn" @click.stop="deleteGroup">Удалить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

// Состояние загрузки
const loading = ref(true);
const loadingStudents = ref(false);

// Список групп
const groups = ref([]);

// Список всех студентов
const allStudents = ref([]);

// Поиск групп
const searchQuery = ref('');
// Поиск студентов в модальном окне
const studentSearchQuery = ref('');

// Состояние модальных окон
const showModal = ref(false);
const showDeleteConfirm = ref(false);
const isEditing = ref(false);

// Текущая группа для редактирования/добавления
const currentGroup = ref({
  id: null,
  name: '',
  comment: '',
  students: []
});

// Выбранные студенты для группы (ID)
const selectedStudentIds = ref([]);

// Группа для удаления
const groupToDelete = ref(null);

// Получение списка групп с сервера
const fetchGroups = async () => {
  try {
    loading.value = true;
    const response = await axios.get(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcardgroups/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    groups.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке групп:', error);
  } finally {
    loading.value = false;
  }
};

// Получение списка всех студентов
const fetchAllStudents = async () => {
  try {
    loadingStudents.value = true;
    const response = await axios.get(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcards/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    allStudents.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке студентов:', error);
  } finally {
    loadingStudents.value = false;
  }
};

// Фильтрация групп по поисковому запросу
const filteredGroups = computed(() => {
  if (!searchQuery.value) return groups.value;

  const query = searchQuery.value.toLowerCase();
  return groups.value.filter(group =>
    group.name.toLowerCase().includes(query) ||
    (group.comment && group.comment.toLowerCase().includes(query))
  );
});

// Фильтрация студентов по поисковому запросу
const filteredStudents = computed(() => {
  if (!studentSearchQuery.value) return allStudents.value;

  const query = studentSearchQuery.value.toLowerCase();
  return allStudents.value.filter(student =>
    student.name.toLowerCase().includes(query) ||
    student.surname.toLowerCase().includes(query)
  );
});

// Получение имени и фамилии студента по ID
const getStudentName = (studentId) => {
  const student = allStudents.value.find(s => s.id === studentId);
  return student ? `${student.name} ${student.surname}` : 'Неизвестный студент';
};

// Проверка выбран ли студент
const isStudentSelected = (studentId) => {
  return selectedStudentIds.value.includes(studentId);
};

// Переключение выбора студента
const toggleStudentSelection = (studentId) => {
  const index = selectedStudentIds.value.indexOf(studentId);
  if (index === -1) {
    selectedStudentIds.value.push(studentId);
  } else {
    selectedStudentIds.value.splice(index, 1);
  }
};

// Удаление студента из выбранных
const removeSelectedStudent = (studentId) => {
  const index = selectedStudentIds.value.indexOf(studentId);
  if (index !== -1) {
    selectedStudentIds.value.splice(index, 1);
  }
};

// Обработчики модального окна для добавления/редактирования
const openAddModal = async () => {
  isEditing.value = false;
  currentGroup.value = {
    id: null,
    name: '',
    comment: '',
    students: []
  };
  selectedStudentIds.value = [];
  studentSearchQuery.value = '';

  // Загружаем список студентов
  await fetchAllStudents();

  showModal.value = true;
};

const openDetailsModal = async (group) => {
  isEditing.value = true;
  currentGroup.value = { ...group };
  studentSearchQuery.value = '';

  // Загружаем список студентов
  await fetchAllStudents();

  // Устанавливаем выбранных студентов
  selectedStudentIds.value = group.students.map(student => student.id);

  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

// Сохранение группы (добавление или обновление)
const saveGroup = async () => {
  if (selectedStudentIds.value.length === 0) {
    return; // Не сохраняем, если не выбран ни один студент
  }

  try {
    const groupData = {
      name: currentGroup.value.name,
      comment: currentGroup.value.comment,
      students: selectedStudentIds.value
    };

    if (isEditing.value) {
      // Обновление существующей группы
      await axios.put(
        `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcardgroups/${currentGroup.value.id}/`,
        groupData,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
    } else {
      // Добавление новой группы
      await axios.post(
        `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcardgroups/`,
        groupData,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
    }
    // После успешного сохранения обновляем список групп
    await fetchGroups();
    closeModal();
  } catch (error) {
    console.error('Ошибка при сохранении группы:', error);
  }
};

// Обработчики удаления
const confirmDelete = (group) => {
  groupToDelete.value = group;
  showDeleteConfirm.value = true;
};

const cancelDelete = () => {
  groupToDelete.value = null;
  showDeleteConfirm.value = false;
};

const deleteGroup = async () => {
  try {
    await axios.delete(
      `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcardgroups/${groupToDelete.value.id}/`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    );
    // После успешного удаления обновляем список групп
    await fetchGroups();
    cancelDelete();
  } catch (error) {
    console.error('Ошибка при удалении группы:', error);
  }
};

// Загрузка данных при монтировании компонента
onMounted(() => {
  fetchGroups();
});
</script>

<style scoped>
.groups-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 0;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2rem;
  gap: 1rem;
}

.search-input {
  flex-grow: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-size: 0.875rem;
}

.add-group-btn {
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

.add-group-btn:hover {
  background-color: #5D2DE0;
}

.add-group-btn:active {
  background-color: #502BC0;
}

.groups-list {
  margin-top: 1.5rem;
}

.empty-state, .loading-state, .loading-students {
  text-align: center;
  padding: 1.5rem 0;
  color: #757575;
}

.group-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.group-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  touch-action: manipulation;
  min-height: 150px;
  height: 100%;
}

.group-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.group-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}

.group-info h3 {
  margin: 0 0 0.5rem;
  font-weight: 600;
  color: #2D2D2D;
  word-break: break-word;
  overflow-wrap: break-word;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  max-height: 3em;
}

.student-count {
  color: #757575;
  font-size: 0.875rem;
  margin: 0;
  word-break: break-word;
}

.group-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: auto; /* Прижимаем кнопки к низу */
}

.details-btn, .delete-btn {
  flex: 1;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-weight: 500;
  font-size: 0.8125rem;
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

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2D2D2D;
}

.form-group input {
  width: 95%;
  padding: 0.75rem;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-size: 0.875rem;
}

.students-label {
  margin-bottom: 0.75rem;
}

/* Новые стили для улучшенного интерфейса выбора студентов */
.students-selection-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  padding: 1rem;
}

.student-search {
  margin-bottom: 0.5rem;
}

.student-search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-size: 0.875rem;
}

.selected-students-section {
  margin-bottom: 1rem;
}

.selected-count {
  font-size: 0.875rem;
  color: #2D2D2D;
  margin: 0 0 0.5rem;
  font-weight: 500;
}

.selected-students-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.selected-student-tag {
  display: flex;
  align-items: center;
  background-color: #F0EBFF;
  color: #6E3AFF;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.remove-student-btn {
  background: none;
  border: none;
  color: #6E3AFF;
  margin-left: 0.25rem;
  cursor: pointer;
  font-size: 1rem;
  line-height: 0.5;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-student-btn:hover {
  color: #5D2DE0;
}

.available-students-section {
  max-height: 200px;
  overflow-y: auto;
}

.student-list {
  display: flex;
  flex-direction: column;
}

.student-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #F5F5F5;
  transition: background-color 0.2s ease;
}

.student-item:last-child {
  border-bottom: none;
}

.student-item:hover {
  background-color: #F9F9F9;
}

.student-selected {
  background-color: #F0EBFF;
}

.student-selected:hover {
  background-color: #E4D9FF;
}

.student-name {
  font-size: 0.875rem;
}

.selection-indicator {
  color: #6E3AFF;
  font-size: 0.875rem;
  font-weight: bold;
}

.no-students-message {
  text-align: center;
  padding: 1rem;
  color: #757575;
  font-style: italic;
}

.validation-error {
  color: #FF3A6E;
  font-size: 0.75rem;
  margin-top: 0.5rem;
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

@media (max-width: 768px) {
  .search-bar {
    flex-direction: column;
  }

  .group-cards {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 90%;
    margin: 0;
    padding: 1.25rem;
    max-height: 80vh;
  }

  .group-actions {
    flex-direction: row;
  }

  .details-btn, .delete-btn {
    width: 50%;
  }

  .modal-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .modal-actions button {
    flex: 1;
    min-width: 120px;
    padding: 0.75rem 0.5rem;
  }
}
</style>