<template>
    <div id="rms-edit-user">
        <div class="ui big breadcrumb">
            <router-link to="/rms" class="section">数据化运营</router-link>
            <div class="divider"> / </div>
            <router-link to="/rms/user" class="section">用户管理</router-link>
            <div class="divider"> / </div>
            <div class="active section">新建用户</div>
        </div>

        <div class="ui segment">
            <div class="ui form input-group">
                <div class="ui grid">
                    <div class="two wide column">
                        <label>用户名:</label>
                    </div>

                    <div class="four wide column edit-input">
                        <input type="text" name="username" placeholder="请输入" v-model="username">
                    </div>
                </div>

                <div class="ui grid">
                    <div class="two wide column">
                        <label>密码:</label>
                    </div>

                    <div class="four wide column edit-input">
                        <input type="password" name="password" placeholder="请输入" v-model="password">
                    </div>
                </div>

                <div class="ui grid">
                    <div class="two wide column">
                        <label>重复密码:</label>
                    </div>

                    <div class="four wide column edit-input">
                        <input type="password" name="repeatPassword" placeholder="请输入" v-model="repeatPassword">
                    </div>
                </div>

                <div class="ui grid">
                    <div class="two wide column">
                        <label>选择连锁店:</label>
                    </div>

                    <div class="four wide column edit-input">
                        <Selection addClass="selection" name="chain"
                                   defaultText="请选择" :options="chainList"
                                   textFiled="name" valueFiled="id"
                                   v-model="selectedChain"
                        ></Selection>
                    </div>
                </div>

                <div class="ui grid page-allow">
                    <div class="two wide column">
                        <label>功能权限:</label>
                    </div>

                    <div class="sixteen wide column">
                        <el-transfer
                            v-model="allocatedPages"
                            :data="pageList"
                            :props="{
                                key: 'id',
                                label: 'name'
                            }"
                            :titles="['待分配的功能', '已分配的功能']"
                        ></el-transfer>
                    </div>
                </div>
            </div>

            <div class="ui grid">
                <div class="sixteen wide column right aligned">
                    <div class="ui primary button" @click="confirm">确认</div>
                    <router-link class="ui button" to="/rms/user">取消</router-link>
                </div>
            </div>
        </div>

        <div class="ui mini modal" id="confirmModal">
            <div class="header">提示</div>
            <div class="content">
                <h4 class="ui header">
                    确认修改？
                </h4>
            </div>
            <div class="actions">
                <div class="ui green ok button">确定</div>
                <div class="ui button deny">取消</div>
            </div>
        </div>
    </div>
</template>

<script>
import Selection from '@/components/Selection.vue'

export default {
    name: 'rms-edit-user',
    data () {
        return {
            pageList: [],
            allocatedPages: [],
            chainList: [],
            selectedChain: null,
            username: '',
            password: '',
            repeatPassword: ''
        }
    },

    components: {
        'Selection': Selection
    },

    computed: {
        isNull: function() {
            return (this.selectedChain === null
                 || this.password === ''
                 || this.repeatPassword === ''
                 || this.username === ''
                 || this.allocatedPages.length <= 0)
        },

        isRepeated: function() {
            return this.password === this.repeatPassword
        }
    },

    mounted() {
        this.getChainList()
        this.getPageNameList()
    },

    methods: {
        getChainList: function() {
            var self = this

            $.get(
                '/api/manage/v0/chain-store',
                function(res) {
                    if(res.code === 0) {
                        self.chainList = res.data.map((item) => {
                            return {
                                id: item.id,
                                name: item.cm_name
                            }
                        })
                    } else {
                        self.$message({
                            message: res.error_msg,
                            type: 'error'
                        })
                    }
                }
            )
        },

        getPageNameList: function() {
            var self = this

            $.get(
                '/api/manage/v0/menu-all',
                function(res) {
                    if(res.code === 0) {
                        self.pageList = res.data.map((item) => {
                            return {
                                id: item.id,
                                name: item.description
                            }
                        })
                    } else {
                        self.$message({
                            message: res.error_msg,
                            type: 'error'
                        })
                    }
                }
            )
        },

        confirm: function() {
            var self = this

            if(this.isNull) {
                self.$message({
                    message: '所有项都是必填的哦',
                    type: 'warning'
                })
                return
            }

            if(!this.isRepeated) {
                self.$message({
                    message: '两次密码不一致',
                    type: 'warning'
                })
                return
            }

            $('#confirmModal').modal({
                onApprove: function() {
                    self.submit()
                }
            }).modal('show')
        },

        submit: function() {
            var self = this

            $.ajax({
                url: '/api/manage/v0/chain-user',
                dataType: 'json',
                type: 'POST',
                data: {
                    chainId: this.selectedChain,
                    password: this.password,
                    username: this.username,
                    selectedMenu: JSON.stringify(this.allocatedPages)
                },

                success: function(data) {
                    if(data.code === 0) {
                        self.$message({
                            message: '添加成功',
                            type: 'success'
                        })
                    } else {
                        self.$message({
                            message: data.error_msg,
                            type: 'error'
                        })
                    }

                    self.$router.push('/rms/user')
                },
                error: function() {
                    self.$message({
                        message: '连接出现问题，请重试',
                        type: 'error'
                    })
                }
            })
        }
    }
}
</script>

<style scoped>
    .ui.form.input-group {
        margin-top: 15px;
    }

    .ui.form.input-group > .ui.grid:not(.page-allow) label {
        line-height: 38px;
    }

    .ui.grid .edit-input {
        padding-left: 0;
    }

    .page-allow .ui.card {
        height: 300px;
    }

    .page-allow .ui.buttons {
        margin-top: 112px;
    }

    .page-allow  .ui.checkbox.select-all label{
        color: #2185d0;
    }

    .ui.dropdown.selection {
        width: 100%;
    }
</style>
