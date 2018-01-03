<template>
    <div id="nav">
        <TopNav></TopNav>

        <div class="ui divided items" v-show="storeMenuShow" id="storeMenu" @mouseover="storeMenuOver" @mouseout="storeMenuOut">
            <div class="item">
                <div class="content">
                    <div class="ui horizontal list store-menu">
                        <div class="item" v-for="item in storeList">
                            <div class="content">
                                <a :id="item.id" @click="switchStore">{{ item.name }}</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="left-side-bar">
            <div class="ui left vertical inverted large menu">
                <router-link
                    @click.native="zhugeClick(item.description)"
                    class="item"
                    v-for="item in topTitleList"
                    :key="item.route"
                    :class="item.route + '-v1.0pc'"
                    :to="'/operation/store/'+ activeStore.id + '/' + item.route"
                >{{ item.description }}</router-link>

                <div class="ui dropdown item active-store" id="activeStoreItem"
                     @mouseover="activeStoreItemOver" @mouseout="activeStoreItemOut">
                    {{ activeStore.name }}
                    <i class="dropdown icon" v-show="iconShow"></i>
                </div>

                <router-link
                    @click.native="zhugeClick(item.description)"
                    class="item"
                    v-for="item in otherTitleList"
                    :key="item.route"
                    :class="item.route + '-v1.0pc'"
                    :to="'/operation/store/'+ activeStore.id + '/' + item.route
                ">{{ item.description }}</router-link>
            </div>
        </div>

        <div class="main-content">
            <div class="ui container">
                <router-view></router-view>
            </div>
        </div>
    </div>
</template>

<script>
import TopNav from '@/components/TopNav.vue'

export default {
    name: 'nav',
    data () {
        return {
            titleList: [],
            top: [
                'overview',
                'report'
            ],
            topTitleList: [],
            otherTitleList: [],

            storeMenuShow: false,
            storeMenuHover: false,
            storeList: [],

            activeStore: this.$store.state.activeStore,

            iconShow: true,
            timer: null
        }
    },

    components: {
        'TopNav': TopNav
    },

    mounted () {
        this.init()
        this.getStoreList()
    },

    methods: {
        init: function () {
            var _self = this
            $('.ui.accordion').accordion()
            $('.ui.dropdown').dropdown()

            _self.active()
        },
        activeStoreItemOver () {
            var _self = this

            var targetItem = $('#activeStoreItem'),
                storeMenu = $('#storeMenu')

            var left = targetItem.parent().width()
            // var top =targetItem[0].getBoundingClientRect().top

            if(_self.storeList.length <= 1) {
                return false
            }

            storeMenu.css({
                'left': (left - 10) + 'px'
            })

            clearTimeout(_self.timer)
            _self.storeMenuShow = true
        },
        activeStoreItemOut () {
            var _self = this
            _self.timer = setTimeout(function () {
                _self.storeMenuShow = false
            },500)
        },
        storeMenuOver () {
            var _self = this
            clearTimeout(_self.timer)
            _self.storeMenuShow = true
        },
        storeMenuOut () {
            var _self = this
            _self.timer = setTimeout(function () {
                _self.storeMenuShow = false
            },500)
        },
        zhugeClick (name) {
            zhuge.track(name)
            ga('send', 'event', '侧边栏', '选择' + name)
        },
        active: function () {
            var activeTitle = $('.router-link-active').eq(0)

            activeTitle.addClass('active')
            activeTitle.siblings().removeClass('active')

            activeTitle.parents('.content').addClass('active')
            activeTitle.parents('.item').find('.title').addClass('active')
        },

        getStoreList: function() {
            var _self = this

            $.get('/api/basic/v0/store', function(res){
                if(res.code === 0) {
                    _self.storeList = res.data

                    _self.iconShow = _self.storeList.length <= 1 ? false : true

                    _self.getActiveStore()
                } else {
                    _self.$message({
                        message: res.error_msg,
                        type: 'error'
                    })
                }
            })

            $.get('/api/basic/v0/menu', function(res){
                if(res.code === 0) {
                    _self.titleList = res.data

                    _self.topTitleList = _self.titleList.filter((title) => {
                        return _self.top.indexOf(title.route) !== -1
                    })

                    _self.otherTitleList = _self.titleList.filter((title) => {
                        return _self.top.indexOf(title.route) === -1
                    })
                } else {
                    _self.$message({
                        message: res.error_msg,
                        type: 'error'
                    })
                }
            })
        },

        switchStore: function(e) {
            var _self = this
            _self.$store.state.activeStore = _self.activeStore = {
                id: e.target.id,
                name: e.target.text
            }
            // 切换店铺后跳转到 销售趋势
            _self.$router.push('/operation/store/'+ _self.activeStore.id +'/sales_trend')

            zhuge.track('店铺选择', {
                '店铺名': e.target.text
            })
            ga('send', 'event', '侧边栏', '选择店铺', e.target.text)
        },

        getActiveStore: function() {
            var _self = this
            var storeId = _self.$route.params.s_id

            if(storeId) {
                // 当页刷新 从route获取
                var filterStore = _self.storeList.filter((option) => {
                    return option.id.toString() === storeId
                })

                if(filterStore.length > 0) {
                    _self.$store.state.activeStore = _self.activeStore = {
                        id: filterStore[0].id,
                        name: filterStore[0].name
                    }
                }
            } else {
                // 登录进站 选第一个
                _self.$store.state.activeStore = _self.activeStore = {
                    id: _self.storeList[0].id,
                    name: _self.storeList[0].name
                }
            }
        }
    }
}
</script>

<style scoped>
    @media (max-width:1336px) {
        .left-side-bar .menu {
            width: 15rem !important;
        }
    }

    @media (min-width:769px) {
        .small-screen {
            display: none !important;
        }
    }

    @media (max-width:768px) {
        .large-screen {
            display: none !important;
        }

        .float-bar {
            min-height: 60px;
        }

        .left-side-bar {
            z-index: 100;
            top: 50px;

            display: none;
        }

        .main-content {
            margin-left: 0rem !important;
        }

        .float-bar .logo {
            height: 25px;
        }

        .float-bar .icon {
            cursor: pointer !important;
        }
    }

    @media (max-width:320px) {
        .float-bar .item {
            padding-right: 10px !important;
            padding-left: 10px !important;
        }
    }

    .left-side-bar {
        max-width: 15rem;
        height: 100%;
        height:    -moz-calc(100% - 60px);
        height: -webkit-calc(100% - 60px);
        height:         calc(100% - 60px);

        position: fixed;
        top: 65px;
        left: 0;
    }

    .left-side-bar > div {
        overflow-y: scroll;
    }

    .left-side-bar .menu {
        height: 100%;

        border-left-width: 0;
        border-radius: 0 !important;
    }

    .left-side-bar .list .item {
        padding: .25rem 0 .25rem 2rem !important;

        color: '#d0d5de';
    }

    .left-side-bar .list .item:hover {
        color: '#da6666' !important;
    }

    .main-content {
        margin-left: 15rem;
        padding: 1rem;
    }

    .left-side-bar .item.router-link-active {
        color: #fff!important;
        background-color: #3d3e40!important;
    }

    .ui.divided.items {
        width: 700px;
        min-height: 200px;
        padding: 15px;

        position: fixed;
        z-index: 1001;
        top: 47px;

        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: #fff;
        box-shadow: 0 2px 4px 0 rgba(0,0,0,.12), 0 0 6px 0 rgba(0,0,0,.04);
    }

    .ui.horizontal.list > .item {
        margin: .8em 1.5em;
    }

    .ui.horizontal.list.store-menu > .item:first-child {
        margin-left: 1.4em !important;
    }

    .ui.dropdown.item.active-store {
        font-weight: bold;
    }
</style>
