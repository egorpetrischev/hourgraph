// const { defineConfig } = require('@vue/cli-service')
// module.exports = defineConfig({
//   transpileDependencies: true
// });

module.exports = {
  devServer: {
    host: '0.0.0.0', // Прослушивать все сетевые интерфейсы
    port: 3000,      // Укажите желаемый порт
  }
};