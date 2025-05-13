import { createApp } from 'vue'; // Импортируем createApp из Vue 3
import App from './App.vue';
import router from './router';

// Создаём приложение
const app = createApp(App);

// Подключаем роутер
app.use(router);

// Монтируем приложение
app.mount('#app');