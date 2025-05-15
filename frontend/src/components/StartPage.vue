<template>
  <div>
    <NavBar
      :default-page="currentPage"
      @page-changed="handlePageChange"
      @logout="handleLogout"
    />

    <div className="content">
      <!-- Отображаем нужный компонент в зависимости от выбранной страницы -->
      <Students v-if="currentPage === 'students'"/>
      <GroupsComponent v-if="currentPage === 'groups'" />
      <TemplateComponent v-if="currentPage === 'template'" />
      <!-- Здесь будут другие компоненты для остальных страниц -->
    </div>
  </div>
</template>

<script setup>
import {ref, computed} from 'vue';
import NavBar from "@/components/NavBar.vue";
import Students from "@/components/StudentsComponent.vue"; // Импортируем компонент Students
import {watch} from "vue";
import GroupsComponent from "@/components/GroupsComponent.vue";
import TemplateComponent from "@/components/TemplateComponent.vue";

// Текущая страница
const currentPage = ref(localStorage.getItem('page') ? localStorage.getItem('page') :'schedule');

// Вычисляемый заголовок страницы
const pageTitle = computed(() => {
    switch (currentPage.value) {
        case 'schedule':
            return 'Расписание';
        case 'template':
            return 'Шаблон';
        case 'students':
            return 'Студенты';
        case 'groups':
            return 'Группы';
        case 'profile':
            return 'Профиль';
        default:
            return 'ЧасоГраф';
    }
});


watch(pageTitle, (newTitle) => {
  document.title = newTitle;
}, { immediate: true });


// Обработчики событий
const handlePageChange = (page) => {
    currentPage.value = page;
    localStorage.setItem('page', page)
    console.log(`Переход на страницу: ${page}`);
};

</script>

<script>
import axios from "axios";

export default {
    methods: {
        async handleLogout() {
            try {
                await axios.post(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/logout/`, {
                    refresh: localStorage.getItem('ref_token')
                }, {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}` // Отправляем access токен в заголовке Authorization
                    }
                });
                localStorage.clear();
                this.$router.push('/login')
            } catch (error) {
                console.log("Ошибка выхода");
            }
        }
    }
}
</script>

<style scoped>
.content {
    padding: 2rem;
    font-family: 'Open Sans', sans-serif;
}
</style>