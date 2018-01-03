<template>
    <div id="rms-chain-management">
        <div class="ui big breadcrumb">
            <router-link to="/rms" class="section">数据化运营</router-link>
            <div class="divider"> / </div>
            <div class="active section">连锁店管理</div>
        </div>

        <router-link to="/rms/add_chain" class="ui button primary right floated">
            <i class="plus icon"></i>接入连锁店
        </router-link>

        <table class="ui celled compact table">
            <thead>
                <tr class="center aligned">
                    <th>连锁店ID</th>
                    <th>连锁店名</th>
                    <th>店铺数</th>
                    <th>创建日期</th>
                    <th>最近更新日期</th>
                    <th>操作</th>
                    <!-- <th>更新</th> -->
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in chainListShow" class="center aligned">
                    <td>{{ item.chainId }}</td>
                    <td>{{ item.chainName }}</td>
                    <td>{{ item.storeNum }}</td>
                    <td>{{ item.createDate }}</td>
                    <td>{{ item.updateDate }}</td>
                    <td>
                        <router-link :to="'/rms/edit_chain/' + item.chainId">编辑</router-link>
                    </td>
                    <!-- <td>
                        <a href="javascript:void(0)"
                           :id="item.chainId"
                           @click="confirm"
                        >更新</a>
                    </td> -->
                </tr>
            </tbody>
            <tfoot>
                <tr>
                    <th colspan="7">
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
                    确认更新数据？
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
    name: 'rms-chain-management',
    data () {
        return {
            chainList: [],
            chainListShow: [],
            perPageItems: 10,

            modalText: ''
        }
    },

    mounted() {
        this.getChainList()
    },

    computed: {
        listLength: function() {
            return Math.ceil(this.chainList.length / this.perPageItems)
        }
    },

    methods: {
        getChainList: function() {
            var self = this

            $.get(
                '/api/manage/v0/chain-store',
                function(res){
                    if(res.code === 0) {
                        self.chainList = res.data.map((item) => {
                            return {
                                chainId: item.id,
                                storeNum: item.store_num,
                                chainName: item.cm_name,
                                createDate: item.create_date,
                                updateDate: item.last_update
                            }
                        })

                        self.chainListShow = self.chainList.slice(0, self.perPageItems)
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
            // TODO 更新数据
            $('#confirmModal').modal({
                onApprove: function() {
                    // $.ajax({
                    //     url: '',
                    //     type: 'POST',
                    //     dataType: 'json',
                    //     data: {
                    //         userId: e.target.id,
                    //     },
                    //     success: function(data) {
                    //         console.log('成功')
                    //             this.getChainList()
                    //     },

                    //     error: function() {
                    //         alert('失败')
                    //     }
                    // })
                }
            }).modal('show')
        },

        pageTurn: function(e) {
            var pageNum = e.target.text

            this.chainListShow = this.chainList.slice(this.perPageItems * (pageNum - 1),
                this.perPageItems * pageNum - 1)
        }
    }
}
</script>

<style scoped>
    .ui.table {
        margin-top: 25px;
    }

    .disabled:hover {
        cursor: not-allowed;
    }
</style>
