<template>
    <div id="app">
        <div class="float-bar">
            <div class="ui top fixed borderless menu" style="z-index:99;">
                <div class="item small-screen">
                    <img class="logo" src="~assets/images/logo.png">
                </div>
                <div id="menu-item" class="item small-screen" @click="toggle">
                    <i class="large content icon"></i>
                </div>
                <div class="item large-screen">
                    <img class="logo" src="~assets/images/logo.jpg">
                </div>
                <div class="item header-item">
                    <h3 class="ui center aligned header">超盟商超数据化运营</h3>
                </div>

                <div class="right menu">
                    <span class="item large-screen" id="username">{{ username }}，您好</span>
                    <a class="item" @click="changePwdClick">修改密码</a>
                    <router-link class="item large-screen" to="/login" @click.native="gaLogout">退出登录</router-link>

                    <div class="item small-screen">
                        <div class="ui right top pointing dropdown icon button">
                            <i class="user icon"></i>
                            <div class="menu">
                                <a class="item" href="/login">退出登录</a>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- 修改密码modal -->
                <div class="ui tiny modal change-pwd">
                    <div class="content">
                        <div>
                            <span>原密码*：</span>
                            <div class="ui input">
                                <input type="password" v-model="userOldPwd">
                            </div>
                        </div>
                        <div style="margin-top:10px;">
                            <span>新密码*：</span>
                            <div class="ui input">
                                <input type="password" v-model="userPwd" @blur="userPwd.length>=8?lengthLimit=false:lengthLimit=true">
                            </div>
                            <span v-show="lengthLimit" style="color:#ff4a0c;">至少8个字符</span>
                        </div>
                        <div style="margin-top:10px;">
                            <span>确认密码*：</span>
                            <div class="ui input">
                                <input type="password" v-model="userPwdSure" @blur="userPwdSure===userPwd?pwdWrong=false:pwdWrong=true">
                            </div>
                            <span v-show="pwdWrong" style="color:#ff4a0c;">密码确认有误</span>
                        </div>
                    </div>
                    <div class="actions">
                        <div class="ui red button cancel">
                            取消
                        </div>
                        <div class="ui positive right labeled icon button">
                            确认
                            <i class="checkmark icon"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import { setupCSRF } from '@/assets/js/utils.js'

    export default {
        data () {
            return {
                username: null,
                pwdWrong: false,
                lengthLimit: false,
                userOldPwd: '',
                userPwd: '',
                userPwdSure: '',
            }
        },

        beforeMount() {
            setupCSRF()
        },

        mounted() {
            var _self = this
            _self.username = localStorage.getItem('username')

            $.get('/api/basic/v0/menu', function(res){
                if(res.code === 0) {
                    var limits = []
                    for (var i = 0; i < res.data.length; i++) {
                        limits.push(res.data[i].description)
                    }
                    zhuge.identify(_self.username, {
                        '用户名': _self.username,
                        '权限': limits
                    })
                }
            })
            
            if(!_self.username) {
                _self.$message({
                    message: '您已掉线',
                    type: 'warning'
                })

                _self.$router.push('/login')
            }
        },

        methods: {
            toggle: function() {
                $('.left-side-bar').toggle()
            },
            //修改密码
            changePwdClick () {
                var _self = this

                ga('send', 'event', {
                    eventCategory: '修改密码',
                    eventAction: '点击修改密码'
                })

                _self.lengthLimit = false
                _self.pwdWrong = false
                 _self.userOldPwd = ''
                _self.userPwd = ''
                _self.userPwdSure = ''
                $('.ui.tiny.modal.change-pwd')
                .modal({
                    closable  : false,
                    onDeny    : function(){
                        $('.ui.tiny.modal.change-pwd').modal('hide')
                        ga('send', 'event', {
                            eventCategory: '修改密码',
                            eventAction: '取消'
                        })
                    },
                    onApprove : function() {

                        ga('send', 'event', {
                            eventCategory: '修改密码',
                            eventAction: '确定'
                        })

                        if (_self.userOldPwd === '' || _self.userPwd === '' || _self.userPwdSure === '') {
                            alert('请将信息填写完整！')
                            return false
                        } else if (_self.userPwd.length < 8 || _self.userPwd !== _self.userPwdSure) {
                            alert('密码不符合要求!')
                            return false
                        } else {
                            $.ajax({
                                url: '/api/manage/v0/user-basic-info',
                                type: 'patch',
                                dataType: 'json',
                                data: {
                                    old_password: _self.userOldPwd,
                                    password: _self.userPwd
                                },
                                success: function (data) {
                                    $('.ui.tiny.modal.change-pwd').modal('hide')
                                    if (data.code === 0) {
                                        alert('密码修改成功！')
                                    } else {
                                        alert(data.error_msg)
                                    }
                                }
                            })
                        }
                    }
                })
                .modal('show')
            },
            gaLogout () {
                ga('send', 'event', {
                    eventCategory: '系统操作',
                    eventAction: '退出登录',
                    transport: 'beacon'
                })
            }
        }
    }
</script>

<style>
    .float-bar {
        min-height: 70px;
    }

    .float-bar .logo {
        height: 45px;
        width: auto !important;
    }

    .float-bar .header-item {
        flex: 1 0 auto !important;
    }

    .float-bar .item>h3.header {
        margin: auto;
    }

    .float-bar .fixed {
        border-bottom: 3px solid #FF5422;
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
            display: none;
            z-index: 100;
            top: 50px;
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
            padding-left: 10px !important;
            padding-right: 10px !important;
        }
    }

     .left-side-bar .list .item.router-link-active {
        background-color: #3d3e40!important;
        color: #fff!important;
    }
</style>
