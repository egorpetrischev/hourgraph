<template>
  <div class="profile-container">
    <h1 class="profile-title">Профиль пользователя</h1>

    <!-- Секция смены пароля -->
    <div class="form-section">
      <h2 class="section-title">Изменение пароля</h2>
      <div class="form-group">
        <label for="oldPassword">Текущий пароль</label>
        <input
          type="password"
          id="oldPassword"
          v-model="passwordForm.oldPassword"
          class="form-input"
          placeholder="Введите текущий пароль"
        />
      </div>
      <div class="form-group">
        <label for="newPassword">Новый пароль</label>
        <input
          type="password"
          id="newPassword"
          v-model="passwordForm.newPassword"
          class="form-input"
          placeholder="Введите новый пароль"
        />
      </div>
      <div class="form-group">
        <label for="confirmPassword">Подтвердите пароль</label>
        <input
          type="password"
          id="confirmPassword"
          v-model="passwordForm.confirmPassword"
          class="form-input"
          placeholder="Подтвердите новый пароль"
        />
        <p v-if="passwordError" class="error-message">{{ passwordError }}</p>
      </div>
      <button
        class="submit-btn"
        @click="changePassword"
        :disabled="isPasswordFormIncomplete || isPasswordChanging"
      >
        {{ isPasswordChanging ? 'Изменение...' : 'Изменить пароль' }}
      </button>
      <p v-if="passwordSuccess" class="success-message">{{ passwordSuccess }}</p>
    </div>

    <!-- Секция Telegram ID -->
    <div class="form-section">
      <h2 class="section-title">Настройка уведомлений Telegram</h2>
      <div class="form-group">
        <label for="telegramId">Идентификатор чата Telegram</label>
        <input
          type="text"
          id="telegramId"
          v-model="telegramId"
          class="form-input"
          placeholder="Введите идентификатор чата Telegram"
          maxlength="32"
        />
        <div class="input-info">
          <span class="char-counter">{{ telegramId.length }}/32</span>
        </div>
      </div>
      <div class="info-box">
        <p>Для получения уведомлений необходимо написать боту <a href="https://t.me/HourGraphBot" target="_blank">@HourGraphBot</a> и добавить идентификатор чата, который он пришлет.</p>
      </div>
      <button
        class="submit-btn"
        @click="saveTelegramId"
        :disabled="isTelegramIdSaving"
      >
        {{ isTelegramIdSaving ? 'Сохранение...' : 'Сохранить' }}
      </button>
      <p v-if="telegramSuccess" class="success-message">{{ telegramSuccess }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

// Данные для формы смены пароля
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// Данные для Telegram ID
const telegramId = ref('');

// Состояния загрузки
const isPasswordChanging = ref(false);
const isTelegramIdSaving = ref(false);

// Сообщения об ошибках и успехе
const passwordError = ref('');
const passwordSuccess = ref('');
const telegramSuccess = ref('');

// Вычисляемое свойство для проверки заполнения формы пароля
const isPasswordFormIncomplete = computed(() => {
  return !passwordForm.value.oldPassword ||
         !passwordForm.value.newPassword ||
         !passwordForm.value.confirmPassword;
});

// Получение данных пользователя при загрузке компонента
onMounted(async () => {
  try {
    const response = await axios.get(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/user-profile/`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    // Если у пользователя уже есть Telegram ID, заполняем поле
    if (response.data.telegram_chat_id) {
      telegramId.value = response.data.telegram_chat_id;
    }
  } catch (error) {
    console.error('Ошибка при загрузке профиля:', error);
  }
});

// Функция смены пароля
const changePassword = async () => {
  // Сбрасываем сообщения об ошибке и успехе
  passwordError.value = '';
  passwordSuccess.value = '';

  // Проверка совпадения паролей
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = 'Новый пароль и подтверждение не совпадают';
    return;
  }

  isPasswordChanging.value = true;

  try {
    await axios.post(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/change-password/`, {
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword
    }, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    // Сбрасываем форму при успешной смене пароля
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    };

    passwordSuccess.value = 'Пароль успешно изменен';

    // Убираем сообщение об успехе через 5 секунд
    setTimeout(() => {
      passwordSuccess.value = '';
    }, 5000);

  } catch (error) {
    if (error.response && error.response.data) {
      if (error.response.data.old_password) {
        passwordError.value = 'Неверный текущий пароль';
      } else if (error.response.data.new_password) {
        passwordError.value = error.response.data.new_password.join(', ');
      } else {
        passwordError.value = 'Ошибка при смене пароля';
      }
    } else {
      passwordError.value = 'Ошибка сервера. Попробуйте позже';
    }
  } finally {
    isPasswordChanging.value = false;
  }
};

// Функция сохранения Telegram ID
const saveTelegramId = async () => {
  telegramSuccess.value = '';
  isTelegramIdSaving.value = true;

  try {
    await axios.post(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/update-telegram-id/`, {
      telegram_chat_id: telegramId.value
    }, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    });

    telegramSuccess.value = 'Идентификатор Telegram успешно сохранен';

    // Убираем сообщение об успехе через 5 секунд
    setTimeout(() => {
      telegramSuccess.value = '';
    }, 5000);

  } catch (error) {
    console.error('Ошибка при сохранении Telegram ID:', error);
  } finally {
    isTelegramIdSaving.value = false;
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem 1rem;
  font-family: 'Manrope', sans-serif;
}

.profile-title {
  color: #2D2D2D;
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 2rem;
}

.form-section {
  background-color: #FFFFFF;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-title {
  color: #2D2D2D;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
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

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-size: 0.95rem;
  transition: border-color 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #6E3AFF;
}

.form-input::placeholder {
  color: #A0A0A0;
}

.input-info {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.25rem;
}

.char-counter {
  font-size: 0.8rem;
  color: #777777;
}

.info-box {
  background-color: #F0EBFF;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1.25rem;
}

.info-box p {
  color: #2D2D2D;
  font-size: 0.95rem;
  margin: 0;
}

.info-box a {
  color: #6E3AFF;
  text-decoration: none;
  font-weight: 500;
}

.info-box a:hover {
  text-decoration: underline;
}

.submit-btn {
  background-color: #6E3AFF;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.75rem 1.5rem;
  font-family: 'Manrope', sans-serif;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-btn:hover:not(:disabled) {
  background-color: #5A2DE0;
}

.submit-btn:disabled {
  background-color: #BEBEBE;
  cursor: not-allowed;
}

.error-message {
  color: #E53935;
  font-size: 0.85rem;
  margin-top: 0.5rem;
  margin-bottom: 0;
}

.success-message {
  color: #4CAF50;
  font-size: 0.95rem;
  margin-top: 0.75rem;
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .profile-container {
    padding: 1.5rem 1rem;
  }

  .profile-title {
    font-size: 1.5rem;
  }

  .section-title {
    font-size: 1.15rem;
  }

  .form-input {
    padding: 0.7rem 0.9rem;
  }

  .submit-btn {
    width: 100%;
  }
}
</style>