import {createRouter, createWebHistory} from 'vue-router'; // Импорт Vue Router для Vue 3
import LoginPage from '@/components/LoginPage.vue';
import RestorePass from "@/components/RestorePass.vue";
import RegisterPage from "@/components/RegisterPage.vue";
import EmailVerification from "@/components/EmailVerification.vue";
import RestorePassConfirm from "@/components/RestorePassConfirm.vue";
import StartPage from "@/components/StartPage.vue";

const router = createRouter({
    history: createWebHistory(), // Используем history mode
    routes: [
        {
            path: '/restore-password',
            name: 'RestorePass',
            component: RestorePass,
            meta: {forGuestsOnly: true},
        },
        {
            path: '/login',
            name: 'Login',
            component: LoginPage,
            meta: {forGuestsOnly: true}
        },
        {
            path: '/register',
            name: 'Registration',
            component: RegisterPage,
            meta: {forGuestsOnly: true}
        },
        {
            path: '/verify-email/:activationKey',
            name: 'EmailVerification',
            component: EmailVerification,
            props: route => ({
                activationKey: route.params.activationKey
            }),
            meta: {forGuestsOnly: true}
        },
        {
            path: '/pass-reset/:uid/:token',
            name: 'PasswordResetConfirm',
            component: RestorePassConfirm,
            props: route => ({
                uid: route.params.uid,
                token: route.params.token
            }),
            meta: {forGuestsOnly: true}
        },
        {
            path: '/',
            name: 'Start',
            component: StartPage,
            meta: {requiresAuth: true}
        },
    ],
});

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token');
  const isGuestRoute = to.matched.some(record => record.meta.forGuestsOnly);
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  // Если маршрут не требует авторизации — пропускаем
  if (!requiresAuth) {
    // Если пользователь на гостевом маршруте и не авторизован — пропускаем
    if (!token) return next();

    // Если пользователь авторизован, не пускаем на гостевые маршруты
    if (isGuestRoute) {
      try {
        const response = await fetch(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/check-auth/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Invalid token');

        const data = await response.json();
        if (data.is_authenticated) {
          return next('/'); // Перенаправим на главную
        }
      } catch (error) {
        localStorage.removeItem('token');
        // Остаться на текущем гостевом маршруте
      }
    }

    return next();
  }

  // Если маршрут требует авторизации
  if (!token) {
    return next('/login');
  }

  try {
    const response = await fetch(`${process.env.VUE_APP_IP_ADDRESS_BACKEND}/api/check-auth/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (!response.ok) throw new Error('Invalid token');

    const data = await response.json();
    if (data.is_authenticated) {
      return next();
    } else {
      localStorage.removeItem('token');
      return next('/login');
    }
  } catch (error) {
    console.error('Auth check error:', error);
    localStorage.removeItem('token');
    return next('/login');
  }
});

export default router;