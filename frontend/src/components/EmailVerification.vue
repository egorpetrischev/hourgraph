<template>
  <div class="confirm-email-container">
    <div class="confirm-email-card">
      <!-- Иконка в шапке компонента -->
      <div class="confirm-icon" v-if="!isConfirmed">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#6E3AFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="success-icon" v-else>
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 13L9 17L19 7M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#00C897" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Состояние подтверждения email -->
      <div v-if="!isConfirmed && !isError">
        <h1 class="confirm-email-title">Подтверждение электронной почты</h1>

        <div class="confirm-email-message">
          <p>Вы почти у цели! Для активации вашего аккаунта необходимо подтвердить адрес электронной почты.</p>

          <p class="email-note">Нажмите кнопку ниже для завершения процесса регистрации.</p>
        </div>

        <div class="action-buttons">
          <button
            @click="confirmEmail"
            class="btn-confirm"
            :disabled="isLoading"
          >
            <span v-if="isLoading">Подтверждение...</span>
            <span v-else>Подтвердить</span>
          </button>
        </div>
      </div>

      <!-- Состояние успешного подтверждения -->
      <div v-else-if="isConfirmed">
        <h1 class="confirm-email-title">Email успешно подтвержден!</h1>

        <div class="confirm-email-message">
          <p>Поздравляем! Ваш адрес электронной почты успешно подтвержден.</p>
          <p>Теперь вы можете войти в свой аккаунт, используя свои учетные данные.</p>
        </div>

        <div class="action-buttons">
          <button @click="goToLogin" class="btn-primary">
            Перейти к входу
          </button>
        </div>
      </div>

      <!-- Состояние ошибки -->
      <div v-else>
        <h1 class="confirm-email-title error-title">Ошибка подтверждения</h1>

        <div class="confirm-email-message">
          <p>К сожалению, возникла проблема при подтверждении вашего email.</p>
          <p class="error-details">{{ errorMessage }}</p>
          <p>Возможно, ссылка устарела или была уже использована ранее.</p>
        </div>

        <div class="action-buttons">
          <button @click="goToLogin" class="btn-primary">
            Перейти к входу
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: 'ConfirmEmailPage',
  props: {
    activationKey: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      isLoading: false,
      isConfirmed: false,
      isError: false,
      errorMessage: ''
    }
  },
  methods: {
    async confirmEmail() {
      this.isLoading = true;

      try {
        // Отправляем запрос на подтверждение email с ключом активации
        await axios.post(`http://${process.env.VUE_APP_IP}:8000/api/verify-email/` + this.activationKey + '/');

        console.log('как бы должен');
        // Если запрос успешен, устанавливаем флаг подтверждения
        this.isConfirmed = true;
      } catch (error) {
        this.isError = true;

        // Обработка различных типов ошибок
        if (error.response && error.response.data) {
          if (error.response.data.detail) {
            this.errorMessage = error.response.data.detail;
          } else if (error.response.data.key) {
            this.errorMessage = error.response.data.key[0];
          } else {
            this.errorMessage = 'Произошла ошибка при подтверждении email.';
          }
        } else {
          this.errorMessage = 'Не удалось связаться с сервером. Пожалуйста, попробуйте позже.';
        }

        console.error('Ошибка подтверждения email:', error);
      } finally {
        this.isLoading = false;
      }
    },

    goToLogin() {
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Open+Sans:wght@400;500;600&display=swap');

.confirm-email-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #FDFCFF;
  font-family: 'Manrope', sans-serif;
  color: #2D2D2D;
  padding: 20px;
}

.confirm-email-card {
  width: 100%;
  max-width: 500px;
  padding: 2.5rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(110, 58, 255, 0.08);
  text-align: center;
}

.confirm-icon, .success-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.confirm-email-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.25rem;
  color: #2D2D2D;
}

.error-title {
  color: #FF5A5F;
}

.confirm-email-message {
  margin-bottom: 2rem;
  line-height: 1.6;
}

.confirm-email-message p {
  margin-bottom: 1rem;
  font-size: 1rem;
  color: #2D2D2D;
}

.email-note {
  background-color: #F0EBFF;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.error-details {
  background-color: rgba(255, 90, 95, 0.1);
  padding: 1rem;
  border-radius: 8px;
  color: #FF5A5F;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-confirm, .btn-primary {
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

.btn-confirm:hover, .btn-primary:hover {
  background-color: #5A2DE9;
}

.btn-confirm:active, .btn-primary:active {
  transform: translateY(1px);
}

.btn-confirm:disabled {
  background-color: #B9A7FF;
  cursor: not-allowed;
}

@media (max-width: 560px) {
  .confirm-email-card {
    padding: 1.5rem;
    border-radius: 8px;
    max-width: 100%;
    margin: 0 1rem;
  }

  .confirm-email-title {
    font-size: 1.5rem;
  }
}
</style>