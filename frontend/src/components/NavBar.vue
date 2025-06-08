<!-- NavBar.vue -->
<template>
  <nav class="navbar">
    <div class="nav-logo">ЧасоГраф</div>

    <button class="hamburger" :class="{ active: menuActive }" @click="toggleMenu">
      <span></span>
      <span></span>
      <span></span>
    </button>

    <div class="nav-container" :class="{ active: menuActive }">
      <div class="nav-links">
        <a href="#" class="nav-link" :class="{ active: currentPage === 'schedule' }" @click="setPage('schedule')">Расписание</a>
        <a href="#" class="nav-link" :class="{ active: currentPage === 'template' }" @click="setPage('template')">Шаблон</a>
        <a href="#" class="nav-link" :class="{ active: currentPage === 'students' }" @click="setPage('students')">Студенты</a>
        <a href="#" class="nav-link" :class="{ active: currentPage === 'groups' }" @click="setPage('groups')">Группы</a>
        <a href="#" class="nav-link" :class="{ active: currentPage === 'profile' }" @click="setPage('profile')">Профиль</a>
      </div>

      <button class="logout-btn" @click.prevent="logout">Выйти</button>
    </div>

    <!-- Изменения здесь: добавляем z-index и показываем оверлей только при активном меню -->
    <div v-if="menuActive" class="mobile-overlay" @click="closeMenu"></div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

// Определяем props, которые можно передавать в компонент
const props = defineProps({
  defaultPage: {
    type: String,
    default: 'schedule'
  }
});

// Определяем события, которые будет генерировать компонент
const emit = defineEmits(['page-changed', 'logout']);

// Реактивные переменные
const currentPage = ref(props.defaultPage);
const menuActive = ref(false);

// Методы
const setPage = (page) => {
  currentPage.value = page;
  menuActive.value = false;
  emit('page-changed', page);
};

const toggleMenu = () => {
  menuActive.value = !menuActive.value;

  // Блокировка прокрутки страницы при открытом меню
  if (menuActive.value) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
};

const closeMenu = () => {
  menuActive.value = false;
  document.body.style.overflow = '';
};

const logout = () => {
  emit('logout');
};

// Автоматическое определение необходимости переключения на бургер-меню
const checkScreenSize = () => {
  if (window.innerWidth > 768 && menuActive.value) {
    closeMenu();
  }
};

// Жизненный цикл компонента
onMounted(() => {
  window.addEventListener('resize', checkScreenSize);
});

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize);
});
</script>

<style scoped>
body {
  font-family: 'Manrope', sans-serif;
  background-color: #FDFCFF;
  color: #2D2D2D;
  margin: 0;
  padding: 0;
}

.navbar {
  background-color: #F0EBFF;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  height: 70px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 1000;
}

.nav-logo {
  font-weight: 700;
  font-size: 1.5rem;
  color: #6E3AFF;
  flex-shrink: 0;
  margin-right: 2rem;
}

.nav-container {
  display: flex;
  flex-grow: 1;
  justify-content: space-between;
  align-items: center;
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #2D2D2D;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  position: relative;
  transition: color 0.2s ease;
  white-space: nowrap;
}

.nav-link:hover {
  color: #6E3AFF;
}

.nav-link.active {
  color: #6E3AFF;
    font-family: 'Manrope', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 100%;
  height: 3px;
  background-color: #6E3AFF;
  border-radius: 3px;
}

.logout-btn {
  background-color: transparent;
  border: 1px solid #6E3AFF;
  color: #6E3AFF;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-family: 'Manrope', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  margin-left: 2rem;
  flex-shrink: 0;
}

.logout-btn:hover {
  background-color: rgba(110, 58, 255, 0.08);
}

.hamburger {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 24px;
  height: 18px;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  margin-left: auto;
  z-index: 101;
}

.hamburger span {
  display: block;
  height: 2px;
  width: 100%;
  background-color: #2D2D2D;
  transition: all 0.3s ease-in-out;
}

.hamburger.active span:nth-child(1) {
  transform: translateY(8px) rotate(45deg);
}

.hamburger.active span:nth-child(2) {
  opacity: 0;
}

.hamburger.active span:nth-child(3) {
  transform: translateY(-8px) rotate(-45deg);
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 90; /* Уменьшен z-index, чтобы быть ниже, чем у модальных окон */
  opacity: 1;
  transition: opacity 0.3s ease;
}

@media (max-width: 992px) {
  .navbar {
    padding: 0 1.5rem;
  }

  .logout-btn {
    margin-left: 1.5rem;
  }
}

/* Адаптивное переключение на бургер при необходимости */
@media (max-width: 768px) {
  .navbar {
    padding: 0 1rem;
  }

  .hamburger {
    display: flex;
  }

  .nav-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100vh;
    background-color: #FDFCFF;
    flex-direction: column;
    justify-content: center;
    transform: translateX(-100%);
    transition: transform 0.3s ease-in-out;
    z-index: 100;
  }

  .nav-container.active {
    transform: translateX(0);
  }

  .nav-links {
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    margin-bottom: 3rem;
  }

  .nav-link {
    font-size: 1.2rem;
  }

  .logout-btn {
    margin-left: 0;
  }
}

@media (max-width: 480px) {
  .nav-logo {
    font-size: 1.2rem;
  }

  .nav-link {
    font-size: 1.1rem;
  }

  .logout-btn {
    width: 200px;
    text-align: center;
  }
}
</style>