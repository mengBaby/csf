<template>
    <div id="mgmt">
        <TopNav></TopNav>

        <div class="ui menu" style="position: fixed;left: 0;right: 0;top:62px;z-index: 99;">
            <router-link class="item" :to="'/management/manager/area'">
                区域管理
            </router-link>
            <router-link class="item" :to="'/management/manager/role'">
                角色管理
            </router-link>
            <router-link class="item" :to="'/management/manager/user'">
                用户管理
            </router-link>
        </div>

        <div class="main-content">
            <router-view class="management-info"></router-view>
        </div>
    </div>
</template>

<script>
    import TopNav from '@/components/TopNav.vue'

    export default {
        name: 'mgmt',
        data () {
            return {
            }
        },

        components: {
            'TopNav': TopNav
        },
    }
</script>

<style scoped>
    @media (min-width:769px) {
        .small-screen {
            display: none !important;
        }
    }

    @media (max-width:768px) {
        .large-screen {
            display: none !important;
        }
    }
    .main-content {
        margin-top: 50px;
    }
    .main-content .management-info {
        width: 90%;
        margin: 0 auto;
    }
    .ui.menu .router-link-active {
        color: #ff4a0c;
    }
    .ui.menu .item:hover {
        color: #ff4a0c;
    }
    .ui.menu {
        margin: 0;
    }
</style>
