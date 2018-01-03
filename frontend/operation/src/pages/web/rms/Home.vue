<template>
    <div id="rms-home" class="rms-home">
        <div class="ui text container">
            <div class="ui three column grid">
                <div class="column center aligned">
                    <router-link class="circular ui button massive basic orange" to="/rms/user">
                        用户管理
                    </router-link>
                </div>
                <div class="column">
                    <router-link class="circular ui button massive basic orange" to="/rms/chain">
                        连锁店管理
                    </router-link>
                </div>
                <div class="column">
                    <router-link class="circular ui button massive basic orange" to="/rms/store">
                        店铺查看
                    </router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .rms-home {
        margin-top: 10em;

        font-size: 18px;
    }
</style>
