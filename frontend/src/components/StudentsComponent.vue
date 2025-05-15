<!-- Students.vue -->
<template>
  <div class="students-container">
    <div class="search-bar">
      <input type="text" v-model="searchQuery" placeholder="Поиск студентов..." class="search-input">
      <button type="button" class="add-student-btn" @click.stop="openAddModal">Добавить студента</button>
    </div>

    <div class="students-list">
      <div v-if="loading" class="loading-state">
        <p>Загрузка студентов...</p>
      </div>
      <div v-else-if="students.length === 0" class="empty-state">
        <p>Студенты не найдены</p>
      </div>
      <div v-else class="student-cards">
        <div v-for="student in filteredStudents" :key="student.id" class="student-card">
          <div class="student-info">
            <h3>{{ student.name }}</h3>
            <h3>{{ student.surname }}</h3>
          </div>
          <div class="student-actions">
            <button type="button" class="details-btn" @click.stop="openDetailsModal(student)">Подробнее</button>
            <button type="button" class="delete-btn" @click.stop="confirmDelete(student)">Удалить</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно для добавления/редактирования студента -->
    <div class="modal" v-if="showModal" @click.self="closeModal">
      <div class="modal-overlay" @click.stop="closeModal"></div>
      <div class="modal-content">
        <h2>{{ isEditing ? 'Редактирование студента' : 'Добавление нового студента' }}</h2>
        <form @submit.prevent="saveStudent">
          <div class="form-group">
            <label for="name">Имя*</label>
            <input type="text" id="name" v-model="currentStudent.name" required>
          </div>
          <div class="form-group">
            <label for="surname">Фамилия</label>
            <input type="text" id="surname" v-model="currentStudent.surname">
          </div>
          <div class="form-group">
            <label for="contacts">Контактные данные</label>
            <input type="text" id="contacts" v-model="currentStudent.contacts">
          </div>
          <div class="form-group">
            <label for="comment">Комментарий</label>
            <input type="text" id="comment" v-model="currentStudent.comment">
          </div>
          <div class="form-group">
            <label for="address">Адрес</label>
            <input type="text" id="address" v-model="currentStudent.address">
          </div>
          <div class="modal-actions">
            <button type="button" class="cancel-btn" @click.stop="closeModal">Отмена</button>
            <button type="submit" class="save-btn">Сохранить</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Модальное окно для подтверждения удаления -->
    <div class="modal" v-if="showDeleteConfirm" @click.self="cancelDelete">
      <div class="modal-overlay" @click.stop="cancelDelete"></div>
      <div class="modal-content confirm-modal">
        <h2>Подтверждение удаления</h2>
        <p>Вы действительно хотите удалить студента "{{ studentToDelete?.name }}"?</p>
        <div class="modal-actions">
          <button type="button" class="cancel-btn" @click.stop="cancelDelete">Отмена</button>
          <button type="button" class="delete-confirm-btn" @click.stop="deleteStudent">Удалить</button>
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

// Список студентов
const students = ref([]);

// Поиск студентов
const searchQuery = ref('');

// Состояние модальных окон
const showModal = ref(false);
const showDeleteConfirm = ref(false);
const isEditing = ref(false);

// Текущий студент для редактирования/добавления
  const currentStudent = ref({
      id: null,
      name: '',
      surname: '',
      contacts: '',
      comment: '',
      address: ''
  });

// Студент для удаления
const studentToDelete = ref(null);

// Получение списка студентов с сервера
const fetchStudents = async () => {
  try {
    loading.value = true;
    const response = await axios.get(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcards/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });
    students.value = response.data;
  } catch (error) {
    console.error('Ошибка при загрузке студентов:', error);
  } finally {
    loading.value = false;
  }
};

// Фильтрация студентов по поисковому запросу
const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value;

  const query = searchQuery.value.toLowerCase();
  return students.value.filter(student =>
    student.name.toLowerCase().includes(query) ||
    (student.surname && student.surname.toLowerCase().includes(query)) ||
    (student.contacts && student.contacts.toLowerCase().includes(query))
  );
});
// Обработчики модального окна для добавления/редактирования
const openAddModal = () => {
  isEditing.value = false;
  currentStudent.value = {
      id: null,
      name: '',
      surname: '',
      contacts: '',
      comment: '',
      address: ''
  };
  showModal.value = true;
};

const openDetailsModal = (student) => {
  isEditing.value = true;
  currentStudent.value = { ...student };
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

// Сохранение студента (добавление или обновление)
const saveStudent = async () => {
  try {
    if (isEditing.value) {
      // Обновление существующего студента
      await axios.put(
        `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcards/${currentStudent.value.id}/`,
        currentStudent.value,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
    } else {
      // Добавление нового студента
        console.log(currentStudent.value);
      await axios.post(
        `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcards/`,
        currentStudent.value,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
    }
    // После успешного сохранения обновляем список студентов
    await fetchStudents();
    closeModal();
  } catch (error) {
    console.error('Ошибка при сохранении студента:', error);
  }
};

// Обработчики удаления
const confirmDelete = (student) => {
  studentToDelete.value = student;
  showDeleteConfirm.value = true;
};

const cancelDelete = () => {
  studentToDelete.value = null;
  showDeleteConfirm.value = false;
};

const deleteStudent = async () => {
  try {
    await axios.delete(
      `${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/studentcards/${studentToDelete.value.id}/`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    );
    // После успешного удаления обновляем список студентов
    await fetchStudents();
    cancelDelete();
  } catch (error) {
    console.error('Ошибка при удалении студента:', error);
  }
};

// Загрузка данных при монтировании компонента
onMounted(() => {
  fetchStudents();
});
</script>

<style scoped>
.students-container {
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

.add-student-btn {
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

.add-student-btn:hover {
  background-color: #5D2DE0;
}

.add-student-btn:active {
  background-color: #502BC0;
}

.students-list {
  margin-top: 1.5rem;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 3rem 0;
  color: #757575;
}

.student-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.student-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  touch-action: manipulation;
}

.student-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.student-info h3 {
  margin: 0;
  font-weight: 600;
  color: #2D2D2D;
  text-align: center;
}

.student-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
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
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-size: 0.875rem;
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

  .student-cards {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 90%;
    margin: 0;
    padding: 1.25rem;
    max-height: 80vh;
  }

  .student-actions {
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