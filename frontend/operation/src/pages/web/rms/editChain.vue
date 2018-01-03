<template>
    <div id="rms-edit-chain">
        <div class="ui big breadcrumb">
            <router-link to="/rms" class="section">数据化运营</router-link>
            <div class="divider"> / </div>
            <router-link to="/rms/chain" class="section">连锁店管理</router-link>
            <div class="divider"> / </div>
            <div class="active section">编辑连锁店</div>
        </div>

        <div class="ui segment">
            <div class="ui form input-group">
                <div class="ui grid">
                    <div class="five wide column inline field">
                        <label>连锁店名称：{{editChainName}}</label>
                    </div>

                    <div class="three wide column use-standard inline field">
                        <label>使用标准库品类:</label>
                        <div class="ui checkbox">
                            <label></label>
                            <input type="checkbox" tabindex="0" class="hidden" v-model="useStandard">
                        </div>
                    </div>
                    <div class="four wide column ">
                        <div class="ui icon input">
                            <input type="text" placeholder="增加类型" v-model="newType">
                            <i class="inverted circular plus link icon"
                               @click="addType"
                            ></i>
                        </div>
                    </div>
                    <div class="four wide column">
                        <div class="ui right floated primary button" @click="addStoreTableItem">
                            添加新类型<i class="right plus icon"></i>
                        </div>
                    </div>
                </div>
            </div>
            <!-- 编辑连锁店 -->
            <div id="store-info-con">
                <div v-for="list in storeTypeInfoList">
                    <h5>店铺类型:{{list.type}}</h5>
                    <table class="ui compact celled table store-table">
                        <thead>
                            <tr>
                                <th>门店超盟ID：cmid</th>
                                <th>门店连锁ID：foreign_store_id</th>
                                <th>店铺名称</th>
                                <th>店铺地址</th>
                                <th>操作</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in list.infoList">
                                <td>{{item.cmid}}</td>
                                <td>{{item.foreignStoreId}}</td>
                                <td>{{item.name}}</td>
                                <td>{{item.address}}</td>
                                <td>
                                    <a @click="editInfoClick(item.id, item.cmid, item.foreignStoreId, item.name, item.address)">编辑｜</a>
                                    <a @click="deleteInfoClick(item.id)">删除｜</a>
                                    <a @click="updateInfoClick(item.id)">更新</a>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <!-- 添加连锁店-->
            <div id="editChainModal">        
                <div class="clearfix" v-for="(list, index) in storeList" :key="index">
                    <div class="ui section divider"></div>
                    <div class="description">
                        <div class="ui form">
                            <div class="fields">
                                <div class="eight wide inline field">
                                    <label>店铺类型：</label>
                                    <Selection addClass="selection" name="type"
                                               defaultText="请选择" :options="typeList"
                                               v-model="list.type"
                                    ></Selection>
                                </div>

                                <div class="eight wide inline field">
                                    <textarea rows="1" placeholder="多条数据粘贴至此,空格加项,回车加行"
                                              v-model="list.dataStr"
                                              @input="renderStoreTable(index)"
                                    ></textarea>
                                </div>
                            </div>
                        </div>

                        <table class="ui compact celled table store-table">
                            <thead>
                                <tr>
                                    <th>门店超盟ID：cmid</th>
                                    <th>门店连锁ID：foreign_store_id</th>
                                    <th>店铺名称</th>
                                    <th>店铺地址</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="item in list.infoList">
                                    <td>
                                        <div class="ui input">
                                            <input type="text" name="cmid"
                                                   v-model="item.cmid">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="ui input">
                                            <input type="text" name="foreignStoreId"
                                                   v-model="item.foreignStoreId">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="ui input">
                                            <input type="text" name="name"
                                                   v-model="item.name">
                                        </div>
                                    </td>
                                    <td>
                                        <div class="ui input">
                                            <input type="text" name="address"
                                                   v-model="item.address">
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div v-if="index >= 1" class="ui right floated negative button delete-store" @click="deleteStoreTableItem(index)">
                        删除
                    </div>
                </div>
                <div class="ui grid button-group">
                    <div class="sixteen wide column center aligned">
                        <div class="ui primary button" @click="confirm">确认</div>
                        <router-link class="ui button" to="/rms/chain">取消</router-link>
                    </div>
                </div>
            </div>

            <!-- 编辑已有店铺信息modal -->
            <div class="ui mini modal edit-store-info" id="edit-store-info">
                <div class="header">编辑</div>
                <div class="content">
                    <div>
                        <span>门店超盟ID：</span>
                        <div class="ui input">
                            <input type="text"
                                   v-model="currentCmid">
                        </div>
                    </div>
                    <div>
                        <span>门店连锁ID：</span>
                        <div class="ui input">
                            <input type="text"
                                   v-model="currentStoreid">
                        </div>
                    </div>
                    <div>
                        <span>店铺名称：</span>
                        <div class="ui input">
                            <input type="text"
                                   v-model="currentStoreName">
                        </div>
                    </div>
                    <div>
                        <span>店铺地址：</span>
                        <div class="ui input">
                            <input type="text"
                                   v-model="currentStoreAddress">
                        </div>
                    </div>
                </div>
                <div class="actions">
                    <div class="ui green ok button">确定</div>
                    <div class="ui button deny">取消</div>
                </div>
            </div>
            <!-- 确认框 -->
            <div class="ui mini modal confirm-modal" id="confirmModal">
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
            <!-- 删除modal -->
            <div class="ui mini modal delete-modal" id="delete-modal">
                <div class="header">提示</div>
                <div class="content">
                    <h4 class="ui header">
                        确认删除？
                    </h4>
                </div>
                <div class="actions">
                    <div class="ui green ok button">确定</div>
                    <div class="ui button deny">取消</div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import Selection from '@/components/Selection.vue'

export default {
    name: 'rms-edit-chain',
    data() {
        return {
            chainId: this.$route.params.chain_id,

            useStandard: true,

            storeList: [
                {
                    type: null,
                    dataStr: '',
                    infoList: [
                        // {
                        //     cmid: '',
                        //     foreignStoreId: '',
                        //     name: '',
                        //     address: ''
                        // }
                    ]
                }
            ],
            typeList: [],
            editChainName: '',
            newType: '',

            // 已经接入的店铺数据
            storeTypeInfoList: [],
            currentCmid: '',
            currentStoreid: '',
            currentStoreName: '',
            currentStoreAddress: ''
        }
    },

    components: {
        'Selection': Selection
    },

    mounted() {
        this.initCheckbox()
        this.getTypeList()
        this.getStoreInfo(this.chainId)
    },

    methods: {
        initCheckbox: function() {
            var self = this

            $('.ui.checkbox').checkbox({
                onUnchecked: function() {
                    self.useStandard = false
                },

                onChecked: function() {
                    self.useStandard = true
                }
            })
        },
        // 获取店铺类型
        getTypeList: function() {
            var self = this

            $.get(
                '/api/manage/v0/store-type',
                function(res) {
                    if(res.code === 0) {
                        self.typeList = res.data.map((item) => {
                            return {
                                value: item.id,
                                text: item.type_name
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
        //多条数据粘贴渲染数据表格
        renderStoreTable: function(index) {
            var thisItem = this.storeList[index]

            if(thisItem.dataStr !== '') {
                var parseStr = thisItem.dataStr.replace(/\n/g, '<n>').replace(/\s+/g, '<s>')

                thisItem.infoList = []

                parseStr.split('<n>').forEach(function(str) {
                    let option = [],
                        storeItem = {}

                    option = str.split('<s>')

                    option.forEach(function(item, index) {
                        switch (index) {
                            case 0:
                                storeItem.cmid = item
                                break
                            case 1:
                                storeItem.foreignStoreId = item
                                break
                            case 2:
                                storeItem.name = item
                                break
                            case 3:
                                storeItem.address = item
                                break
                            default:
                                break
                        }
                    })

                    thisItem.infoList.push(storeItem)
                })
            }
        },
        addStoreTableItem: function() {
            this.storeList.push({
                type: null,
                dataStr: '',
                infoList: []
            })
        },

        deleteStoreTableItem: function(index) {
            this.storeList.splice(index, 1)
        },

        addType: function() {
            var self = this

            $.ajax({
                type: 'POST',
                url: '/api/manage/v0/store-type',
                dataType: 'json',
                data: {
                    type: this.newType
                },

                success: function(res) {
                    if(res.code === 0) {
                        self.$message({
                            message: '增加成功',
                            type: 'success'
                        })

                        self.getTypeList()
                    } else {
                        self.$message({
                            message: res.error_msg,
                            type: 'error'
                        })
                    }
                },

                error: function() {
                    self.$message({
                        message: '连接出现问题',
                        type: 'error'
                    })
                }
            })
        },
        // 获取已接入的连锁店店铺信息
        getStoreInfo: function(key) {
            var self = this

            $.get(
                '/api/manage/v0/store',
                { chainId: key },
                function(res) {
                    if(res.code === 0) {
                        self.editChainName = res.data.chainName
                        if(Object.keys(res.data.storeList).length > 0) {
                            self.storeTypeInfoList = []

                            for(key in res.data.storeList) {
                                self.storeTypeInfoList.push({
                                    type: res.data.storeList[key].type_name,
                                    infoList: res.data.storeList[key].infoList
                                })
                            }
                        } else {
                            self.storeTypeInfoList = []
                        }
                    } else {
                        self.$message({
                            message: res.error_msg,
                            type: 'error'
                        })
                    }
                }
            )
        },
        confirm: function () {
            var self = this
            $('#confirmModal').modal({
                onApprove: function() {
                    $.ajax({
                        type: 'POST',
                        url: '/api/manage/v0/store',
                        dataType: 'json',
                        data: {
                            chainId: self.chainId,
                            useStandard: self.useStandard,
                            storeList: JSON.stringify(self.storeList)
                        },

                        success: function(res) {
                            if(res.code === 0) {
                                self.$message({
                                    message: '添加成功',
                                    type: 'success'
                                })
                            } else {
                                self.$message({
                                    message: res.error_msg,
                                    type: 'error'
                                })
                            }
                        },

                        error: function() {
                            alert('失败')
                        },
                        complete: function () {
                            self.$router.push('/rms/chain')
                        }
                    })
                }
            }).modal('show')
        },
        editInfoClick: function (id, cmid, storeid, name, address) {
            var self = this
            self.currentCmid = cmid
            self.currentStoreid = storeid
            self.currentStoreName = name
            self.currentStoreAddress = address
            $('#edit-store-info').modal({
                onApprove: function() {
                    $.ajax({
                        url: '/api/manage/v0/chain-store-update',
                        type: 'POST',
                        dataType: 'json',
                        data: {
                            storeInfo: JSON.stringify({
                                id: id,
                                cmId: self.currentCmid,
                                foreignStoreId: self.currentStoreid,
                                storeName: self.currentStoreName,
                                address: self.currentStoreAddress
                            })
                        },
                        success: function(res) {
                            if(res.code === 0) {
                                self.getStoreInfo(self.chainId)
                                self.$message({
                                    message: '修改成功',
                                    type: 'success'
                                })
                            } else {
                                self.$message({
                                    message: res.error_msg,
                                    type: 'error'
                                })
                            }
                        },

                        error: function() {
                            alert('修改失败')
                        }
                    })
                }
            }).modal('show')
        },
        deleteInfoClick: function (id) {
            var self = this
            $('#delete-modal').modal({
                onApprove: function() {
                    $.ajax({
                        url: '/api/manage/v0/store',
                        type: 'delete',
                        dataType: 'json',
                        data: {
                            id: id
                        },
                        success: function(res) {
                            if(res.code === 0) {
                                self.getStoreInfo(self.chainId)
                                self.$message({
                                    message: '删除成功',
                                    type: 'success'
                                })
                            } else {
                                self.$message({
                                    message: res.error_msg,
                                    type: 'error'
                                })
                            }
                        },

                        error: function() {
                            alert('删除失败')
                        }
                    })
                }
            }).modal('show')
        },
        updateInfoClick: function (id) {
            var self = this
            $.ajax({
                url: '/api/manage/v0/store-data-update',
                type: 'post',
                dataType: 'json',
                data: {
                    id: id
                },
                success: function(res) {
                    if(res.code === 0) {
                        self.$message({
                            message: '更新成功',
                            type: 'success'
                        })
                    } else {
                        self.$message({
                            message: res.error_msg,
                            type: 'error'
                        })
                    }
                },

                error: function() {
                    alert('更新失败')
                }
            })
        }
    }
}
</script>

<style scoped>
    .clearfix:after {
        content: '';
        display: block;
        clear: both;
    }
    .ui.button.delete-store {
        float: right;
        margin-top: 10px;
    }
    .ui.grid .use-standard {
        margin-top: 6px;
    }
    .ui.grid .use-standard>div {
        vertical-align: middle;
    }
    .ui.form.input-group {
        margin-top: 15px;
    }
    #editChainModal>.button-group {
        margin-top: 40px;
        text-align: center;
    }
    #edit-store-info .content>div {
        margin-top: 6px;
    }
    #store-info-con>div {
        margin-top: 16px;
    }
</style>
