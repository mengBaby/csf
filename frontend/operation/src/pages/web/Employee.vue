<template>
    <div id="employee">
        <div id="employee-main" v-show="viewShowFlag">
            <h3 class="ui header">账户管理</h3>
            <div class="ui horizontal divider"></div>
            <a class="add-account-set-0.7pc" @click="addAccount">
                <button class="ui blue button">+ 添加账户</button>
            </a>
            <div class="ui horizontal divider"></div>
            <div id="active-employee-table">
                <table class="ui sortable celled table">
                    <thead>
                        <tr class="center aligned">
                            <th class="ascending">序号</th>
                            <th>手机号</th>
                            <th>名字</th>
                            <th>巡查品类</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody class="center aligned">
                        <tr v-for="(item, index) in accountList">
                            <td>{{index - 0 + 1}}</td>
                            <td>{{item.phone}}</td>
                            <td>{{item.name}}</td>
                            <td class="left aligned" style="max-width: 200px">{{item.inspect_category}}</td>
                            <td><a class="edit-account-set-0.7pc" @click="editAccount(item.id,item.phone,item.name)">编辑</a> | <a class='delete delete-account-set-0.7pc' @click="deleteAccount(item.id)">删除</a></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="ui mini modal">
                <i class="close icon"></i>
                <div class="header">
                    确认删除
                </div>
                <div class="content">
                    <div class="description">
                        <p>确认删除账户？</p>
                    </div>
                </div>
                <div class="actions">
                    <div class="ui red button cancel-delete-account-v0.7pc" id="cancel_delete" @click="deleteCancel">
                        否
                    </div>
                    <div class="ui positive right labeled icon button confirm-delete-account-v0.7pc" id="confirm_delete" @click="deleteSure">
                        是
                        <i class="checkmark icon"></i>
                    </div>
                </div>
            </div>
        </div>
        <div id="employee-edit" v-show="!viewShowFlag">
            <div class="ui breadcrumb">
                <a class="section" @click="viewShowFlag=true">账户管理</a>
                <i class="right chevron icon divider"></i>
                <div class="active section" v-if="add_or_edit==='add'">添加账户</div>
                <div class="active section" v-else>编辑账户</div>
            </div>
            <div class="ui horizontal divider"></div>
            <div class="ui form">
            <div class="required field">
                <div class="field" style="max-width: 200px">
                    <label>手机号</label>
                    <input id="phone" type="text" placeholder="请输入手机号" v-model="currentEditPhone">
                </div>
                <div class="field" style="max-width: 200px">
                    <label>姓名</label>
                    <input id="user_name" type="text" placeholder="请输入姓名" v-model="currentEditName">
                </div>
            </div>
            </div>
            <div class="ui horizontal divider">
                <h4>巡查授权</h4>
            </div>
            <div v-for="catItem in inspectCategoryList" style="padding-bottom: 30px;">
                <h5>{{catItem.cat}}</h5>
                <span v-for="item in catItem.items" style="padding-right: 10px;">
                    <input type="checkbox" name="inspect_category" :value="item.id" v-model="checked"> 
                    <label>{{item.name}}</label>
                </span>
            </div>
            <div class="ui horizontal divider"></div>
            <div class="ui horizontal divider"></div>
            <div>
                <div class="ui blue submit button" @click="submitClick">提交</div>
                <div class="ui button" @click="cancelClick">取消</div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'employee',
    props: ['csId', 'sId'],
    data () {
        return {
            cs_id: this.csId,
            s_id: this.sId,
            viewShowFlag: true,
            checked: [],
            add_or_edit: '',
            accountList: [
                {
                    id: 34,
                    phone: '18611402823',
                    name: 'xiatrui',
                    inspect_category: '膨化,糖果,糕点,冲调饮品,果肉干果,小食品'
                },
                {
                    id: 39,
                    phone: '17608054956',
                    name: 'xiatrui',
                    inspect_category: '膨化,糖果,糕点,冲调饮品,果肉干果,小食品'
                }
            ],
            currentEditPhone: '',
            currentEditName: '',
            inspectCategoryList: [
                {
                    cat: '休闲食品',
                    items: [
                        {
                            id: 16,
                            name: '膨化',
                            checked: false
                        },
                        {
                            id: 17,
                            name: '糖果',
                            checked: false
                        },
                        {
                            id: 18,
                            name: '糕点',
                            checked: false
                        }
                    ]
                },
                {
                    cat: '副食调料',
                    items: [
                        {
                            id: 20,
                            name: '酒',
                            checked: false
                        },
                        {
                            id: 21,
                            name: '及食食品',
                            checked: true
                        },
                        {
                            id: 22,
                            name: '调味类',
                            checked: true
                        }
                    ]
                }
            ],
            currentAccountId: ''
        }
    },
    mounted () {
        var _self = this
    },
    methods: {
        init () {
            var _self = this
            //TODO  url
            // $.ajax({
            //     url: '',
            //     type: 'get',
            //     dataType: 'json',
            //     success: function (data) {
            //         _self.accountList = data.data
            //     }
            // })
        },
        addAccount () {
            var _self = this
            _self.viewShowFlag = false
            _self.add_or_edit = 'add'
            _self.currentEditName = ''
            _self.currentEditPhone = ''
            _self.checked = []
            //TODO  inspectCategoryList
            // $.ajax({
            //     url: '',
            //     type: 'get',
            //     dataType: 'json',
            //     success: function (data) {
            //         _self.inspectCategoryList = data.data
            //     }
            // })
        },
        editAccount (id,phone,name) {
            var _self = this
            _self.viewShowFlag = false
            _self.add_or_edit = 'edit'
            _self.currentAccountId = id
            _self.currentEditName = name
            _self.currentEditPhone = phone
            _self.checked = [16, 20, 21]
            //TODO  inspectCategoryList
            // $.ajax({
            //     url: '',
            //     type: 'get',
            //     dataType: 'json',
            //     data: {
            //        empl_id: _self.currentAccountId 
            //     },
            //     success: function (data) {
            //         _self.checked = data.data
            //     }
            // })
        },
        submitClick () {
            var _self = this
            if (_self.currentEditPhone.length !== 11) {
                alert('手机号码不规范')
                return
            }
            if (_self.currentEditName.length < 1) {
                alert('请输入正确的姓名')
                return
            }
            // $.ajax({
            //     url: '/api/v1/operation/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/employee/check_reg_info',
            //     type: 'post',
            //     dataType: 'json',
            //     data: {
            //         phone: _self.currentEditPhone
            //     },
            //     success: function (data) {
            //         if (data.msg === 1 && _self.add_or_edit === 'add') {
            //             alert('该手机号码已被使用！')
            //         } else {
            //             $.ajax({
            //                 url: '/api/v1/operation/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/employee/add',
            //                 type: 'post',
            //                 dataType: 'json',
            //                 data: {
            //                     empl_id: _self.currentAccountId,
            //                     //TODO  判断是编辑账户还是添加账户
            //                     page: _self.add_or_edit,
            //                     phone: _self.currentEditPhone,
            //                     name: _self.currentEditName,
            //                     inspect_category: _self.checked
            //                 },
            //                 success: function(data) {
            //                     _self.viewShowFlag = true
            //                 }
            //             })
            //         }
            //     }
            // })
        },
        cancelClick () {
            var _self = this
            _self.viewShowFlag = true
        },
        deleteAccount (id) {
            var _self = this
            _self.currentAccountId = id
            $('.ui.mini.modal').modal('show')
        },
        deleteSure () {
            var _self = this
            $.ajax({
                url: '/api/v1/operation/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/employee/delete',
                type: 'post',
                dataType: 'json',
                data: {
                    "empl_id": _self.currentAccountId,
                },
                success: function(data) {
                    $('.ui.mini.modal').modal('hide')
                }
            })
        },
        deleteCancel () {
            var _self = this
            $('.ui.mini.modal').modal('hide')
        }
    }
}
</script>

<style scoped>
</style>
