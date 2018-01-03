<template>
    <div id="sales">
        <div>
            <div class="ui segment">
                <div class="ui active inverted dimmer" v-show="loading" style="z-index:1;">
                    <div class="ui text loader">加载中</div>
                </div>
                <h3 class="ui header">报告日期：{{stats_report_date}}</h3>
                <div class="ui four column doubling stackable grid">
                     <div class="eight wide column">
                        <div id="year-on-year-sales-chart" style="min-height: 400px; width: 100%;">
                        </div>
                    </div>
                    <div class="eight wide column">
                        <div id="sales-chart" style="min-height: 400px; width: 100%;">
                        </div>
                    </div>
                    <div class="eight wide column">
                        <div id="receipt-chart" style="min-height: 490px; width: 100%;">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'sales',
    data () {
        return {
            s_id: this.$route.params['s_id'],
            stats_report_date: '',
            loading: true,
            year_on_year_sales: {},
            thirteen_week_sales: {},
            curr_year: String(new Date().getFullYear()),
            last_year: String(new Date().getFullYear() - 1)
        }
    },
    mounted () {
        var _self = this
        $.ajax({
            url: '/api/sales_trend/v0/year-on-year-sales',
            type: 'get',
            dataType: 'json',
            data: {
                store_id: _self.s_id
            },
            beforeSend: function () {
                _self.loading = true
            },
            success: function (data) {              
                _self.year_on_year_sales = data.data
                _self.$nextTick(function () {
                    _self.year_on_year_sales_chart()    
                })
                $.ajax({
                    url: '/api/sales_trend/v0/thirteen-weeks-sales',
                    type: 'get',
                    dataType: 'json',
                    data: {
                        store_id: _self.s_id
                    },
                    success: function (data) {
                        _self.thirteen_week_sales = data.data
                        _self.stats_report_date = data.data.date
                        _self.$nextTick(function () {
                            _self.thirteen_week_sales_chart()
                            _self.stats_data_chart()
                        })
                    },
                    complete: function () {
                        _self.loading = false
                    }
                })
            }
        })
    },
    methods: {
        getMaxOfArray(numArray) {
            return Math.max.apply(null, numArray);
        },
        year_on_year_sales_chart (resize) {
            var _self = this
            var last_year_sales = [], this_year_sales = []
            for (var i = 0; i < _self.year_on_year_sales['last_year_sales'].length; i++) {
                last_year_sales.push(Number(_self.year_on_year_sales['last_year_sales'][i]).toFixed(2))
            }
            for (var j = 0; j < _self.year_on_year_sales['this_year_sales'].length; j++) {
                this_year_sales.push(Number(_self.year_on_year_sales['this_year_sales'][j]).toFixed(2))
            }
            var el = document.getElementById("year-on-year-sales-chart")
            if (resize) {
                var stats_chart = echarts.getInstanceByDom(el)
                if (stats_chart && stats_chart.need_resize) {
                    stats_chart.resize()
                }
                return
            }
            var stats_chart = echarts.init(el, 'cmTheme')
            var baseOption = {
                title : {
                    text: '同比销售额',
                    subtext: '单位：万元'
                },
                tooltip : {
                    trigger: 'axis',
                    show: true
                },
                legend: {
                    orient: "vertical",
                    left: "70%",
                    data:[_self.last_year, _self.curr_year]
                },
                calculable : true,
                xAxis : [
                    {
                        type : 'category',
                        data : ['01','02','03','04','05','06','07','08','09','10','11','12']
                    }
                ],
                yAxis : [
                    {
                        type : 'value'
                    }
                ],
                series : [
                    {
                        name:_self.last_year,
                        type:'bar',
                        data:last_year_sales
                    },
                    {
                        name:_self.curr_year,
                        type:'bar',
                        data:this_year_sales
                    }
                ]
            }
            var option = {
                baseOption: baseOption,
                media: [
                    {
                        query: {
                            maxWidth: 375,
                        },
                        option: {
                            legend:{
                                left: "60%",
                            },
                        },
                    },
                ],
            }
            stats_chart.setOption(option)

            stats_chart.on('legendselectchanged', function (params) {
                ga('send', 'event', '销售趋势', '同比销售额图例', params.name)
            })

            $(window).on("resize", function (){
                if (stats_chart != undefined && stats_chart != null) {
                    var el = stats_chart.getDom()
                    if ($(el).is(":visible")) {
                        stats_chart.need_resize = false
                        stats_chart.resize()
                    } else {
                        stats_chart.need_resize = true
                    }
                }
            })
        },
        thirteen_week_sales_chart (resize) {
            var _self = this
            var el = document.getElementById("sales-chart")
            if (resize) {
                var stats_chart = echarts.getInstanceByDom(el)
                if (stats_chart && stats_chart.need_resize) {
                    stats_chart.resize()
                }
                return
            }

            var last_year_thirteen_weeks_sales = [],
                this_year_thirteen_weeks_sales = []
            for (var i = 0; i < _self.thirteen_week_sales['last_year_thirteen_weeks_sales'].length; i++) {
                last_year_thirteen_weeks_sales.push(Number(_self.thirteen_week_sales['last_year_thirteen_weeks_sales'][i]).toFixed(2))
            }
            for (var j = 0; j < _self.thirteen_week_sales['this_year_thirteen_weeks_sales'].length; j++) {
                this_year_thirteen_weeks_sales.push(Number(_self.thirteen_week_sales['this_year_thirteen_weeks_sales'][j]).toFixed(2))
            }

            var stats_chart = echarts.init(el, 'cmTheme')
            var baseOption = {
                title : {
                    text: '过去13周销售额趋势',
                    subtext: '单位：万元'
                },
                tooltip : {
                    trigger: 'axis',
                    show:true
                },
                legend: {
                    orient: "vertical",
                    left: "70%",
                    data:[_self.last_year, _self.curr_year]
                },

                calculable : true,
                xAxis : [
                    {
                        type : 'category',
                        // axisLabel: {
                        //     interval: 0,
                        //     rotate: 45,
                        //     show: true,
                        // },
                        data: ['13','12','11','10','09','08','07','06','05','04','03','02','01']

                    }
                ],
                yAxis : [
                    {
                        type : 'value'
                    }
                ],
                series : [
                    {
                        name:_self.last_year,
                        type:'bar',
                        data: last_year_thirteen_weeks_sales
                    },
                    {
                        name:_self.curr_year,
                        type:'bar',
                        data: this_year_thirteen_weeks_sales
                    }
                ]
            }
            var option = {
                baseOption: baseOption,
                media: [
                    {
                        query: {
                            maxWidth: 375,
                        },
                        option: {
                            legend:{
                                left: "60%",
                            },
                        },
                    },
                ],
            }
            stats_chart.setOption(option)

            stats_chart.on('legendselectchanged', function (params) {
                ga('send', 'event', '销售趋势', '过去13周销售额趋势图例', params.name)
            })

            $(window).on("resize", function (){
                if (stats_chart != undefined && stats_chart != null) {
                    var el = stats_chart.getDom()
                    if ($(el).is(":visible")) {
                        stats_chart.need_resize = false
                        stats_chart.resize()
                    } else {
                        stats_chart.need_resize = true
                    }
                }
            })
        },
        stats_data_chart (resize) {
            var _self = this
            var el = document.getElementById("receipt-chart")
            if (resize) {
                var stats_chart = echarts.getInstanceByDom(el)
                if (stats_chart && stats_chart.need_resize) {
                    stats_chart.resize()
                }
                return
            }
            
            var traffic_max = _self.getMaxOfArray(_self.thirteen_week_sales["this_year_thirteen_weeks_traffic"])
            var avg_price_max = _self.getMaxOfArray(_self.thirteen_week_sales["this_year_thirteen_weeks_avg_price"])

            var thirteen_weeks_avg_price = []
            for (var j = 0; j < _self.thirteen_week_sales["this_year_thirteen_weeks_avg_price"].length; j++) {
                thirteen_weeks_avg_price.push(Number(_self.thirteen_week_sales["this_year_thirteen_weeks_avg_price"][j]).toFixed(2))
            }

            var stats_chart = echarts.init(el, 'cmTheme')
            var baseOption = {
                title: {
                    text: "单次/客单价13周趋势",
                    left: "left",
                },
                tooltip : {
                    trigger: 'axis',
                    show: true
                },
                legend: {
                    data: ["单次", "客单价"],
                    orient: "vertical",
                    left: "70%",
                    formatter: function(name){
                        switch (name){
                            case "单次":
                                return name + "(次)"
                            case "客单价":
                                return "平均" + name + "(元)"
                            default:
                                return name
                        }
                    },
                },
                grid: {
                    left: "1%",
                    top: '90',
                    containLabel: true
                },
                xAxis: [
                    {
                        type: "category",
                        data: ['13','12','11','10','09','08','07','06','05','04','03','02','01']
                        // axisTick: {
                        //     alignWithLabel: true,
                        //     show: true,
                        // },
                        // axisLabel: {
                        //     interval: 0,
                        //     rotate: 45,
                        //     show: true,
                        // }
                    }
                ],
                yAxis: [
                    {
                        type: "value",
                        min: 0,
                        max: _self.beautify_value(traffic_max),
                        interval: _self.beautify_value(traffic_max) / 2,
                        name : "周单次（次）",
                        nameLocation : "end",
                        nameGap: "5",
                    },
                    {
                        type: "value",
                        min: 0,
                        max: _self.beautify_value(avg_price_max),
                        interval: _self.beautify_value(avg_price_max) / 2,
                        name: "平均客单价（元）",
                        nameLocation: "end",
                        nameGap: "5",
                    }
                ],
                series: [
                    {
                        name: "单次",
                        type: "bar",
                        data: _self.thirteen_week_sales["this_year_thirteen_weeks_traffic"],
                        itemStyle: {
                            normal: {
                                color: "#ffbe00",
                            },
                        }
                    },
                    {
                        name: "客单价",
                        type: "line",
                        yAxisIndex: 1,
                        data: thirteen_weeks_avg_price,
                        itemStyle: {
                            normal: {
                                color: "#FF415b",
                            },
                        }
                    }
                ]
            }
            var option = {
                baseOption: baseOption,
                media: [
                    {
                        query: {
                            maxWidth: 500,
                        },
                        option: {
                            legend: {
                                left: "60%"
                            }
                        },
                    },
                ],
            }

            stats_chart.setOption(option)

            stats_chart.on('legendselectchanged', function (params) {
                ga('send', 'event', '销售趋势', '单次／客单价13周趋势图例', params.name)
            })

            $(window).on("resize", function (){
                if (stats_chart != undefined && stats_chart != null) {
                    var el = stats_chart.getDom()
                    if ($(el).is(":visible")) {
                        stats_chart.need_resize = false
                        stats_chart.resize()
                    } else {
                        stats_chart.need_resize = true
                    }
                }
            })
        },
        beautify_value (value) {
            if (value > 1000) {
                return Math.ceil(value / 1000) * 1000
            } else if (value > 100 && value <= 1000) {
                return Math.ceil(value / 100) * 100
            } else if (value >= 0) {
                return Math.ceil(value / 10) * 10
            } else if (value < 0  && value >= -100) {
                return Math.floor(value / 10) * 10
            } else if (value >= -1000 && value < -100) {
                return Math.floor(value / 100) * 100
            } else if (value < -1000) {
                return Math.floor(value / 1000) * 1000
            }   
        }
    }
}
</script>
