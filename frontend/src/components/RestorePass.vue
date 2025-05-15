<template>
  <div class="password-reset-container">
    <div class="password-reset-card">
      <div class="lock-icon" v-if="!emailSent">
        <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M16 9V7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7V9M12 15V17M6 21H18C19.1046 21 20 20.1046 20 19V11C20 9.89543 19.1046 9 18 9H6C4.89543 9 4 9.89543 4 11V19C4 20.1046 4.89543 21 6 21Z" stroke="#6E3AFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      
      <div class="email-icon" v-else>
        <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M22 10V18C22 19.1046 21.1046 20 20 20H4C2.89543 20 2 19.1046 2 18V10M22 10L12 4L2 10M22 10L17 13.5M2 10L7 13.5M12 14L12 14.01" stroke="#00C897" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Шаг 1: Ввод email -->
      <div v-if="!emailSent" class="reset-step">
        <h1 class="reset-title">Восстановление пароля</h1>
        
        <div class="reset-description">
          <p>Для восстановления доступа к аккаунту, пожалуйста, введите адрес электронной почты, который вы использовали при регистрации.</p>
        </div>
        
        <form @submit.prevent="sendResetLink" class="reset-form">
          <div class="form-group">
            <label for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              v-model="email" 
              placeholder="Введите ваш email" 
              required
            />
            <span v-if="error" class="error-message">{{ error }}</span>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn-primary" :disabled="isLoading">
              <span v-if="isLoading">Отправка...</span>
              <span v-else>Отправить ссылку</span>
            </button>
            
            <button type="button" @click="goToLogin" class="btn-secondary">
              Вернуться к входу
            </button>
          </div>
        </form>
      </div>
      
      <!-- Шаг 2: Письмо отправлено -->
      <div v-else class="reset-step">
        <h1 class="reset-title">Проверьте почту</h1>
        
        <div class="reset-description">
          <p>Мы отправили письмо с инструкциями по восстановлению пароля на адрес:</p>
          <p class="email-highlight">{{ email }}</p>
          <p>Пожалуйста, проверьте входящие сообщения и следуйте указаниям в письме.</p>
        </div>
        
        <div class="reset-info">
          <p>Не получили письмо?</p>
          <ul>
            <li>Проверьте папку "Спам" или "Нежелательная почта"</li>
            <li>Убедитесь, что указанный email верный</li>
            <li>Подождите несколько минут, иногда письма доставляются с задержкой</li>
          </ul>
        </div>
        
        <div class="form-actions">
          <button @click="goToLogin" class="btn-primary">
            Вернуться к входу
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: 'PasswordResetPage',
  data() {
    return {
      email: '',
      isLoading: false,
      emailSent: false,
      error: '',
      resendLoading: false,
      resendSuccess: false
    }
  },
  methods: {
    async sendResetLink() {
      if (!this.validateEmail()) return;
      
      this.isLoading = true;
      this.error = '';
      
      try {
        await axios.post(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/password/reset/`, {email: this.email});
        
        // Переключение на следующий шаг
        this.emailSent = true;
        console.log('Ссылка для восстановления отправлена на', this.email);
      } catch (error) {
        console.error('Ошибка при отправке ссылки для восстановления:', error);
        this.error = 'Не удалось отправить ссылку для восстановления. Пожалуйста, проверьте email и попробуйте снова.';
      } finally {
        this.isLoading = false;
      }
    },
    
    validateEmail() {
      if (!this.email) {
        this.error = 'Пожалуйста, введите email';
        return false;
      }
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.email)) {
        this.error = 'Пожалуйста, введите корректный email';
        return false;
      }
      
      return true;
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

.password-reset-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #FDFCFF;
  font-family: 'Manrope', sans-serif;
  color: #2D2D2D;
}

.password-reset-card {
  width: 100%;
  max-width: 480px;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(110, 58, 255, 0.08);
}

.lock-icon, .email-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.reset-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  text-align: center;
  color: #2D2D2D;
}

.reset-description {
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.reset-description p {
  margin-bottom: 0.75rem;
  color: #2D2D2D;
}

.email-highlight {
  font-weight: 600;
  color: #6E3AFF;
  background-color: #F0EBFF;
  padding: 0.75rem;
  border-radius: 8px;
  margin: 1rem 0;
  text-align: center;
}

.reset-form {
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

.form-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
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

.btn-primary:disabled {
  background-color: #B9A7FF;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: white;
  color: #6E3AFF;
  border: 1px solid #6E3AFF;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-family: 'Manrope', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
}

.btn-secondary:hover {
  background-color: #F0EBFF;
}

.btn-secondary:active {
  transform: translateY(1px);
}

.btn-secondary:disabled {
  color: #B9A7FF;
  border-color: #B9A7FF;
  cursor: not-allowed;
}

.error-message {
  color: #FF5A5F;
  font-size: 0.75rem;
  font-weight: 500;
}

.reset-info {
  background-color: #F0EBFF;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.reset-info p {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.reset-info ul {
  padding-left: 1.25rem;
  margin: 0;
}

.reset-info li {
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #6B6B6B;
}

.reset-info li:last-child {
  margin-bottom: 0;
}

@media (max-width: 560px) {
  .password-reset-card {
    padding: 1.5rem;
    border-radius: 8px;
    max-width: 100%;
    margin: 0 1rem;
  }
  
  .reset-title {
    font-size: 1.5rem;
  }
}
</style>