<template>
    <div id="area">
        <div v-if="areaListShow">
            <div>
                <span style="padding-right:50px;">区域列表</span>
                <button class="ui basic small button" @click="createAreaClick">
                    <i class="icon add"></i>新建区域
                </button>
            </div>
            <div class="ui divider"></div>
            <tree-grid 
                :items='areaList' 
                :columns='columns'
                @on-row-click='rowClick'
            ></tree-grid>
            <div class="ui mini modal deletearea">
                <i class="close icon"></i>
                <div class="content">
                    <div class="description">
                        <p>确认删除？</p>
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
        <div v-else>
            <h4 v-if="isCreate" @click="treeBoxStatus.area.show=false">新建区域</h4>
            <h4 v-else @click="treeBoxStatus.area.show=false">编辑区域</h4>
            <div @click="treeBoxStatus.area.show=false">
                名称*：
                <div class="ui input">
                    <input type="text" v-model="areaName">
                </div>
            </div>
            <div class="area-describe" @click="treeBoxStatus.area.show=false">
                描述：
                <textarea rows="3" cols="20" v-model="areaDesc"></textarea>
            </div>
            <div class="area-select">
                <span>上级区域*：</span>
                <div class="custom-selection" id="customSelection" @click="showTreeBox('area')">
                    <div class="item" id="area">
                        <p v-show="selectedAreaList.length <= 0">----</p>
                        <el-tag
                            class="area-tag"
                            v-for="item in selectedAreaList"
                            :key="item.label"
                            :closable="true"
                            type="primary"
                            @close="deleteOption('area', item.id)">
                            {{item.label}}
                        </el-tag>
                    </div>
                    <i :class="treeBoxStatus.area.customSelectionIcon"></i>
                </div>
                <div class="custom-tree-box" v-show="treeBoxStatus.area.show">
                    <el-input placeholder="输入关键字进行过滤" v-model="filterAreaText"></el-input>
                        <el-tree
                            :data="areaSelectList"
                            :props="areaTreeDefaultProps"
                            show-checkbox
                            node-key="id"
                            ref="area"
                            @check-change="getCheckedNode"
                            :filter-node-method="filterNode"
                            :default-checked-keys='selectedAreaIdArr'
                            check-strictly
                            default-expand-all
                        >
                        </el-tree>
                </div>
            </div>
            <div class="last-area" @click="treeBoxStatus.area.show=false">
                <span>末端区域：</span>
                <el-checkbox v-model="lastAreaChecked"></el-checkbox> 
            </div>
            <div class="search-store" v-show="lastAreaChecked" @click="treeBoxStatus.area.show=false">
                <span style="padding-right:50px;">勾选店铺</span>
                <div class="ui icon input">
                    <input type="text" placeholder="Search..." v-model="searchStore">
                    <i class="search icon"></i>
                </div>
            </div>
            <div class="ui segment" v-show="lastAreaChecked" @click="treeBoxStatus.area.show=false">
                <table class="ui striped sortable celled table">
                    <thead>
                        <tr class="center aligned">
                            <th>
                                <input type='checkbox' style="width:18px;height:18px;" class="storeCheckAll" v-model="allChecked">
                            </th>
                            <th>上级店铺</th>
                            <th>店名</th>
                            <th>地址</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr class="center aligned" v-for="storeItem in storeList">
                            <td>
                                <input type='checkbox' style="width:18px;height:18px;" class="storeCheckSingle" v-model="checked" :value="storeItem.id">
                            </td>
                            <td>{{storeItem.type_name}}</td>
                            <td>{{storeItem.name}}</td>
                            <td>{{storeItem.address}}</td>
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
            </div>            
            <div class="creat-buttons" @click="treeBoxStatus.area.show=false">
                <div class="ui buttons">
                    <button class="ui positive button" v-if="isCreate" @click="createSureClick">创建</button>
                    <button class="ui positive button" v-else  @click="editorSureClick">确定</button>
                    <div class="or"></div>
                    <button class="ui button" @click="createCancelClick">取消</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import TreeGrid from '@/components/TreeGrid.vue'
    export default {
        name: 'area',
        data () {
            return {
                areaListShow: true,
                isCreate: true,
                checked: [],
                currentAreaId: 0,
                // 分页
                pages: 1,//1
                pagesArr: [],
                currentPage: 1,
                areaDesc: '',
                areaName: '',
                lastAreaChecked: false,
                searchStore: '',
                storeList: [],
                columns: [
                {
                    title: '名称',
                    key: 'label'
                }, {
                    title: '描述',
                    key: 'description'
                }, {
                    title: '创建时间',
                    key: 'create_date'
                }, {
                    title: '最后更新时间',
                    key: 'last_update'
                },{
                    title: '操作',
                    type: 'action',
                    actions: [{
                        type: 'primary',
                        text: '编辑'
                    },{
                        type: 'primary',
                        text: '删除'
                    }]
                }],
                areaList: [],
                areaSelectList: [{
                    id: 0,
                    pid: 0,
                    label: '----',
                    children: []
                }],
                 //树选择器
                treeBoxStatus: {
                    area: {
                        show: false,
                        customSelectionIcon: 'el-icon-caret-bottom',
                    },
                    store: {
                        show: false,
                        customSelectionIcon: 'el-icon-caret-bottom',
                    }
                },
                //区域树选择器
                areaTreeDefaultProps: {
                    children: 'children',
                    label: 'label'
                },
                selectedAreaList: [],
                selectedAreaIdArr:[],
                filterAreaText: '',
                selectedNodes: []
            }
        },
        computed: {
            allChecked: {
                get: function () {
                    return this.checkedCount === this.storeList.length
                },
                set: function (value) {
                    if (value) {
                        this.checked = this.storeList.map(function (item) {
                            return item.id
                        })
                    } else {
                        this.checked = []
                    }
                }
            },
            checkedCount: {
                get: function () {
                    return this.checked.length
                }
            }
        },
        watch: {
            filterAreaText(newVal) {
                this.$refs.area.filter(newVal);
            },
            searchStore (newVal) {
                var _self = this
                _self.currentPage = 1
                _self.paginationInit(_self.currentPage)
            }
        },
        components: {
            TreeGrid
        },
        mounted () {
            var _self = this
            _self.paginationInit(_self.currentPage)
            _self.init()
        },
        methods: {
            init () {
                var _self = this
                _self.areaSelectList[0].children = []
                $.ajax({
                    url: '/api/manage/v0/area',
                    type: 'get',
                    dataType: 'json',
                    success: function (data) {
                        _self.areaList = data.data
                        for (var i = 0; i < _self.areaList.length; i ++) {
                            _self.areaSelectList[0].children.push(_self.areaList[i])
                        }
                    }
                })
            },
            paginationInit (currentPage) {
                var _self = this
                _self.storeList = []
                // 分页
                $.ajax({
                    url: '/api/manage/v0/store',
                    type: 'get',
                    dataType: 'json',
                    data: {
                        per_page: 20,
                        page: currentPage,
                        search: _self.searchStore
                    },
                    success: function (data) {
                        var storeList = data.data.storeList
                        for (var key in storeList) {
                            for (var i = 0; i < storeList[key].infoList.length; i++) {
                                _self.storeList.push(storeList[key].infoList[i])
                            }    
                        }
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
            rowClick(data, event, index, text) {
                var _self = this
                if (text === '编辑') {
                    _self.editorAreaClick(data)
                } else if (text === '删除') {
                    _self.deleteAreaClick (data)
                }
            },
            // 创建区域
            createAreaClick () {
                var _self = this
                _self.areaListShow = false
                _self.isCreate = true
                _self.areaName = ''
                _self.areaDesc = ''
                _self.selectedAreaList = []
                _self.selectedAreaIdArr = []
                _self.searchStore = ''
                _self.checked = []
                _self.lastAreaChecked = false
                _self.currentPage = 1
                _self.paginationInit(_self.currentPage)
            },
            createCancelClick () {
                var _self = this
                _self.areaListShow = true
            },
            createSureClick () {
                var _self = this
                if (_self.areaName === '') {
                    alert('请将信息填写完整！')
                } else {
                    $.ajax({
                        url: '/api/manage/v0/area-store',
                        type: 'post',
                        dataType: 'json',
                        data: {
                            name: _self.areaName,
                            description: _self.areaDesc,
                            pid: _self.selectedAreaIdArr[0],
                            is_end: _self.lastAreaChecked,
                            store_ids: JSON.stringify(_self.checked)
                        },
                        success: function (data) {
                            if (data.code === 0) {
                                alert('创建区域成功！')
                                _self.init()
                            } else {
                                alert('创建区域失败！')
                            }
                            _self.areaListShow = true
                        }
                    })
                }
            },
            // 编辑区域
            editorAreaClick(row) {
                var _self = this
                _self.areaListShow = false
                _self.isCreate = false
                _self.currentAreaId = row.id
                _self.areaName = row.label
                _self.areaDesc = row.description
                _self.lastAreaChecked = row.is_end
                _self.selectedAreaIdArr = []
                _self.checked = []
                _self.currentPage = 1
                _self.paginationInit(_self.currentPage)
                _self.selectedAreaList = []
                $.ajax({
                    url: '/api/manage/v0/area-store',
                    type: 'get',
                    dataType: 'json',
                    data: {
                        area_id: _self.currentAreaId
                    },
                    success: function (data) {
                        _self.checked = data.data.store_ids
                        if (data.data.pid === 0) {
                            _self.selectedAreaIdArr.push(0)
                            _self.$refs['area'].setCheckedKeys(_self.selectedAreaIdArr)
                            _self.selectedAreaList.push({
                                id: 0,
                                label: '----'
                            })
                        } else {
                            _self.selectedAreaIdArr.push(data.data.pid)
                            _self.selectedAreaList.push({
                                id: data.data.pid,
                                label: data.data.pname
                            })
                            _self.$refs['area'].setCheckedKeys(_self.selectedAreaIdArr)
                        }
                    }
                })
            },
            editorSureClick () {
                var _self = this
                if (_self.areaName === '') {
                    alert('请将信息填写完整！')
                } else {
                    $.ajax({
                        url: '/api/manage/v0/area-store',
                        type: 'patch',
                        dataType: 'json',
                        data: {
                            id: _self.currentAreaId,
                            name: _self.areaName,
                            description: _self.areaDesc,
                            pid: _self.selectedAreaIdArr[0],
                            is_end: _self.lastAreaChecked,
                            store_ids: JSON.stringify(_self.checked)
                        },
                        success: function (data) {
                            if (data.code === 0) {
                                alert('编辑区域成功！')
                                _self.init()
                            } else {
                                alert('编辑区域失败！')
                            }
                            _self.areaListShow = true
                        }
                    })
                }
            },
            deleteAreaClick (row) {
                var _self = this
                $('.ui.mini.modal.deletearea')
                .modal({
                    closable  : false,
                    onDeny    : function(){
                        $('.ui.mini.modal.deletearea').modal('hide')
                    },
                    onApprove : function() {   
                        $.ajax({
                            url: '/api/manage/v0/area-store',
                            type: 'delete',
                            dataType: 'json',
                            data: {
                                id: row.id
                            },
                            success: function (data) {
                                if (data.code === 0) {
                                    alert('删除成功！')
                                    _self.init()
                                } else {
                                    alert('删除失败！')
                                }
                                $('.ui.mini.modal.deletearea').modal('hide')
                            }
                        })
                    }
                })
                .modal('show')
            },
            //可搜索的树选择器
            showTreeBox: function(key) {
                var _self = this
                _self.treeBoxStatus[key].show = !_self.treeBoxStatus[key].show
                _self.treeBoxStatus[key].customSelectionIcon = _self.treeBoxStatus[key].show
                ? 'el-icon-caret-top'
                : 'el-icon-caret-bottom'   
            },
            //删除已选中的标签
            deleteOption: function(ref, id) {
                var _self = this
                _self.$refs[ref].setChecked(id, false, true)
                _self.treeBoxStatus[ref].show = false
            },
            // 获取选中的节点
            getCheckedNode: function(data) { 
                var _self = this
                var selectedNodes = _self.$refs['area'].getCheckedNodes()
                if (selectedNodes.length > 1) {
                    _self.$refs['area'].setCheckedKeys([data.id])
                } else {
                    let parentNodeJson = {}
                    _self['selectedAreaList'] = []
                    // only parent node
                    selectedNodes.reverse().forEach(function(item, index) {
                        parentNodeJson[item.id] = item.label
                    })
                    for(let key in parentNodeJson) {
                        _self['selectedAreaList'].push({
                            id: key,
                            label: parentNodeJson[key]
                        })
                    }
                }
                _self.selectedAreaIdArr = []
                for (var i = 0; i < _self.selectedAreaList.length; i++) {
                    _self.selectedAreaIdArr.push(Number(_self.selectedAreaList[i].id))
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
                _self.paginationInit(_self.currentPage)
            },
            prePageClick () {
                var _self = this
                _self.currentPage = _self.currentPage - 1
                if (_self.currentPage <= 0) {
                    _self.currentPage = 1
                }
                _self.paginationInit(_self.currentPage)
            },
            nextPageClick () {
                var _self = this
                _self.currentPage = _self.currentPage - 0 + 1
                if (_self.currentPage >= _self.pages) {
                    _self.currentPage = _self.pages
                }
                _self.paginationInit(_self.currentPage)
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
    .area-describe, .area-select, .last-area, .search-store {
        margin-top: 20px;
    }
    .area-describe textarea{
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
        width: 10%;
        position: absolute;
        color: #bfcbd9;
        font-size: 12px;
        line-height: 3em;
    }

    .custom-tree-box {
        margin-top: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,.12), 0 0 6px rgba(0,0,0,.04);
        width: 300px;
        margin-left: 78px;
    }

    .custom-tree-box > .el-tree{
        padding-right: 4px;
    }
</style>
