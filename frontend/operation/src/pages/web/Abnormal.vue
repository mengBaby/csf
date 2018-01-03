<template>
    <div id="abnormal">
        <div  class="ui segment">
            <h3 class="ui header">异常库存分析周报</h3>
            <div id="category-exception">
                <div class="report-date">
                    <span>
                       报告日期：
                    </span>
                    <div>
                        <div class="ui selection dropdown year year-stock-v0.7pc">
                            <input type="hidden" name="year" v-bind:value="selected_year">
                            <i class="dropdown icon"></i>
                            <div class="default text">请选择</div>
                            <div class="menu">
                                <div class="item" v-for="year in years" v-bind:data-value="year">{{year}}</div>
                            </div>
                        </div>
                        <span style="margin-left:1rem">年</span>
                    </div>
                    <div>
                        <div class="ui selection dropdown mon month-stock-v0.7pc">
                            <input type="hidden" name="month" v-bind:value="selected_mon">
                            <i class="dropdown icon"></i>
                            <div class="default text">请选择</div>
                            <div class="menu">
                                <div class="item" v-for='mon in mons' v-bind:data-value="mon">{{mon}}</div>
                            </div>
                        </div>
                        <span style="margin-left:1rem">月</span>
                    </div>
                    <div>
                        <div class="ui selection dropdown week day-stock-v0.7pc">
                            <input type="hidden" name="week" v-bind:value="selected_week">
                            <i class="dropdown icon"></i>
                            <div class="default text">请选择</div>
                            <div class="menu">
                                <div class="item" v-for='week in weeks' v-bind:data-value="week">{{week}}</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="ui active centered inline large text loader" v-show="loading">加载中</div>
                <div class="ui fluid card" v-show="!loading && periods===null">
                    <div class="center aligned content">
                        <i class="big meh icon"></i>
                        <p>暂时还没有生成数据</p>
                    </div>
                </div>
                <div class="ui styled fluid accordion" v-for="(catItem, catIndex) in reportData" v-show="!loading&&catItem.cat_stats.length>0">
                    <div class="ui header title" :class="{ active: catIndex === 0 }">
                        <i class="dropdown icon"></i>
                        <span class="header">品类: {{catItem.item_name}}</span>
                    </div>
                    <div class="content" :class="{ active: catIndex === 0 }">
                        <table class="ui striped orange sortable celled table">
                            <thead>
                                <tr class="center aligned">
                                    <th>序号</th>
                                    <th>商品内码</th>
                                    <th>商品名称</th>
                                    <th>期末库存</th>
                                    <th>连续不动销天数</th>
                                    <th>巡查反馈</th>
                                    <th>巡查日期</th>
                                    <th>巡查人</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(item, index) in catItem.cat_stats" class="center aligned">
                                    <td>{{ index - 0 + 1 }}</td>
                                    <td>{{ item.item_id }}</td>
                                    <td>{{ item.item_name }}</td>
                                    <td>{{ item.stock }}</td>
                                    <td>{{ item.non_sales_date }}</td>
                                    <td>{{ item.feedback_text }}</td>
                                    <td>{{ item.feedback_time }}</td>
                                    <td>{{ item.person_name }}</td>   
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'abnormal',
    props: ['csId', 'sId'],
    data () {
        return {
            cs_id: this.csId,
            s_id: this.sId,
            periods: {},
            years: [],
            mons: [],
            weeks: [],
            selected_year: null,
            selected_mon: null,
            selected_week: null,
            loading: true,
            reportData: []
        }
    },
    mounted () {
        var _self = this
        _self.initDropdown()
        _self.getDateOptions()
    },
    methods: {
        initDropdown () {
            var _self = this
            $(".ui.dropdown.year").dropdown({
                action: "activate",
                onChange: function(value){
                    _self.selected_year = value;
                    _self.mons = Object.keys(_self.periods[value]).sort(function(a, b){return b-a})
                    _self.selected_mon = null
                    _self.weeks = []
                    $(".ui.dropdown.mon").dropdown("set text", "请选择")
                    $(".ui.dropdown.week").dropdown("set text", "请选择")
                }
            })
            $(".ui.dropdown.mon").dropdown({
                action: "activate",
                onChange: function(value){
                    _self.selected_mon = value
                    _self.weeks = _self.periods[_self.selected_year][_self.selected_mon]
                    _self.selected_week = null
                    $(".ui.dropdown.week").dropdown("set text", "请选择")
                }
            })
            $(".ui.dropdown.week").dropdown({
                action: "activate",
                onChange: function(value){
                    _self.selected_week = value
                    _self.getTableData(value)
                    _self.loading = true
                }
            })
        },
        getDateOptions () {
            var _self = this
            $.ajax({
                url: '/api/v1/operation/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/abnormal/periods',
                type: 'get',
                dataType: 'json',
                success: function (res) {
                    if (res.code === 0){
                        _self.periods = res.periods
                        if (_self.periods !== null) {
                            _self.years = Object.keys(res.periods).sort(function(a, b){return b-a;})
                            _self.selected_year = _self.years[0]

                            _self.mons = Object.keys(res.periods[_self.selected_year]).sort(function(a, b){return b-a;})
                            _self.selected_mon = _self.mons[0]

                            _self.weeks = res.periods[_self.selected_year][_self.selected_mon]
                            _self.selected_week = _self.weeks[0]

                            $(".ui.dropdown.year").dropdown("set text", _self.selected_year)
                            $(".ui.dropdown.mon").dropdown("set text", _self.selected_mon)
                            $(".ui.dropdown.week").dropdown("set text", _self.selected_week)

                           _self.getTableData(_self.selected_week)
                        } else {
                            _self.loading = false
                            _self.periods = res.periods
                        }
                    }
                }
            })
        },
        getTableData (week) {
            var _self = this
            $.ajax({
                url: '/api/v1/operation/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/abnormal',
                type: 'get',
                dataType: 'json',
                data: {
                    week: week
                },
                success: function(data) {
                    _self.reportData = data.stats
                    _self.$nextTick(function() {
                        $('.ui.accordion').accordion('refresh')
                    })
                    _self.loading = false
                }
            })
        }
    }
}
</script>

<style scoped>
    .ui.dropdown.year, .ui.dropdown.mon {
        min-width: 4rem !important;
    }
    .ui.ui.dropdown.week {
        min-width: 15rem !important;
    }
    .report-date>div {
        display: inline-block;
    }
    .pro-category>div {
        display: inline-block;
        margin-top: 10px;
        margin-right: 10px;
    }
    .table-con {
        margin-top: 10px;
    }
    .table-con>table tr {
        text-align: center;
    }

    .ui.bottom.negative.message {
        margin: 0;
    }

    .ui.fluid.accordion {
        margin-top: 10px;
    }
</style>
