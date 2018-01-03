<template>
    <div id="rms-add-chain">
        <div class="ui big breadcrumb">
            <router-link to="/rms" class="section">数据化运营</router-link>
            <div class="divider"> / </div>
            <router-link to="/rms/chain" class="section">连锁店管理</router-link>
            <div class="divider"> / </div>
            <div class="active section">接入连锁店</div>
        </div>

        <div class="ui segment">
            <div class="ui form input-group">
                <div class="ui grid">
                    <div class="five wide column inline field">
                        <label>连锁店名称：</label>
                        <input type="text" name="newChainName" v-model="newChainName">
                    </div>

                    <div class="three wide column use-standard inline field">
                        <label>使用标准库品类:</label>
                        <div class="ui checkbox">
                            <label></label>
                            <input type="checkbox" tabindex="0" class="hidden" v-model="useStandard">
                        </div>
                    </div>
                    <div class="four wide column ">
                        <!-- <div class="field"> -->
                            <div class="ui icon input">
                                <input type="text" placeholder="增加类型" v-model="newType">
                                <i class="inverted circular plus link icon"
                                   @click="addType"
                                ></i>
                            </div>
                        <!-- </div> -->
                    </div>
                    <div class="four wide column">
                        <div class="ui right floated primary button" @click="addStoreTableItem">
                            添加新类型<i class="right plus icon"></i>
                        </div>
                    </div>
                </div>
            </div>
            <!-- 添加连锁店-->
            <div id="addChainModal">
                <div v-for="(list, index) in storeList" :key="index" class="clearfix">
                    <div class="ui section divider"></div>
                    <div class="description">
                        <div class="ui form">
                            <div class="inline fields">
                                <div class="eight wide field">
                                    <label>店铺类型：</label>
                                    <Selection addClass="selection" name="type"
                                               defaultText="请选择" :options="typeList"
                                               v-model="list.type"
                                    ></Selection>
                                    
                                </div>
                                <div class="eight wide field">
                                    <textarea rows="1" placeholder="多条数据粘贴至此，空格加项，回车加行"
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
                    <div v-if="index >= 1" class="ui negative button delete-store" @click="deleteStoreTableItem(index)">
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
        </div>

        <!-- 确认框 -->
        <div class="ui mini modal" id="confirmModal">
            <div class="header">提示</div>
            <div class="content">
                <h4 class="ui header">
                    确认接入？
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
    name: 'rms-add-chain',
    data() {
        return {
            chainList: [],
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
            newChainName: '',
            newType: '',
        }
    },

    components: {
        'Selection': Selection
    },

    mounted() {
        this.initCheckbox()
        this.getTypeList()
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
        // 添加新类型
        addStoreTableItem: function() {
            this.storeList.push({
                type: null,
                dataStr: '',
                infoList: []
            })
        },
        // 删除店铺表格
        deleteStoreTableItem: function(index) {
            this.storeList.splice(index, 1)
        },
        //添加店铺类型
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
                            message: '新增店铺类型成功',
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
                        message: '新增店铺类型失败',
                        type: 'error'
                    })
                }
            })
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
        //确定提交
        confirm: function () {
            var self = this
            if(self.newChainName === '') {
                self.$message({
                    message: '连锁店名还没填',
                    type: 'warning'
                })

                return false
            }
            $.ajax({
                type: 'post',
                url: '/api/manage/v0/chain-store',
                dataType: 'json',
                data: {
                    chainName: self.newChainName,
                    useStandard: this.useStandard
                },

                success: function(res) {
                    if(res.code === 0) {
                        $.ajax({
                            url: '/api/manage/v0/store',
                            type: 'post',
                            dataType: 'json',
                            data: {
                                chainId: res.data.chainId,
                                storeList: JSON.stringify(self.storeList)
                            },
                            success: function (data) {
                                if(data.code === 0) {
                                    self.$message({
                                        message: '接入成功',
                                        type: 'success'
                                    })
                                } else {
                                    self.$message({
                                        message: res.error_msg,
                                        type: 'error'
                                    })
                                }
                            },
                            error: function () {
                                alert('接入失败')
                            },
                            complete: function () {
                                self.$router.push('/rms/chain')
                            }
                        })
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
    #addChainModal>.button-group {
        margin-top: 40px;
        text-align: center;
    }
</style>
