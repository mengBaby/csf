<template>
    <div class="login">
        <div class="login-wrapper">
            <div class="login-logo">
                <img src="~assets/images/logo.jpg" alt="logo">
            </div>

            <div class="login-list">
                <div class="input-box">
                    <input type="text" name="username"
                           class="username" placeholder="用户名"
                           v-model="username"
                           @keyup.enter="loginSubmit">
                    <input type="password" name="password"
                           placeholder="密码" v-model="password"
                           @keyup.enter="loginSubmit">

                    <div class="warning">
                        <p>{{ warnMessage }}</p>
                    </div>

                    <input class="submit login_entry_all_v2" type="submit" value="登陆" @click="loginSubmit">
                </div>
            </div>
        </div>

        <div class="sign-feedback" v-show="show">
            <p class="text">登录失败</p>
            <p class="btn-box">
                <span @click="show = false">确定</span>
            </p>
        </div>
    </div>
</template>

<script type="text/babel">
    import { getCookie } from '@/assets/js/utils.js'

    export default {
        name: 'login',

        data() {
            return {
                username: '',
                password: '',
                warnMessage: '',
                show: false
            }
        },

        mounted() {
            // $.ajax({
            //     type: 'GET',
            //     url: '/api/v1'
            // })
        },

        computed: {
            isEmpty() {
                return (this.username === '' || this.password === '')
            }
        },

        methods: {
            loginRequst(req_data) {
                var self = this

                $.ajax({
                    type: 'POST',
                    url: '/api/login/v0/login',
                    dataType: 'json',
                    data: req_data,

                    success: function(data) {
                        console.log(data)
                        if(data.code === 4) {
                            self.warnMessage = '用户名或密码错误，请重新输入'
                        } else if(data.code === 0) {

                            ga('set', {
                                userId: req_data.account,
                                transport: 'beacon'
                            })
                            
                            ga('send', 'event', {
                                eventCategory: 'form',
                                eventAction: 'click',
                                eventLabel: 'login',
                                transport: 'beacon'
                            })

                            localStorage.setItem('username', req_data.account)

                            self.getUserIdentity()

                        } else {
                            self.show = true
                        }
                    },

                    error: function() {
                        self.show = true
                    }
                })
            },

            getUserIdentity: function() {
                var self = this

                $.get('/api/login/v0/identity', function(res) {
                    if(res.code === 0) {
                        console.log(getCookie('identity'))

                        switch (getCookie('identity')) {
                            case 'superuser':
                                self.$router.push('/rms')
                                break
                            case 'manager':
                                self.$router.push('/management')
                                break
                            case 'user':
                                self.$router.push('/operation')
                                break
                            default:
                                break
                        }
                    } else {
                        alert('获取用户角色失败')
                    }
                })
            },

            loginSubmit() {
                if(this.isEmpty) {
                    this.warnMessage = '用户名或密码不能为空'
                } else {
                    this.warnMessage = ''
                    this.loginRequst({
                        'account': this.username,
                        'password': this.password
                    })
                }
            }
        }
    }
</script>

<style scoped>
    .login-wrapper {
        width: 1000px;
        height: 200px;
        margin: auto;

        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;

        text-align: center;
    }

    .login-wrapper > div {
        display: inline-block;
    }

    .login-logo {
        width: 25%;
        padding: 57px 88px 58px 0;

        border-right: 1px solid #c2c1c2;
    }

    .login-logo > img {
        width: 100%;
    }

    .login-list {
        box-sizing: border-box;
        width: 35%;
        height: 200px;
        padding-left: 8%;

        vertical-align: bottom;
    }

    .login-list .input-box {
        margin-top: 4%;
    }

    .login-list .input-box > input {
        box-sizing: border-box;
        width: 100%;
        margin-bottom: 4%;
        padding: 4%;

        display: block;

        font-size: 1em;

        border: 1px solid lightgray;
        border-radius: 5px;
        outline: none;
    }

    .login-list .input-box .warning {
        width: 100%;
        height: 16px;
        margin-bottom: 4%;

        text-align: left;

        color: red;
    }

    .login-list .input-box .submit {
        color: white;
        border: 0;
        background-color: #f52;
    }

    .sign-feedback {
        width: 412px;
        height: 193px;
        margin: auto;

        position: fixed;
        z-index: 9999999999;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;

        border-radius: 8px;
        background: #fbf5f5;
    }

    .sign-feedback .text {
        width: 100%;
        height: 126px;
        margin: 0;
        padding: 0;

        font-size: 26px;
        line-height: 126px;

        text-align: center;

        color: #333;
    }

    .sign-feedback .btn-box {
        width: 100%;
        height: 66px;
        margin: 0;
        padding: 0;

        position: relative;
        bottom: 0;

        border-top: 1px solid #dbdbdb;
    }

    .sign-feedback .btn-box > span:active {
        opacity: .6;
    }

    .sign-feedback .btn-box > span {
        width: 410px;
        height: 60px;

        float: left;

        font-size: 26px;
        line-height: 60px;

        text-align: center;

        color: #ff4a0c;
    }
</style>
