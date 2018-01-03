import Vue from 'vue'
import Router from 'vue-router'

// web pages
import Nav from '@/pages/web/Nav'
import Transfer from '@/pages/web/Transfer'

// web mgmt
import MgmtNav from '@/pages/mgmt/MgmtNav'

// web rms
import RmsTransfer from '@/pages/web/rms/Transfer'

function route(path, name, url) {
    return {
        path: path,
        name: name,
        component: resolve => import (`@/pages/${url}.vue`).then(resolve)
    }
}

Vue.use(Router)

export function createRouter() {
    const router = new Router({
        mode: 'history',
        routes: [
            {
                path: '*',
                redirect: '/operation'
            },
            {
                path: '/',
                redirect: '/login'
            },
            route('/login', 'login', 'web/Login'),
            {
                path: '/operation',
                component: Nav,
                children: [
                    route('', 'operation', 'web/Welcome'),
                    {
                        path: 'store/:s_id',
                        component: Transfer,
                        children: [
                            route('sales_trend', 'sales_trend', 'web/Sales'),
                            route('category_trend', 'category_trend', 'web/CategoryTrend'),
                            route('ring_analysis', 'ring_analysis', 'web/CategoryLink'),
                            route('loss', 'loss', 'web/Loss'),
                            route('abnormal', 'abnormal', 'web/Abnormal'),
                            route('similar', 'Similar', 'web/Similar'),
                            route('price_belt', 'price_belt', 'web/Price'),
                            route('acceptance', 'acceptance', 'web/Acceptance'),
                            route('advnet', 'advnet', 'web/Advnet'),
                            route('employee', 'employee', 'web/Employee'),
                            route('overview', 'overview', 'web/Overview'),
                            route('report', 'report', 'web/DataReport'),
                        ]
                    }
                ]
            },
            {
                path: '/management',
                component: MgmtNav,
                children: [
                    route('', 'management', 'web/Welcome'),
                    {
                        path: 'manager',
                        component: Transfer,
                        children: [
                            route('area', 'area', 'mgmt/Area'),
                            route('role', 'role', 'mgmt/Role'),
                            route('user', 'user', 'mgmt/User'),
                        ]
                    }
                ]
            },
            {
                path: '/rms',
                component: RmsTransfer,
                children: [
                    route('', 'home', 'web/rms/Home'),
                    route('user', 'rms_user', 'web/rms/UserManagement'),
                    route('edit_user/:user_id', 'edit_user', 'web/rms/editUser'),
                    route('add_user', 'add_user', 'web/rms/addUser'),
                    route('chain', 'chain', 'web/rms/ChainManagement'),
                    route('edit_chain/:chain_id', 'edit_chain', 'web/rms/editChain'),
                    route('add_chain', 'add_chain', 'web/rms/addChain'),
                    route('store', 'store', 'web/rms/StoreManagement'),
                ]
            }
        ]
    })

    router.beforeEach((to, from, next) => {
        next()

        // fix 切换不同门店的同一页面，数据不刷新
        if(to.name === from.name && to.params.s_id !== from.params.s_id) {
            window.location.reload()
        }
    })

    return router
}
