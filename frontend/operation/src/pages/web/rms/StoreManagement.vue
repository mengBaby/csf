<template>
    <div id="rms-store-management">
        <div class="ui big breadcrumb">
            <router-link to="/rms" class="section">数据化运营</router-link>
            <div class="divider"> / </div>
            <div class="active section">店铺查看</div>
        </div>
        <div style="margin-top:20px;">
            <div class="ui icon input" style="width:400px;">
                <i class="search icon"></i>
                <input type="text" placeholder="可输入店铺名/用户名/用户名称" v-model="searchWord">
            </div>
            <table class="ui celled striped table">
                <thead>
                    <tr class="center aligned">
                        <th>用户ID</th>
                        <th>店铺名</th>
                        <th>用户名</th>
                        <th>用户名称</th>
                        <th>区域</th>
                        <th>角色</th>
                        <th>创建日期</th>
                        <th>最近更新日期</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in tableData" class="center aligned">
                        <td>{{item.user_id}}</td>
                        <td>{{item.cm_name}}</td>
                        <td>{{item.username}}</td>
                        <td>{{item.first_name}}</td>
                        <td>{{item.area}}</td>
                        <td>{{item.role_name}}</td>
                        <td>{{item.date_joined}}</td>
                        <td>{{item.last_login}}</td>
                        <td>
                            <a @click="checkStore(item.user_id)">查看</a>
                        </td>
                    </tr>
                </tbody>
            </table>
            <!-- <el-pagination layout="prev, pager, next" :total="200" :page-size="20" @current-change="pageClick"></el-pagination> -->
        </div>
    </div>
</template>

<script>
    import { getCookie } from '@/assets/js/utils.js'
    export default {
        name: 'rms-store-management',
        data () {
            return {
                tableData: [],
                // currentPage: 1,
                searchWord: ''
            }
        },
        watch: {
            searchWord (newVal) {
                console.log(newVal)
                var _self = this
                // _self.currentPage = 1
                _self.init()
            }
        },
        mounted () {
            var _self = this
            _self.init()
        },
        methods: {
            init () {
                var _self = this
                $.ajax({
                    url: '/api/manage/v0/scan-store',
                    type: 'get',
                    dataType: 'json',
                    data: {
                        // page: _self.currentPage,
                        searchName: _self.searchWord

                    },
                    success: function (data) {
                        _self.tableData = data.data
                    }
                })
            },
            checkStore (id) {
                var _self = this
                document.cookie = 'userId=' + id
                _self.$router.push('/operation')
            }
            // pageClick (page) {
            //     console.log(page)
            //     _self.currentPage = page
            //     _self.init()
            // }
        }
    }
</script>

<style>
    .el-pagination {
        text-align: center;
    }
    .el-pagination .el-pager li {
        width: 40px !important;
        height: 40px !important;
        line-height: 40px !important;
    }
    .el-pagination .el-pager li.btn-quicknext, .el-pagination .el-pager li.btn-quickprev {
        line-height: 40px !important;
    }
    .el-pagination .btn-next, .el-pagination .btn-prev {
        width: 40px !important;
        height: 40px !important;
    }
</style>
