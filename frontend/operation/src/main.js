// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
//use iview
import iView from 'iview'
import 'iview/dist/styles/iview.css'
Vue.use(iView)

// element-ui
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-default/index.css'

import App from './App'
import { createRouter } from './router'
import { createStore } from './store'

import '@/assets/plugins/semantic/semantic.min.js'
import '@/assets/plugins/semantic/semantic.min.css'

import '@/assets/js/theme.js'
import '@/assets/js/zhuge.js'
import '@/assets/js/jquery.sparkline.min.js'

// use element
Vue.use(ElementUI)

Vue.config.productionTip = false

const router = createRouter()
const store = createStore()

/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    store,
    template: '<App/>',
    components: { App }
})
