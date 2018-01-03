<template>
    <div id="user">
        <div v-if="userListShow">
            <div>
                <span style="padding-right:50px;">用户列表</span>
                <button class="ui basic small button" @click="createUserClick">
                    <i class="icon add"></i>新建用户
                </button>
            </div>
            <div class="ui divider"></div>
            <div class="filter-con">
                <span>状态：</span>
                <div class="ui selection dropdown status">
                    <input type="hidden" name="gender" :value="userStatusSelected">
                    <i class="dropdown icon"></i>
                    <div class="default text">请选择状态</div>
                    <div class="menu">
                        <div class="item" data-value='0'>全部</div>
                        <div class="item" data-value="1">活动的</div>
                        <div class="item" data-value="2">停用的</div>
                    </div>
                </div>
                <span>角色：</span>
                <div class="ui selection dropdown role">
                    <input type="hidden" name="gender" :value="userRoleSelected">
                    <i class="dropdown icon"></i>
                    <div class="default text">请选择角色</div>
                    <div class="menu">
                        <div class="item" data-value="0">全部</div>
                        <div class="item" :data-value="roleItem.role_id" v-for="roleItem in userRoleList">{{roleItem.role_name}}</div>
                    </div>
                </div>
                <span>用户：</span>
                <div class="ui input icon">
                    <input type="text" placeholder="请输入登录名或姓名" v-model="userSearch">
                    <i class="search icon"></i>
                </div>
                <a @click="filterClear">清除筛选条件</a>
            </div>
            <table class="ui striped orange sortable celled table">
                <thead>
                    <tr class="center aligned">
                        <th>登录名</th>
                        <th>姓名</th>
                        <th>手机</th>
                        <th>电子邮箱</th>
                        <th>角色</th>
                        <th>创建时间</th>
                        <th>最后登陆时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="center aligned" v-for="(userItem, index) in userList">
                        <td>{{userItem.user_login_name}}</td>
                        <td>{{userItem.user_name}}</td>
                        <td>{{userItem.user_phone}}</td>
                        <td>{{userItem.user_email}}</td>
                        <td>{{userItem.user_role}}</td>
                        <td>{{userItem.user_create_time}}</td>
                        <td>{{userItem.user_last_login_time}}</td>
                        <td v-if="userItem.is_manager">
                            <a @click="checkUserClick(userItem.user_id,userItem.user_login_name,userItem.user_name,userItem.user_phone,userItem.user_email,userItem.user_role_id_list,userItem.selected_area_list,userItem.selected_store_list)">查看</a>
                        </td>
                        <td v-else>
                            <p>
                                <a @click="editorUserClick(userItem.user_id,userItem.user_login_name,userItem.user_name,userItem.user_phone,userItem.user_email,userItem.user_role_id_list,userItem.selected_area_list,userItem.selected_store_list)">编辑｜</a>
                                <a v-if="userItem.user_status===true" @click="userStatusClick(userItem.user_id,false)">停用｜</a>
                                <a v-else-if="userItem.user_status===false"  @click="userStatusClick(userItem.user_id,true)">启用｜</a>
                                <a @click="changePwdClick(userItem.user_id)">修改密码</a>
                            </p>
                        </td>
                    </tr>
                </tbody>
            </table>
            <div style="width:100%;text-align:center;">
                <div class="ui pagination menu">
                    <a class="item" @click="prePageClick">
                        <i class="angle left large icon" style="width:0;margin:0;padding:0;"></i>
                    </a>
                    <a v-for="page in pagesArr" :class="[page===currentPage?'active item':'item']" @click="pageClick(page)">{{page}}</a>
                    <a class="item" @click="nextPageClick">
                        <i class="angle right large icon" style="width:0;margin:0;padding:0;"></i>
                    </a>
                </div>
            </div>
            <div class="ui mini modal userstatus">
                <i class="close icon"></i>
                <div class="content">
                    <div class="description">
                        <p v-if="currentUserStatus===true">确认停用？</p>
                        <p v-if="currentUserStatus===false">确认启用？</p>
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
            <div class="ui tiny modal user-change-pwd">
                <div class="content">
                    <div>
                        <span>密码*：</span>
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
        <div v-else class="user-handle-con">
            <h4 v-if="isManager" @click="treeBoxStatus.area.show=false">查看用户</h4>
            <h4 v-else-if="!isManager&&isCreate" @click="treeBoxStatus.area.show=false">新建用户</h4>
            <h4 v-else-if="!isManager&&!isCreate" @click="treeBoxStatus.area.show=false">编辑用户</h4>
            <div class="ui divider"></div>
            <div @click="treeBoxStatus.area.show=false">
                <span>登录名*：</span>
                <div class="ui input">
                    <input type="text" :readonly="isManager" v-model="currentLoginName">
                </div>
            </div>
            <div @click="treeBoxStatus.area.show=false">
                <span>姓名*：</span>
                <div class="ui input">
                    <input type="text" :readonly="isManager" v-model="currentName">
                </div>
            </div>
            <div @click="treeBoxStatus.area.show=false">
                <span>手机：</span>
                <div class="ui input">
                    <input type="text" :readonly="isManager" v-model="currentPhone">
                </div>
            </div>
            <div @click="treeBoxStatus.area.show=false">
                <span>电子邮箱：</span>
                <div class="ui input">
                    <input type="text" :readonly="isManager" v-model="currentEmail">
                </div>
            </div>
            <div class="ui divider" v-show="isCreate"></div>
            <div v-show="isCreate" @click="treeBoxStatus.area.show=false">
                <span>密码*：</span>
                <div class="ui input">
                    <input type="password" :readonly="isManager" v-model="currentUserPwd" @blur="currentUserPwd.length>=8?lengthLimit=false:lengthLimit=true">
                </div>
                <span v-show="lengthLimit" style="color:#ff4a0c;">至少8个字符</span>
            </div>
            <div v-show="isCreate" @click="treeBoxStatus.area.show=false">
                <span>确认密码*：</span>
                <div class="ui input">
                    <input type="password" :readonly="isManager" v-model="currentUserPwdSure" @blur="currentUserPwdSure===currentUserPwd?pwdWrong=false:pwdWrong=true">
                </div>
                <span v-show="pwdWrong" style="color:#ff4a0c;">密码确认有误</span>
            </div>
            <div class="ui divider"></div>
            <h5 @click="treeBoxStatus.area.show=false">权限</h5>
            <div @click="treeBoxStatus.area.show=false">
                <span>角色：</span>
                <div class="ui segment">
                    <p v-for="userRoleListItem in userRoleList">
                        <input type="checkbox" :disabled="isManager" v-model="currentRoleIdList" :value="userRoleListItem.role_id" style="margin-right:6px;">{{userRoleListItem.role_name}}
                    </p>
                </div>
            </div>
            <div>
                <span>区域：</span>
                <div class="custom-selection" id="customSelection" @click="showTreeBox('area')">
                    <div class="item" id="area">
                        <p v-show="selectedAreaList.length <= 0">请选择</p>
                        <el-tag
                            class="area-tag"
                            v-for="item in selectedAreaList"
                            :key="item.name"
                            :closable="!isManager"
                            type="primary"
                            @close="deleteOption('area', item.id)">
                            {{item.name}}
                        </el-tag>
                    </div>
                    <i :class="treeBoxStatus.area.customSelectionIcon"></i>
                </div>
                <div class="custom-tree-box" v-show="treeBoxStatus.area.show">
                    <el-input placeholder="输入关键字进行过滤" v-model="filterAreaText"></el-input>
                    <el-tree
                        :data="areaList"
                        :props="areaTreeDefaultProps"
                        show-checkbox
                        node-key="id"
                        ref="area"
                        @check-change="getCheckedNode('selectedAreaList', 'area')"
                        :filter-node-method="filterNode"
                        :default-checked-keys='selectedAreaIdArr'
                        check-strictly
                    >
                    </el-tree>
                </div>
            </div>
            <div @click="treeBoxStatus.area.show=false">
                <span>店铺：</span>
                <el-select v-model="selectedStoreIdArr" filterable multiple placeholder="请选择/可搜索" :disabled="isManager">
                    <el-option
                      v-for="item in storeList"
                      :key="item.id"
                      :label="item.name"
                      :value="item.id">
                    </el-option>
                </el-select>
            </div>
            <div class="creat-buttons" @click="treeBoxStatus.area.show=false">
                <button class="ui button" v-if="isManager" @click="checkBackClick">返回</button>
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
        name: 'user',
        data () {
            return {
                userListShow: true,
                isCreate: false,
                isManager: true,
                currentUserId: 0,
                userStatusSelected: 0,
                userRoleSelected: 0,
                currentUserStatus:true,
                lengthLimit: false,
                pwdWrong: false,
                userSearch: '',
                userPwd: '',
                userPwdSure: '',
                userList: [],
                // 当前用户信息
                currentLoginName: '',
                currentName: '',
                currentPhone: '',
                currentEmail: '',
                currentRoleIdList: [],
                currentCreateTime: '',
                currentLastLoginTime: '',
                currentUserAreaArr: [],
                currentUserStoreArr: [],
                currentUserPwd: '',
                currentUserPwdSure: '',
                // 全部角色列表
                userRoleList: [],
                // 分页
                pages: 1,//1
                pagesArr: [],
                currentPage: 1,
                //树选择器
                treeBoxStatus: {
                    area: {
                        show: false,
                        customSelectionIcon: 'el-icon-caret-bottom',
                    }
                },
                //区域树选择器
                areaList: [],
                areaTreeDefaultProps: {
                    children: 'children',
                    label: 'label'
                },
                selectedAreaList: [],
                selectedAreaIdArr:[],
                filterAreaText: '',
                // 店铺选择器
                filterStoreText: '',                
                storeList: [],
                selectedStoreList: [],
                selectedStoreIdArr: []
            }
        },
        watch: {
            filterAreaText(newVal) {
                this.$refs.area.filter(newVal);
            },
            userSearch (newVal) {
                var _self = this
                _self.currentPage = 1
                _self.init(_self.currentPage)
            }
        },
        mounted () {
            var _self = this
            $.ajax({
                url: '/api/manage/v0/store-role',
                type: 'get',
                dataType: 'json',
                success: function (data) {
                    _self.userRoleList = data.data
                }
            })
            $.ajax({
                url: '/api/manage/v0/area',
                type: 'get',
                dataType: 'json',
                success: function (data) {
                    _self.areaList = data.data
                }
            })
            $.ajax({
                url: '/api/manage/v0/store',
                type: 'get',
                dataType: 'json',
                success: function (data) {
                    var storeList = data.data.storeList
                    for (var key in storeList) {
                        for (var i = 0; i < storeList[key].infoList.length; i++) {
                            _self.storeList.push(storeList[key].infoList[i])
                        }    
                    }
                }
            })
            _self.init(_self.currentPage)
        },
        methods: {
            init (currentPage) {
                var _self = this
                $(".ui.dropdown.status").dropdown({
                    action: "activate",
                    onChange: function (value) {
                        _self.userStatusSelected = value
                        _self.currentPage = 1
                        _self.init(_self.currentPage)
                    }
                })
                $(".ui.dropdown.role").dropdown({
                    action: "activate",
                    onChange: function (value) {
                        _self.userRoleSelected = value
                        _self.currentPage = 1
                        _self.init(_self.currentPage)
                    }
                })
                $.ajax({
                    url: '/api/manage/v0/user',
                    type: 'get',
                    dataType: 'json',
                    data: {
                        per_page: 20,
                        page: currentPage,
                        status: _self.userStatusSelected,
                        role: _self.userRoleSelected,
                        user_search: _self.userSearch
                    },
                    success: function (data) {
                        _self.userList = data.data.userList
                        _self.pages = data.data.pages
                        _self.pagesArr = []
                        for (var i = 1; i <= _self.pages; i++) {
                            if (i <= 6) {
                                _self.pagesArr.push(i)
                            }
                        }
                        _self.pageStatus()
                    }
                })
            },
            // 停用启用
            userStatusClick (currentUserId,changeUserStatus) {
                var _self = this
                _self.currentUserStatus = !changeUserStatus
                $('.ui.mini.modal.userstatus')
                .modal({
                    closable  : false,
                    onDeny    : function(){
                        $('.ui.mini.modal.userstatus').modal('hide')
                    },
                    onApprove : function() {
                        $.ajax({
                            url: '/api/manage/v0/user-status',
                            type: 'post',
                            dataType: 'json',
                            data: {
                                userId: currentUserId,
                                isActive: changeUserStatus//true是启用 false是停用
                            },
                            success: function (data) {
                                $('.ui.mini.modal.userstatus').modal('hide')
                                _self.init(_self.currentPage)
                            }
                        })
                    }
                })
                .modal('show')
            },
            //修改密码
            changePwdClick (currentUserId) {
                var _self = this
                _self.lengthLimit = false
                _self.pwdWrong = false
                _self.userPwd = ''
                _self.userPwdSure = ''
                $('.ui.tiny.modal.user-change-pwd')
                .modal({
                    closable  : false,
                    onDeny    : function(){
                        $('.ui.tiny.modal.user-change-pwd').modal('hide')
                    },
                    onApprove : function() {
                        if (_self.userPwd === '' || _self.userPwdSure === '') {
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
                                    userId: currentUserId,
                                    password: _self.userPwd
                                },
                                success: function (data) {
                                    $('.ui.tiny.modal.user-change-pwd').modal('hide')
                                    if (data.code === 0) {
                                        alert('密码修改成功！')
                                    } else {
                                        alert('密码修改失败！')
                                    }
                                }
                            })
                        }
                        
                    }
                })
                .modal('show')
            },
            // 新建用户
            createUserClick () {
                var _self = this
                _self.isCreate = true
                _self.isManager = false
                _self.userListShow = false
                _self.lengthLimit = false
                _self.pwdWrong = false
                _self.treeBoxStatus['area'].show = false
                //所有信息置空
                _self.currentLoginName = ''
                _self.currentName = ''
                _self.currentPhone = ''
                _self.currentEmail = ''
                _self.currentUserPwd = ''
                _self.currentUserPwdSure = ''
                _self.currentRoleIdList = []
                _self.selectedAreaList = []
                _self.selectedStoreList = []
                _self.selectedAreaIdArr = []
                _self.selectedStoreIdArr = []
            },
            // 编辑用户
            editorUserClick (currentUserId,currentLoginName,currentName,currentPhone,currentEmail,currentRoleIdList,selectedAreaList,selectedStoreList) {
                var _self = this
                _self.isCreate = false
                _self.isManager = false
                _self.userListShow = false
                _self.currentUserId = currentUserId
                _self.treeBoxStatus['area'].show = false
                //补全用户原有信息
                _self.currentLoginName = currentLoginName
                _self.currentName = currentName
                _self.currentPhone = currentPhone
                _self.currentEmail = currentEmail
                _self.currentRoleIdList = currentRoleIdList
                _self.selectedAreaList = selectedAreaList
                _self.selectedStoreIdArr = selectedStoreList
                _self.selectedAreaIdArr = []
                for (var i = 0; i < _self.selectedAreaList.length; i++) {
                    _self.selectedAreaIdArr.push(_self.selectedAreaList[i].id)
                }
            },
            createSureClick () {
                var _self = this
                if (_self.currentLoginName === ''
                    || _self.currentName === ''
                    || _self.currentUserPwd === ''
                    || _self.currentUserPwdSure === ''
                    || _self.currentRoleIdList.length <= 0
                ) {
                    alert('请将信息填写完整！')
                } else if (_self.currentUserPwd.length < 8 || _self.currentUserPwd !== _self.currentUserPwdSure) {
                    alert('密码不符合要求!')
                } else {
                    $.ajax({
                        url: '/api/manage/v0/user',
                        type: 'post',
                        dataType: 'json',
                        data: {
                            login_name: _self.currentLoginName,
                            name: _self.currentName,
                            phone: _self.currentPhone,
                            email: _self.currentEmail,
                            password: _self.currentUserPwd,
                            role_list: JSON.stringify(_self.currentRoleIdList),
                            area_list: JSON.stringify(_self.selectedAreaIdArr),
                            store_list: JSON.stringify(_self.selectedStoreIdArr)
                        },
                        success: function (data) {
                            if (data.code === 0) {
                                alert('创建用户成功！')
                                _self.init(_self.currentPage)
                            } else {
                                alert(data.error_msg)
                            }
                            _self.userListShow = true
                        }
                    })
                }
            },
            editorSureClick () {
                var _self = this
                if (_self.currentLoginName === ''
                    || _self.currentName === ''
                    || _self.currentRoleIdList.length <= 0
                ) {
                    alert('请将信息填写完整！')
                } else {
                    $.ajax({
                        url: '/api/manage/v0/user-basic-info',
                        type: 'post',
                        dataType: 'json',
                        data: {
                            userId: _self.currentUserId,
                            username: _self.currentLoginName,
                            name: _self.currentName,
                            phone: _self.currentPhone,
                            email: _self.currentEmail
                        },
                        success: function (data) {
                            $.ajax({
                                url: '/api/manage/v0/user',
                                type: 'patch',
                                dataType: 'json',
                                data: {
                                    user_id: _self.currentUserId,
                                    role_list: JSON.stringify(_self.currentRoleIdList),
                                    area_list: JSON.stringify(_self.selectedAreaIdArr),
                                    store_list: JSON.stringify(_self.selectedStoreIdArr)
                                },
                                success: function (data) {
                                    if (data.code === 0) {
                                        alert('信息编辑成功！')
                                        _self.init(_self.currentPage)
                                    } else {
                                        alert(data.error_msg)
                                    }
                                    _self.userListShow = true
                                }
                            })
                        }
                    })
                }
            },
            editorCancelClick () {
                var _self = this
                _self.userListShow = true
            },
            // 查看用户
            checkUserClick (currentUserId,currentLoginName,currentName,currentPhone,currentEmail,currentRoleIdList,selectedAreaList,selectedStoreList) {
                var _self = this
                _self.userListShow = false
                _self.isManager = true
                _self.isCreate = false
                //补全用户原有信息
                _self.currentLoginName = currentLoginName
                _self.currentName = currentName
                _self.currentPhone = currentPhone
                _self.currentEmail = currentEmail
                _self.currentRoleIdList = currentRoleIdList
                _self.selectedAreaList = selectedAreaList
                _self.selectedStoreIdArr = selectedStoreList
                _self.selectedAreaIdArr = []
                for (var i = 0; i < _self.selectedAreaList.length; i++) {
                    _self.selectedAreaIdArr.push(_self.selectedAreaList[i].id)
                }
            },
            checkBackClick () {
                var _self = this
                _self.userListShow = true
            },
            //清除过滤器
            filterClear () {
                var _self = this
                _self.currentPage = 1
                _self.userSearch = ''
                $('.ui.selection.dropdown.status').dropdown('set value', '0')
                $('.ui.selection.dropdown.role').dropdown('set value', '0')
                _self.init(_self.currentPage)
            },
            //可搜索的树选择器
            showTreeBox: function(key) {
                var _self = this
                if (_self.isManager) {
                    _self.treeBoxStatus[key].show = false
                } else {
                    _self.treeBoxStatus[key].show = !_self.treeBoxStatus[key].show
                    _self.treeBoxStatus[key].customSelectionIcon = _self.treeBoxStatus[key].show
                    ? 'el-icon-caret-top'
                    : 'el-icon-caret-bottom'
                }    
            },
            //删除已选中的标签
            deleteOption: function(ref, id) {
                var _self = this
                _self.$refs[ref].setChecked(id, false, false)
                _self.treeBoxStatus[ref].show = false
            },
            // 获取选中的节点
            getCheckedNode: function(list, ref) {
                var _self = this
                var selectedNodes = _self.$refs[ref].getCheckedNodes()
                let parentNodeJson = {}

                _self[list] = []

                // only parent node
                selectedNodes.reverse().forEach(function(item, index) {
                    parentNodeJson[item.id] = item.label

                    // if(item.children) {
                    //     item.children.forEach(function(node, node_idx) {
                    //         delete parentNodeJson[node.id]
                    //     })
                    // }
                })

                for(let key in parentNodeJson) {
                   _self[list].push({
                        id: key,
                        name: parentNodeJson[key]
                    })
                }
                if (list === 'selectedAreaList') {
                    _self.selectedAreaIdArr = []
                    for (var i = 0; i < _self.selectedAreaList.length; i++) {
                        _self.selectedAreaIdArr.push(Number(_self.selectedAreaList[i].id))
                    }
                }
            },
            // 搜索过滤节点
            filterNode: function(value, data) {
                if (!value){
                    return true;
                }

                return data.label.indexOf(value) !== -1;
            },
            //分页
            pageClick (page) {
                var _self = this
                _self.currentPage = page
                _self.init(_self.currentPage)
            },
            prePageClick () {
                var _self = this
                _self.currentPage = _self.currentPage - 1
                if (_self.currentPage <= 0) {
                    _self.currentPage = 1
                }
                _self.init(_self.currentPage)
            },
            nextPageClick () {
                var _self = this
                _self.currentPage = _self.currentPage - 0 + 1
                if (_self.currentPage >= _self.pages) {
                    _self.currentPage = _self.pages
                }
                _self.init(_self.currentPage)
            },
            pageStatus () {
                var _self = this
                if (_self.currentPage >= 4 && _self.pages > 6) {
                    _self.pagesArr = []
                    if (_self.currentPage >= _self.pages - 2) {
                        for (var i = 0; i < _self.pages; i++) {
                            if (i < 6) {
                                _self.pagesArr.push(_self.pages - 5 + i)
                            }
                        }
                    } else {
                        for (var j = 0; j < _self.pages; j++) {
                            if (j < 6) {
                                _self.pagesArr.push(_self.currentPage - 3 + j)
                            }
                        }
                    }
                } else if (_self.currentPage < 4 && _self.pages > 6) {
                    _self.pagesArr = []
                    for (var k = 0; k < _self.pages; k++) {
                        if (k < 6) {
                            _self.pagesArr.push(1 - 0 + k)
                        }
                    }
                }
            }
        }
    }
</script>

<style scoped>
    .filter-con>div, .filter-con>button {
        margin-right: 10px;
    }
    .user-handle-con>div {
        margin-top: 10px;
    }
    .creat-buttons {
        margin-bottom: 30px;
        margin-top: 30px;
        width: 100%;
        text-align: center;
    }

    .custom-selection {
        display: inline-block;
        min-width: 300px;
        width: 300px;
        padding-right: 2px;
        line-height: 0;
        border: 1px solid #bfcbd9;
        border-radius: 4px;
        box-sizing: border-box;
        cursor: pointer;
        vertical-align: middle;
    }

    .custom-selection > .item {
        width: 93%;
        display: inline-block;
        padding-right: 2px;
        min-height: 32px;
    }

    .custom-selection > .item > p {
        padding-left: 7px;
        padding-top: 3px;
        font-size: 1em;
        color: #bfcbd9;
        line-height: 2em;
    }

    .custom-selection > .item > .area-tag {
        display: inline-block;
        padding: 2px 4px;
        margin: 4px 2px;
        color: #20a0ff;
        line-height: 20px;
        border-radius: 4px;
        border: 1px solid rgba(32,160,255,.2);
        background-color: rgba(32,160,255,.1);
    }

    .custom-selection > i {
        width: 100%;
        position: absolute;
        color: #bfcbd9;
        font-size: 12px;
        line-height: 3em;
    }

    .custom-tree-box {
        margin-top: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,.12), 0 0 6px rgba(0,0,0,.04);
        width: 300px;
        margin-left: 44px;
    }

    .custom-tree-box > .el-tree{
        padding-right: 4px;
    }
</style>
