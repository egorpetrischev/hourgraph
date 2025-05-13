<template>
  <div class="password-reset-container">
    <div class="password-reset-card">
      <h1 class="password-reset-title">Восстановление пароля</h1>

      <div v-if="success" class="success-message">
        <div class="success-icon">✓</div>
        <p>Пароль успешно изменен. Теперь вы можете войти в систему, используя новый пароль.</p>
        <button @click="goToLogin" class="primary-button">Перейти к входу</button>
      </div>

      <form v-else @submit.prevent="resetPassword" class="password-reset-form">
        <div class="form-group">
          <label for="password">Новый пароль</label>
          <input
            id="password"
            type="password"
            v-model="password"
            :class="{'input-error': errors.password}"
            @input="validatePassword"
          />
          <p v-if="errors.password" class="error-text">{{ errors.password }}</p>
        </div>

        <div class="form-group">
          <label for="passwordConfirm">Подтвердите пароль</label>
          <input
            id="passwordConfirm"
            type="password"
            v-model="passwordConfirm"
            :class="{'input-error': errors.passwordConfirm}"
            @input="validatePasswordConfirm"
          />
          <p v-if="errors.passwordConfirm" class="error-text">{{ errors.passwordConfirm }}</p>
        </div>

        <div v-if="serverError" class="server-error">
          <p>{{ serverError }}</p>
        </div>

        <button
          type="submit"
          class="primary-button"
          :disabled="isSubmitting || !isFormValid"
        >
          <span v-if="isSubmitting">Изменение...</span>
          <span v-else>Изменить пароль</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PasswordReset',
  props: {
    uid: {
      type: String,
      required: true
    },
    token: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      password: '',
      passwordConfirm: '',
      errors: {
        password: '',
        passwordConfirm: ''
      },
      serverError: '',
      isSubmitting: false,
      success: false
    };
  },
  computed: {
    isFormValid() {
      return this.password &&
             this.passwordConfirm &&
             !this.errors.password &&
             !this.errors.passwordConfirm;
    }
  },
  methods: {
    validatePassword() {
      this.errors.password = '';

      if (this.password.length === 0) {
        this.errors.password = 'Пароль обязателен';
      } else if (this.password.length < 8) {
        this.errors.password = 'Пароль должен содержать минимум 8 символов';
      }

      // Если подтверждение пароля уже введено, проверим совпадение
      if (this.passwordConfirm) {
        this.validatePasswordConfirm();
      }
    },

    validatePasswordConfirm() {
      this.errors.passwordConfirm = '';

      if (this.passwordConfirm.length === 0) {
        this.errors.passwordConfirm = 'Подтверждение пароля обязательно';
      } else if (this.password !== this.passwordConfirm) {
        this.errors.passwordConfirm = 'Пароли не совпадают';
      }
    },

    async resetPassword() {
      if (!this.isFormValid) return;

      this.isSubmitting = true;
      this.serverError = '';

      try {
        await axios.post(`http://${process.env.VUE_APP_IP}:8000/api/password/reset/confirm/` + this.uid + '/' + this.token + '/', {
          uidb64: this.uid,
          token: this.token,
          new_password: this.password
        });

        this.success = true;
      } catch (error) {
        if (error.response && error.response.data) {
          if (error.response.data.token) {
            this.serverError = 'Недействительный или просроченный токен.';
          } else if (error.response.data.new_password) {
            this.errors.password = error.response.data.new_password[0];
          } else {
            this.serverError = 'Произошла ошибка при сбросе пароля. Пожалуйста, попробуйте снова.';
          }
        } else {
          this.serverError = 'Проблема с сервером. Пожалуйста, попробуйте позже.';
        }
      } finally {
        this.isSubmitting = false;
      }
    },

    goToLogin() {
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Open+Sans:wght@400;600&display=swap');

.password-reset-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #FDFCFF;
  font-family: 'Manrope', sans-serif;
  color: #2D2D2D;
  padding: 20px;
}

.password-reset-card {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(110, 58, 255, 0.1);
  padding: 32px;
  width: 100%;
  max-width: 480px;
}

.password-reset-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
  text-align: center;
  color: #2D2D2D;
}

.password-reset-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-family: 'Open Sans', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: #2D2D2D;
}

input {
  font-family: 'Manrope', sans-serif;
  padding: 12px 16px;
  border: 1px solid #E0E0E0;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s;
}

input:focus {
  outline: none;
  border-color: #6E3AFF;
  box-shadow: 0 0 0 3px rgba(110, 58, 255, 0.1);
}

.input-error {
  border-color: #FF5A5F;
}

.primary-button {
  background-color: #6E3AFF;
  color: white;
  font-family: 'Manrope', sans-serif;
  font-weight: 600;
  font-size: 16px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 8px;
}

.primary-button:hover {
  background-color: #5E29FF;
}

.primary-button:disabled {
  background-color: #B8A8FF;
  cursor: not-allowed;
}

.error-text {
  color: #FF5A5F;
  font-size: 14px;
  margin: 0;
}

.server-error {
  background-color: rgba(255, 90, 95, 0.1);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
}

.server-error p {
  color: #FF5A5F;
  margin: 0;
  font-size: 14px;
}

.success-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
}

.success-icon {
  background-color: #00C897;
  color: white;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  margin-bottom: 8px;
}

.success-message p {
  color: #2D2D2D;
  font-size: 16px;
  margin: 0;
  line-height: 1.5;
}
</style>