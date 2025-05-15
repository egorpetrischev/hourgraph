<template>
  <div class="register-container">
    <!-- Экран регистрации -->
    <div v-if="!registrationSuccess" class="register-card">
      <h1 class="register-title">Регистрация</h1>

      <form @submit.prevent="register" class="register-form">
        <div class="form-group">
          <label for="name">Имя</label>
          <input
            type="text"
            id="name"
            v-model="name"
            placeholder="Введите ваше имя"
            required
          />
          <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input
            type="email"
            id="email"
            v-model="email"
            placeholder="Введите ваш email"
            required
          />
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password">Пароль</label>
          <div class="password-input">
            <input
              :type="showPassword ? 'text' : 'password'"
              id="password"
              v-model="password"
              placeholder="Создайте пароль"
              required
            />
            <button
              type="button"
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? 'Скрыть' : 'Показать' }}
            </button>
          </div>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label for="confirmPassword">Подтвердите пароль</label>
          <div class="password-input">
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              id="confirmPassword"
              v-model="confirmPassword"
              placeholder="Введите пароль повторно"
              required
            />
            <button
              type="button"
              class="toggle-password"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              {{ showConfirmPassword ? 'Скрыть' : 'Показать' }}
            </button>
          </div>
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
        </div>

        <button type="submit" class="btn-register" :disabled="isLoading">
          <span v-if="isLoading">Создание аккаунта...</span>
          <span v-else>Зарегистрироваться</span>
        </button>
      </form>

      <div v-if="registerError" class="register-error">
        {{ registerError }}
      </div>

      <div class="login-link">
        <span>Уже есть аккаунт?</span>
        <a href="#" @click.prevent="goToLogin">Войти</a>
      </div>
    </div>

    <!-- Экран подтверждения Email -->
    <div v-else class="email-verify-card">
      <div class="email-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M22 10V18C22 19.1046 21.1046 20 20 20H4C2.89543 20 2 19.1046 2 18V10M22 10L12 4L2 10M22 10L17 13.5M2 10L7 13.5M2 6L12 12L22 6" stroke="#6E3AFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <h1 class="email-verify-title">Подтвердите ваш e-mail</h1>

      <div class="email-verify-message">
        <p>Для завершения регистрации необходимо подтвердить адрес электронной почты. Мы отправили письмо с ссылкой для активации вашего аккаунта.</p>

        <p class="email-info" v-if="email">
          Письмо отправлено на: <span class="highlight-email">{{ email }}</span>
        </p>
      </div>

      <div class="action-buttons">
        <button @click="goToLogin" class="btn-primary">
          Перейти к входу
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: 'RegisterPage',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      showPassword: false,
      showConfirmPassword: false,
      isLoading: false,
      registerError: '',
      registrationSuccess: false,
      errors: {
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    }
  },
  methods: {
    validateForm() {
      let isValid = true;
      this.errors = {
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
      };

      // Валидация имени
      if (!this.name.trim()) {
        this.errors.name = 'Имя обязательно';
        isValid = false;
      }

      // Валидация email
      if (!this.email) {
        this.errors.email = 'Email обязателен';
        isValid = false;
      } else if (!/^\S+@\S+\.\S+$/.test(this.email)) {
        this.errors.email = 'Некорректный формат email';
        isValid = false;
      }

      // Валидация пароля
      if (!this.password) {
        this.errors.password = 'Пароль обязателен';
        isValid = false;
      } else if (this.password.length < 8) {
        this.errors.password = 'Пароль должен содержать минимум 8 символов';
        isValid = false;
      }

      // Проверка совпадения паролей
      if (this.password !== this.confirmPassword) {
        this.errors.confirmPassword = 'Пароли не совпадают';
        isValid = false;
      }

      return isValid;
    },
    async register() {
      if (!this.validateForm()) return;

      this.isLoading = true;
      this.registerError = '';

      try {
        await axios.post(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/register/`, {
          name: this.name,
          email: this.email,
          password: this.password
        });

        // Сохраняем email в localStorage (хотя в объединенном компоненте это не обязательно)
        localStorage.setItem('registrationEmail', this.email);

        // Переключаем на экран подтверждения email
        this.registrationSuccess = true;

        console.log('Регистрация успешна', this.email);
      } catch (error) {
        console.error('Ошибка регистрации:', error);
        this.registerError = 'Не удалось создать аккаунт. Возможно, пользователь с таким email уже существует.';
      } finally {
        this.isLoading = false;
      }
    },
    goToLogin() {
      this.$router.push('/login');
      console.log('Переход на страницу входа');
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Open+Sans:wght@400;500;600&display=swap');

.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #FDFCFF;
  font-family: 'Manrope', sans-serif;
  color: #2D2D2D;
}

/* Стили для экрана регистрации */
.register-card {
  width: 100%;
  max-width: 460px;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(110, 58, 255, 0.08);
}

.register-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  text-align: center;
  color: #2D2D2D;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #2D2D2D;
}

input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  font-family: 'Open Sans', sans-serif;
  font-size: 1rem;
  color: #2D2D2D;
  background-color: white;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #6E3AFF;
  outline: none;
  box-shadow: 0 0 0 3px rgba(110, 58, 255, 0.15);
}

input::placeholder {
  color: #6B6B6B;
  opacity: 0.6;
}

.password-input {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6E3AFF;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  font-family: 'Manrope', sans-serif;
}

.toggle-password:hover {
  text-decoration: underline;
}

.btn-register {
  background-color: #6E3AFF;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-family: 'Manrope', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
  margin-top: 0.5rem;
}

.btn-register:hover {
  background-color: #5A2DE9;
}

.btn-register:active {
  transform: translateY(1px);
}

.btn-register:disabled {
  background-color: #B9A7FF;
  cursor: not-allowed;
}

.error-message {
  color: #FF5A5F;
  font-size: 0.75rem;
  font-weight: 500;
}

.register-error {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: rgba(255, 90, 95, 0.1);
  border-radius: 6px;
  font-size: 0.875rem;
  color: #FF5A5F;
  text-align: center;
}

.login-link {
  margin-top: 1.25rem;
  text-align: center;
  font-size: 0.875rem;
  color: #6B6B6B;
}

.login-link a {
  margin-left: 0.5rem;
  color: #6E3AFF;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.login-link a:hover {
  text-decoration: underline;
  color: #5A2DE9;
}

/* Стили для экрана подтверждения email */
.email-verify-card {
  width: 100%;
  max-width: 520px;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(110, 58, 255, 0.08);
  text-align: center;
}

.email-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.email-verify-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  color: #2D2D2D;
}

.email-verify-message {
  margin-bottom: 2rem;
  line-height: 1.6;
}

.email-verify-message p {
  margin-bottom: 1rem;
  font-size: 1rem;
  color: #2D2D2D;
}

.email-info {
  background-color: #F0EBFF;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1.5rem;
}

.highlight-email {
  font-weight: 600;
  color: #6E3AFF;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.btn-primary {
  background-color: #6E3AFF;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-family: 'Manrope', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
}

.btn-primary:hover {
  background-color: #5A2DE9;
}

.btn-primary:active {
  transform: translateY(1px);
}

/* Адаптивные стили */
@media (max-width: 560px) {
  .register-card,
  .email-verify-card {
    padding: 1.5rem;
    border-radius: 8px;
    max-width: 100%;
    margin: 0 1rem;
  }

  .register-title,
  .email-verify-title {
    font-size: 1.5rem;
  }
}
</style>