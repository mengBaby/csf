import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export function createStore () {
    return new Vuex.Store({
        state: {
            activeStore: {
                name: null,
                id: null
            }
        },

        actions: {},

        mutations: {},

        getters: {}
    })
}
