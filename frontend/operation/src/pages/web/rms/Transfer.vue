<template>
    <div id="rms-transfer">
        <TopNav></TopNav>
        <div class="ui container rms-content">
            <router-view></router-view>
        </div>
    </div>
</template>

<script>
import TopNav from '@/components/TopNav.vue'

export default {
    name: 'rms-transfer',

    components: {
        'TopNav': TopNav
    },
}
</script>

<style scoped>
    .rms-content {
        margin-top: 35px;
    }
</style>

<style>
    /*ui 样式修正*/
    .el-transfer__buttons > .el-button+.el-button {
        margin: 0 auto;
    }

    .el-checkbox.el-transfer-panel__item {
        display: block;
    }

    .el-transfer-panel__list > .el-transfer-panel__item.el-checkbox+.el-checkbox {
        margin: 0;
    }
</style>
