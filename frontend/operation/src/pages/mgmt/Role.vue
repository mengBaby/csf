<template>
    <div id="role">
        <div v-if="roleListShow">
            <div>
                <span style="padding-right:50px;">角色列表</span>
                <button class="ui basic small button" @click="createRoleClick">
                    <i class="icon add"></i>新建角色
                </button>
            </div>
            <table class="ui striped orange sortable celled table">
                <thead>
                    <tr class="center aligned">
                        <th>序号</th>
                        <th>角色名称</th>
                        <th>描述</th>
                        <th>创建时间</th>
                        <th>最后更新时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="center aligned" v-for="(roleItem, index) in roleList">
                        <td>{{index - 0 + 1}}</td>
                        <td>{{roleItem.role_name}}</td>
                        <td>{{roleItem.description}}</td>
                        <td>{{roleItem.create_date}}</td>
                        <td>{{roleItem.last_update}}</td>
                        <td v-if="roleItem.role_id===1">
                            <a @click="checkRoleClick(roleItem.role_id,roleItem.role_name,roleItem.description)">查看</a>
                        </td>
                        <td v-else>
                            <p>
                                <a @click="editorRoleClick(roleItem.role_id,roleItem.role_name,roleItem.description)">编辑｜</a>
                                <a @click="deleteRoleClick(roleItem.role_id)">删除</a>
                            </p>
                        </td>
                    </tr>
                </tbody>
            </table>
            <div class="ui mini modal deleterole">
                <i class="close icon"></i>
                <div class="header">
                    确认删除
                </div>
                <div class="content">
                    <div class="description">
                        <p>确认删除角色？</p>
                    </div>
                </div>
                <div class="actions">
                    <div class="ui red button cancel">
                        否
                    </div>
                    <div class="ui positive right labeled icon button">
                        是
                        <i class="checkmark icon"></i>
                    </div>
                </div>
            </div>
        </div>
        <div v-else>
            <h4 v-if="ismanager">查看角色</h4>
            <h4 v-else-if="!ismanager&&isCreate">新建角色</h4>
            <h4 v-else-if="!ismanager&&!isCreate">编辑角色</h4>
            <div>
                名称*：
                <div class="ui input">
                    <input type="text" :readonly="ismanager" v-model="currentRoleName">
                </div>
            </div>
            <div class="role-describe">
                描述：
                <textarea rows="3" cols="20" :readonly="ismanager" v-model="currentRoleDescribe"></textarea>
            </div>
            <div>
                <span>权限*：</span>
                <div class="ui segment">
                    <p v-for="permissionItem in permissionsList">
                        <input type="checkbox" :disabled="ismanager" v-model="permissionsChecked" :value="permissionItem.id" style="margin-right:6px;">{{permissionItem.description}}
                    </p>
                </div>
            </div>
            <div class="creat-buttons">
                <button class="ui button" v-if="ismanager" @click="checkBackClick">返回</button>
                <div class="ui buttons" v-else>
                    <button class="ui positive button" @click="createSureClick" v-if="isCreate">创建</button>
                    <button class="ui positive button" @click="editorSureClick" v-else>确定</button>
                    <div class="or"></div>
                    <button class="ui button" @click="editorCancelClick">取消</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'role',
        data () {
            return {
                roleListShow: true,
                ismanager:false,
                isCreate: false,
                currentRoleId: 0,
                roleList: [],
                permissionsList: [],
                currentRoleName: '',
                currentRoleDescribe: '',
                permissionsChecked: []
            }
        },
        mounted () {
            var _self = this
            $.ajax({
                url: '/api/manage/v0/user-menu',
                type: 'get',
                dataType: 'json',
                success: function (data) {
                    _self.permissionsList = data.data
                }
            })
            _self.init()
        },
        methods: {
            init () {
                var _self = this
                $.ajax({
                    url: '/api/manage/v0/store-role',
                    type: 'get',
                    dataType: 'json',
                    success: function (data) {
                        _self.roleList = data.data
                    }
                })
            },
            checkRoleClick (currentRoleId,currentRoleName,currentRoleDescribe) {
                var _self = this
                _self.roleListShow = false
                _self.ismanager = true
                _self.currentRoleName = currentRoleName
                _self.currentRoleDescribe = currentRoleDescribe
                _self.permissionsChecked = []
                $.ajax({
                    url: '/api/manage/v0/role-menu',
                    type: 'get',
                    dataType: 'json',
                    data: {
                        role_id: currentRoleId
                    },
                    success: function (data) {
                        for (var i = 0; i < data.data.menus.length; i++) {
                            _self.permissionsChecked.push(data.data.menus[i].id)
                        }
                    }
                })
            },
            checkBackClick () {
                var _self = this
                _self.roleListShow = true
            },
            editorRoleClick (currentRoleId,currentRoleName,currentRoleDescribe) {
                var _self = this
                _self.roleListShow = false
                _self.ismanager = false
                _self.isCreate = false
                _self.currentRoleId = currentRoleId
                _self.currentRoleName = currentRoleName
                _self.currentRoleDescribe = currentRoleDescribe
                _self.permissionsChecked = []
                $.ajax({
                    url: '/api/manage/v0/role-menu',
                    type: 'get',
                    dataType: 'json',
                    data: {
                        role_id: currentRoleId
                    },
                    success: function (data) {
                        for (var i = 0; i < data.data.menus.length; i++) {
                            _self.permissionsChecked.push(data.data.menus[i].id)
                        }
                    }
                })
            },
            editorSureClick () {
                var _self = this
                if (_self.currentRoleName === '' || _self.permissionsChecked.length <= 0) {
                    alert('请将信息填写完整！')
                } else {
                    $.ajax({
                        url: '/api/manage/v0/role-menu',
                        type: 'patch',
                        dataType: 'json',
                        data: {
                            id: _self.currentRoleId,
                            name: _self.currentRoleName,
                            description: _self.currentRoleDescribe,
                            menu_ids: JSON.stringify(_self.permissionsChecked)
                        },
                        success: function (data) {
                            if (data.code === 0) {
                                alert('编辑角色成功！')
                                _self.init()
                            } else {
                                alert('编辑角色失败！')
                            }
                            _self.roleListShow = true
                        }
                    })
                }   
            },
            createSureClick () {
                var _self = this
                if (_self.currentRoleName === '' || _self.permissionsChecked.length <= 0) {
                    alert('请将信息填写完整！')
                } else {
                    $.ajax({
                        url: '/api/manage/v0/role-menu',
                        type: 'post',
                        dataType: 'json',
                        data: {
                            name: _self.currentRoleName,
                            description: _self.currentRoleDescribe,
                            menu_ids: JSON.stringify(_self.permissionsChecked)
                        },
                        success: function (data) {
                            if (data.code === 0) {
                                alert('创建角色成功！')
                                _self.init()
                            } else {
                                alert('创建角色失败！')
                            }
                            _self.roleListShow = true
                        }
                    })
                }   
            },
            editorCancelClick () {
                var _self = this
                _self.roleListShow = true
            },
            deleteRoleClick (id) {
                var _self = this
                $('.ui.mini.modal.deleterole')
                .modal({
                    closable  : false,
                    onDeny    : function(){
                        $('.ui.mini.modal.deleterole').modal('hide')
                    },
                    onApprove : function() {
                        $.ajax({
                            url: '/api/manage/v0/role-menu',
                            type: 'delete',
                            dataType: 'json',
                            data: {
                                id: id
                            },
                            success: function (data) {
                                $('.ui.mini.modal.deleterole').modal('hide')
                                if (data.code === 0) {
                                    alert('删除成功！')
                                    _self.init()
                                } else {
                                    alert('删除失败！')
                                }
                            }
                        })
                    }
                })
                .modal('show')
            },
            createRoleClick () {
                var _self = this
                _self.roleListShow = false
                _self.ismanager = false
                _self.isCreate = true
                _self.currentRoleName = ''
                _self.currentRoleDescribe = ''
                _self.permissionsChecked = []
            }
        }
    }
</script>

<style scoped>
    .role-describe {
        margin-top: 20px;
    }
    .role-describe textarea{
        width: 177px;
        height: 100px;
        vertical-align: middle;
        border: 1px solid #dbdbdb;
        border-radius: 4px;
        resize: none;
        outline: none;
    }
    .creat-buttons {
        margin-bottom: 30px;
        margin-top: 30px;
        width: 100%;
        text-align: center;
    }
</style>
