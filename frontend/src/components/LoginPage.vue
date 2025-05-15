<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">Вход в систему</h1>

      <form @submit.prevent="login" class="login-form">
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
              placeholder="Введите ваш пароль"
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

        <div class="auth-links">
          <div class="register-link">
            <a href="#" @click.prevent="register">Зарегистрироваться</a>
          </div>
          <div class="forgot-password-link">
            <a href="#" @click.prevent="forgotPassword">Забыли пароль?</a>
          </div>
        </div>

        <button type="submit" class="btn-login" :disabled="isLoading">
          <span v-if="isLoading">Загрузка...</span>
          <span v-else>Войти</span>
        </button>
      </form>

      <div v-if="loginError" class="login-error">
        {{ loginError }}
      </div>
    </div>
  </div>
</template>

<script>

import axios from "axios";

export default {
  name: 'LoginPage',
  data() {
    return {
      email: '',
      password: '',
      showPassword: false,
      isLoading: false,
      loginError: '',
      errors: {
        email: '',
        password: ''
      }
    }
  },
  methods: {
    validateForm() {
      let isValid = true;
      this.errors = {
        email: '',
        password: ''
      };

      if (!this.email) {
        this.errors.email = 'Email обязателен';
        isValid = false;
      } else if (!/^\S+@\S+\.\S+$/.test(this.email)) {
        this.errors.email = 'Некорректный формат email';
        isValid = false;
      }

      if (!this.password) {
        this.errors.password = 'Пароль обязателен';
        isValid = false;
      }

      return isValid;
    },
    async login() {
      if (!this.validateForm()) return;

      this.isLoading = true;
      this.loginError = '';

      try {
         const response = await axios.post(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/token/`, {
            email: this.email,
            password: this.password
          });
        const data = response.data
        localStorage.setItem('token', data['access']);
        localStorage.setItem('ref_token', data['refresh'])

        // Имитация задержки запроса для демонстрации состояния загрузки
        //await new Promise(resolve => setTimeout(resolve, 1000));

        // После успешной авторизации можно редиректить на нужную страницу
        this.$router.push('/');

        console.log('Логин успешен', this.email);
      } catch (error) {
        console.error('Ошибка авторизации:', error);
        this.loginError = 'Неверный email или пароль. Пожалуйста, проверьте введенные данные.';
      } finally {
        this.isLoading = false;
      }
    },
    forgotPassword() {
      this.$router.push('/restore-password');
      console.log('Переход на страницу восстановления пароля');
    },
    register() {
      this.$router.push('/register');
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Open+Sans:wght@400;500;600&display=swap');

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #FDFCFF;
  font-family: 'Manrope', sans-serif;
  color: #2D2D2D;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(110, 58, 255, 0.08);
}

.login-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  text-align: center;
  color: #2D2D2D;
}

.login-form {
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

.auth-links {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin-top: -0.5rem;
}

.register-link,
.forgot-password-link {
  font-size: 0.75rem;
}

.auth-links a {
  color: #6E3AFF;
  text-decoration: none;
  font-weight: 500;
  font-family: 'Open Sans', sans-serif;
}

.auth-links a:hover {
  text-decoration: underline;
}

.btn-login {
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

.btn-login:hover {
  background-color: #5A2DE9;
}

.btn-login:active {
  transform: translateY(1px);
}

.btn-login:disabled {
  background-color: #B9A7FF;
  cursor: not-allowed;
}

.error-message {
  color: #FF5A5F;
  font-size: 0.75rem;
  font-weight: 500;
}

.login-error {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: rgba(255, 90, 95, 0.1);
  border-radius: 6px;
  font-size: 0.875rem;
  color: #FF5A5F;
  text-align: center;
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
    border-radius: 8px;
    max-width: 100%;
    margin: 0 1rem;
  }
}
</style>