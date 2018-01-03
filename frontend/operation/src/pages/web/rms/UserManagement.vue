<template>
    <div id="rms-user-management">
        <div class="ui big breadcrumb">
            <router-link to="/rms" class="section">数据化运营</router-link>
            <div class="divider"> / </div>
            <div class="active section">用户管理</div>
        </div>

        <router-link to="/rms/add_user" class="ui button primary right floated">
            <i class="plus icon"></i>新建用户
        </router-link>

        <table class="ui celled compact table">
            <thead>
                <tr class="center aligned">
                    <th>用户ID</th>
                    <th>用户名</th>
                    <th>连锁店名</th>
                    <th>创建日期</th>
                    <th>最近更新日期</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in userListShow"
                    class="center aligned">
                    <td>{{ item.userId }}</td>
                    <td>{{ item.username }}</td>
                    <td>{{ item.chainName }}</td>
                    <td>{{ item.createDate }}</td>
                    <td>{{ item.lastLogin }}</td>
                    <td class="status-control">
                        <router-link :to="'/rms/edit_user/' + item.userId">编辑</router-link>
                        <a href="javascript:void(0)"
                           @click="changeStatus"
                           :id="item.userId"
                           :data-status="item.isActive">
                            {{ item.isActive ? '禁用' : '启用' }}
                        </a>
                    </td>
                </tr>
            </tbody>
            <tfoot>
                <tr>
                    <th colspan="6">
                        <div class="ui right floated pagination menu">
                            <a class="icon item disabled">
                                <i class="left chevron icon"></i>
                            </a>
                            <a v-for="i in listLength" class="item" @click="pageTurn">{{ i }}</a>
                            <a class="icon item disabled">
                                <i class="right chevron icon"></i>
                            </a>
                        </div>
                    </th>
                </tr>
            </tfoot>
        </table>

        <div class="ui mini modal" id="confirmModal">
            <div class="header">提示</div>
            <div class="image content">
                <h4 class="ui header">
                    确认 {{modalText}} 此用户？
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
export default {
    name: 'rms-user-management',
    data () {
        return {
            userList: [],
            userListShow: [],
            perPageItems: 10,

            modalText: ''
        }
    },

    mounted() {
        this.getUserList()
    },

    computed: {
        listLength: function() {
            if(this.userList.length !== 0) {
                return Math.ceil(this.userList.length / this.perPageItems)
            } else {
                return 1
            }
        }
    },

    methods: {
        getUserList: function() {
            var self = this

            $.get(
                '/api/manage/v0/chain-user',
                function(res){
                    if(res.code === 0) {
                        self.userList = res.data
                        self.userListShow = self.userList.slice(0, self.perPageItems)
                    }
                }
            )
        },

        changeStatus: function(e) {
            var self = this,
                status = e.target.dataset.status,
                id = e.target.id

            this.modalText = e.target.text

            $('#confirmModal').modal({
                onApprove: function() {
                    $.ajax({
                        url: '/api/manage/v0/user-status',
                        type: 'POST',
                        dataType: 'json',
                        data: {
                            userId: id,
                            isActive: status === 'true' ? false : true
                        },

                        success: function(res) {
                            if(res.code === 0) {
                                self.$message({
                                    message: '成功',
                                    type: 'success'
                                })

                                self.getUserList()
                            } else {
                                self.$message({
                                    message: res.error_msg,
                                    type: 'error'
                                })
                            }
                        },

                        error: function() {
                            self.$message({
                                message: '连接出现问题请重试',
                                type: 'error'
                            })
                        }
                    })
                }
            }).modal('show')
        },

        pageTurn: function(e) {
            var pageNum = e.target.text

            this.userListShow = this.userList.slice(this.perPageItems * (pageNum - 1),
                this.perPageItems * pageNum - 1)
        }
    }
}
</script>

<style scoped>
    .status-control > a:first-child:after{
        content: "|";
        margin-left: 2px;
    }

    .ui.table {
        margin-top: 25px;
    }

    .disabled:hover {
        cursor: not-allowed;
    }
</style>
