<template>
    <div id="data-report">
        <div>
            <span>选择店铺：</span>
            <el-select v-model="storeSelected" multiple filterable placeholder="默认展示全部(可选择/可搜索)" style="margin-right:20px;width: 300px;" @change="storeChange">
                <el-option
                  v-for="item in storeList"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                  >
                </el-option>
            </el-select>
            <span>查询时间：</span>
            <el-date-picker
              v-model="dateSelected"
              type="daterange"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              :picker-options="pickerOptions"
              :editable="false"
              style="margin-right:20px;"
              @change="dateChange">
            </el-date-picker>
            <el-button type="primary" @click="submit">确定</el-button>
            <div class="ui segment">
                <div class="ui active inverted dimmer" v-show="loaderShow" style="z-index:1;">
                    <div class="ui text loader" style="position:absolute;top:40px;">Loading</div>
                </div>
                <div class="ui four column doubling stackable grid" v-show="noDataShow">
                    <div class="ui sixteen wide column center aligned">
                        <i class="big meh icon"></i>
                        <p>还没有生成数据</p>
                    </div>
                </div>
                <table class="ui basic celled table" v-if="!noDataShow && dateStoreShow">
                    <thead>
                        <tr>
                            <th>时间<i class="exchange icon" style="margin-left: 44px;" @click="exchange('store')"></i></th>
                            <th>店铺</th>
                            <th>销售额</th>
                            <th>销售量</th>
                            <th>单量</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="(dateItem,dateIndex) in timeStores">
                            <tr v-for="(storeItem,storeIndex) in dateItem.details" :class="dateIndex%2===0?'change-color':''">
                                <td :rowspan="dateItem.details.length" v-show="storeIndex===0" style="width:300px;">{{dateItem.title.split(' ')[0]}}</td>
                                <td>{{storeItem.title}}</td>
                                <td>{{storeItem.sales}}</td>
                                <td>{{storeItem.sales_volume}}</td>
                                <td>{{storeItem.traffic}}</td>
                            </tr>
                            <tr :class="dateIndex%2===0?'change-color':''" v-show="dateItem.details.length>1">
                                <td colspan="2" style="text-align: center;font-weight: bolder;">汇总</td>
                                <td>{{dateItem.sales_sum}}</td>
                                <td>{{dateItem.sales_volume_sum}}</td>
                                <td>{{dateItem.traffic_sum}}</td>
                            </tr>
                        </template>    
                    </tbody>
                </table>
                <table class="ui basic celled table" v-else-if="!noDataShow && !dateStoreShow">
                    <thead>
                        <tr>
                            <th>店铺<i class="exchange icon" style="margin-left: 44px;" @click="exchange('date')"></i></th>
                            <th>时间</th>
                            <th>销售额</th>
                            <th>销售量</th>
                            <th>单量</th>
                        </tr>
                    </thead>
                    <tbody>
                        <template v-for="(storeItem,storeIndex) in timeStores">
                            <tr v-for="(timeItem,timeIndex) in storeItem.details" :class="storeIndex%2===0?'change-color':''">
                                <td :rowspan="storeItem.details.length" v-show="timeIndex===0" style="width:300px;">{{storeItem.title}}</td>
                                <td>{{timeItem.title.split(' ')[0]}}</td>
                                <td>{{timeItem.sales}}</td>
                                <td>{{timeItem.sales_volume}}</td>
                                <td>{{timeItem.traffic}}</td>
                            </tr>
                            <tr :class="storeIndex%2===0?'change-color':''" v-show="storeItem.details.length>1">
                                <td colspan="2" style="text-align: center;font-weight: bolder;">汇总</td>
                                <td>{{storeItem.sales_sum}}</td>
                                <td>{{storeItem.sales_volume_sum}}</td>
                                <td>{{storeItem.traffic_sum}}</td>
                            </tr>
                        </template>    
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'data-report',
        data () {
            return {
                dateStoreShow: true,
                //选择店铺
                storeSelected: [],
                storeList: [],
                //选择日期
                startDate: '',
                endDate: '',
                dateSelected: [],
                pickerOptions: {
                    disabledDate(time) {
                        return time.getTime() > Date.now();
                    }
                },
                //表格
                timeStores: [],
                firstcol: 'date',
                loaderShow: false,
                noDataShow: false
            }
        },
        mounted () {
            var _self = this
            // 获取默认前一天时间
            var endDate = new Date()
            var startDate = new Date()
            var endT = endDate.getTime() - 1 * 24 * 60 * 60 * 1000
            var startT = endDate.getTime() - 1 * 24 * 60 * 60 * 1000
            endDate.setTime(endT)
            startDate.setTime(startT)
            _self.startDate = startDate.getFullYear() + '-' + (startDate.getMonth() - 0 + 1) + '-' + startDate.getDate()
            _self.endDate = endDate.getFullYear() + '-' + (endDate.getMonth() - 0 + 1) + '-' + endDate.getDate()
            _self.dateSelected = [_self.startDate,_self.endDate]
            //请求店铺列表
            $.ajax({
                url: '/api/basic/v0/store',
                type: 'get',
                dataType: 'json',
                success: function (data) {
                    _self.storeList = data.data
                }
            })
            //初始化表格
            _self.init(_self.firstcol)

        },
        methods: {
            init (firstcol) {
                var _self = this
                $.ajax({
                    url: '/api/report/v0/report',
                    type: 'get',
                    dataType: 'json',
                    data: {
                        first_col: firstcol,
                        store_ids: JSON.stringify(_self.storeSelected),
                        start_time: _self.startDate,
                        end_time: _self.endDate
                    },
                    beforeSend: function () {
                        _self.loaderShow = true
                    },
                    success: function (data) {
                        if (data.data.length > 0) {
                            _self.noDataShow = false
                            _self.timeStores = data.data
                        } else {
                            _self.noDataShow = true
                        }    
                    },
                    complete: function () {
                        _self.loaderShow = false
                    }
                })
            },
            exchange (firstcol) {
                var _self = this
                _self.dateStoreShow = !_self.dateStoreShow
                _self.firstcol = firstcol
                _self.init(_self.firstcol)

                ga('send', 'event', '数据报表', '切换')
            },
            dateChange (date) {
                var _self = this
                _self.startDate = date.split(' - ')[0]
                _self.endDate = date.split(' - ')[1]
                // _self.init(_self.firstcol)

                zhuge.track('查询时间(数据报表)', {
                    '查询时间':date
                })

                ga('send', 'event', '数据报表', '查询时间', date)
            },
            storeChange (storeids) {
                var _self = this
                // _self.init(_self.firstcol)

                //zhuge
                var selectedStores = []
                for (var i = 0; i < storeids.length; i++) {
                    for (var j = 0; j < _self.storeList.length; j++) {
                        if (storeids[i] === _self.storeList[j].id) {
                            selectedStores.push(_self.storeList[j].name)
                        }
                    }
                }
                zhuge.track('选择店铺(数据报表)', {
                    '店铺名':selectedStores
                })
                console.log(selectedStores.join(','))
                ga('send', 'event', '数据报表', '选择店铺', selectedStores.join(','))
            },
            submit () {
                var _self = this

                ga('send', 'event', '数据报表', '确定筛选')
                _self.init(_self.firstcol)
            }
        }
    }
</script>

<style scoped>
    #data-report table tbody .change-color {
        background-color: #f3f6f7;
    }
</style>
