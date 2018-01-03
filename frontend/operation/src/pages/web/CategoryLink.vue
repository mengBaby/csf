<template>
    <div id="category-link">
        <div>
            <div>
                <div>
                    <span>报告时间：</span>
                    <el-date-picker
                      v-model="weekDate"
                      type="week"
                      format="yyyy 第WW周"                              
                      placeholder="选择周"
                      :picker-options="pickerOptions"
                      @change="weekChange"
                      :editable="false"
                      :clearable="false"
                    >
                    </el-date-picker>
                </div>
                <div class="ui segment" style="margin-top: 30px;">
                    <div class="ui active inverted dimmer" v-show="loading">
                        <div class="ui text loader">加载中</div>
                    </div>
                    <div class="ui four column doubling stackable grid" v-if="noDataShow">
                        <div class="ui sixteen wide column center aligned">
                            <i class="big meh icon"></i>
                            <p>暂时还没有生成数据</p>
                        </div>
                    </div>
                    <div class="ui four column doubling stackable grid" v-else>
                        <div id="cat-l1-l2-sales" class="eight wide column"></div>
                        <div id="cat-l1-l2-profit" class="eight wide column"></div>
                        <div id="cat-l2-sales" class="sixteen wide column" v-show="catTwoShow"></div>
                        <div id="cat-l3-sales" class="sixteen wide column" v-show="catThreeShow"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'category-link',
    data () {
        return {
            s_id: this.$route.params['s_id'],
            loading: true,
            noDataShow: false,
            catTwoShow: false,
            catThreeShow: false,
            cat_l1_sales: [],
            cat_l2_sales: [],
            cat_l1_profit: [],
            cat_l2_profit: [],
            cat_lv2_sales: [],
            cat_l3_sales: [],
            //日期选择
            weekDate: new Date(new Date().getTime() - 7 * 24 * 60 * 60 * 1000),
            startDate: '',
            endDate: '',
            pickerOptions: {
                firstDayOfWeek: 1,
                disabledDate(time) {
                    return time.getTime() > new Date().getTime()
                }
            }
        }
    },
    mounted () {
        var _self = this
        //默认前一周
        _self.getStartEndDate(_self.weekDate)
        _self.init(_self.startDate,_self.endDate)
    },
    methods: {
        getStartEndDate (middleDate) {
            var _self = this
            var startDate = new Date()
            var endDate = new Date()
            var weekNum = middleDate.getDay()
            if (weekNum === 0) {
                weekNum = 7
            }
            var startT = middleDate.getTime() - (weekNum - 1) * 24 * 60 * 60 * 1000
            var endT = middleDate.getTime() + (7 - weekNum) * 24 * 60 * 60 * 1000           
            startDate.setTime(startT)
            endDate.setTime(endT)
            var startMonth, endMonth, startDay, endDay
            if ((startDate.getMonth() - 0 + 1) < 10) {
                startMonth = '0' + (startDate.getMonth() - 0 + 1)
            } else {
                startMonth = startDate.getMonth() - 0 + 1
            }
            if ((endDate.getMonth() - 0 + 1) < 10) {
                endMonth = '0' + (endDate.getMonth() - 0 + 1)
            } else {
                endMonth = endDate.getMonth() - 0 + 1
            }
            if (startDate.getDate() < 10) {
                startDay = '0' + startDate.getDate()
            } else {
                startDay = startDate.getDate()
            }
            if (endDate.getDate() < 10) {
                endDay = '0' + endDate.getDate()
            } else {
                endDay = endDate.getDate()
            }
            _self.startDate = startDate.getFullYear() + '-' + startMonth + '-' + startDay
            _self.endDate = endDate.getFullYear() + '-' + endMonth + '-' + endDay
        },
        weekChange (week) {
            var _self = this
            _self.getStartEndDate(_self.weekDate)
            _self.init(_self.startDate, _self.endDate)

            zhuge.track('报告时间(品类销售环比分析)', {
                '时间': week
            })

            ga('send', 'event', '品类销售环比分析', '选择报告时间', week)
        },
        init (startDate, endDate) {
            var _self = this
            // 一二级分类旭日图
            $.ajax({
                url: '/api/ring_analysis/v0/sun-figure',
                type: 'get',
                dataType: 'json',
                data: {
                    start_time: startDate,
                    end_time: endDate,
                    store_id: _self.s_id
                },
                success: function (data) {
                    if (data.data.cat_l1_sales.length!==0) {
                        _self.cat_l1_sales = data.data.cat_l1_sales
                        _self.cat_l2_sales = data.data.cat_l2_sales
                        _self.cat_l1_profit = data.data.cat_l1_profit
                        _self.cat_l2_profit = data.data.cat_l2_profit
                        _self.noDataShow = false
                        _self.$nextTick(function () {
                            _self.cat_l1_l2_chart()
                        })
                        
                    } else {
                        _self.noDataShow = true
                    }
                },
                complete: function () {
                    _self.loading = false
                }
            })
            // 二级分类和三级分类销售差值
            $.ajax({
                url: '/api/ring_analysis/v0/sales-diff',
                type: 'get',
                dataType: 'json',
                data: {
                    start_time: startDate,
                    end_time: endDate,
                    store_id: _self.s_id
                },
                success: function (data) {
                    if (data.data.cat_l2_data.length !== 0) {
                        _self.catTwoShow = true
                        _self.cat_lv2_sales = data.data.cat_l2_data
                        _self.$nextTick(function () {
                            _self.cat_l2_chart()
                        })
                    } else {
                        _self.catTwoShow = false
                    }
                    if (data.data.cat_l3_data.length !== 0) {
                        _self.catThreeShow = true
                        _self.cat_l3_sales = data.data.cat_l3_data
                        _self.$nextTick(function () {
                            _self.cat_l3_chart()
                        })
                    } else {
                        _self.catThreeShow = false
                    }
                },
                complete: function () {
                    _self.loading = false
                }
            })
        },
        cat_l1_l2_chart (resize) {
            var _self = this
            var salesEle = document.getElementById("cat-l1-l2-sales")
            var profitEle = document.getElementById("cat-l1-l2-profit")
            if (resize) {
                var salesChart = echarts.getInstanceByDom(salesEle)
                var profitChart = echarts.getInstanceByDom(profitEle)
                if (salesChart && salesChart.need_resize) {
                    salesChart.resize()
                }
                if (profitChart && profitChart.need_resize) {
                    profitChart.resize()
                }
                return
            }
            var salesChart = echarts.init(salesEle, 'cmTheme')
            var profitChart = echarts.init(profitEle, 'cmTheme')
            var cat_l1_names = []
            var cat_l1_data = []
            var cat_l2_data = []
            var cat_l1_pnames = []
            var cat_l1_pdata = []
            var cat_l2_pdata = []
            var cat_lv1_colordata = {}
            var cat_lv2_colordata = {}
            var count_lv1 = 0
            var count_lv2 = 0
            var colorData = [
                {
                    cat_l1_color: '#b71c1c',
                    cat_l2_color: ['#c62828','#d32f2f','#e53935','#ef5350','#e57373','#ef9a9a']
                },
                {
                    cat_l1_color: '#01579B',
                    cat_l2_color: ['#0277BD','#0288D1','#039BE5','#29B6F6','#4FC3F7','#81D4FA']
                },
                {
                    cat_l1_color: '#006064',
                    cat_l2_color: ['#00838F','#0097A7','#00ACC1','#26C6DA','#4DD0E1','#80DEEA']
                },
                {
                    cat_l1_color: '#E65100',
                    cat_l2_color: ['#EF6C00','#F57C00','#FB8C00','#FFA726','#FFB74D','#FFCC80']
                },
                {
                    cat_l1_color: '#880E4F',
                    cat_l2_color: ['#AD1457','#C2185B','#D81B60','#EC407A','#F06292','#F48FB1']
                },
                {
                    cat_l1_color: '#4A148C',
                    cat_l2_color: ['#6A1B9A','#7B1FA2','#8E24AA','#AB47BC','#BA68C8','#CE93D8']
                },
                {
                    cat_l1_color: '#311B92',
                    cat_l2_color: ['#4527A0','#512DA8','#5E35B1','#7E57C2','#9575CD','#B39DDB']
                },
                {
                    cat_l1_color: '#1A237E',
                    cat_l2_color: ['#283593','#303F9F','#3949AB','#5C6BC0','#7986CB','#9FA8DA']
                },
                {
                    cat_l1_color: '#0D47A1',
                    cat_l2_color: ['#1565C0','#1976D2','#1E88E5','#42A5F5','#64B5F6','#90CAF9']
                },
                {
                    cat_l1_color: '#004D40',
                    cat_l2_color: ['#00695C','#00796B','#00897B','#26A69A','#4DB6AC','#80CBC4']
                },
                {
                    cat_l1_color: '#1B5E20',
                    cat_l2_color: ['#2E7D32','#388E3C','#43A047','#66BB6A','#81C784','#A5D6A7']
                },
                {
                    cat_l1_color: '#33691E',
                    cat_l2_color: ['#558B2F','#689F38','#7CB342','#9CCC65','#AED581','#C5E1A5']
                }
            ]
            var cat_colordata = {}
            for (var i=0; i < _self.cat_l1_sales.length; i++) {
                cat_l1_names.push(_self.cat_l1_sales[i].cat_l1_name)
                cat_l1_data.push({
                    name: _self.cat_l1_sales[i].cat_l1_name,
                    value: _self.cat_l1_sales[i].cat_l1_sales
                })
                cat_colordata[_self.cat_l1_sales[i].cat_l1_id] = colorData[count_lv1]
                cat_lv1_colordata[_self.cat_l1_sales[i].cat_l1_name] = colorData[count_lv1].cat_l1_color
                count_lv1++
                if (count_lv1 >= colorData.length) {
                    count_lv1 = 0
                }
            }
            for (var i=0; i < _self.cat_l2_sales.length; i++) {
                cat_l2_data.push({
                    name: _self.cat_l2_sales[i].cat_l2_name,
                    value: _self.cat_l2_sales[i].value
                })
            }
            for (var j=0; j < _self.cat_l1_sales.length; j++) {
                for (var k=0; k < _self.cat_l2_sales.length; k++) {
                    if (_self.cat_l2_sales[k].cat_l1_id === _self.cat_l1_sales[j].cat_l1_id) {
                        cat_lv2_colordata[_self.cat_l2_sales[k].cat_l2_name] = cat_colordata[_self.cat_l2_sales[k].cat_l1_id].cat_l2_color[count_lv2]
                        count_lv2++
                        if (count_lv2 >= cat_colordata[_self.cat_l2_sales[k].cat_l1_id].cat_l2_color.length) {
                            count_lv2 = 0
                        }
                    } else {
                        count_lv2 = 0
                    }
                }
            }
            for (var i=0; i < _self.cat_l1_profit.length; i++) {
                cat_l1_pnames.push(_self.cat_l1_profit[i].cat_l1_name)
                cat_l1_pdata.push({
                    name: _self.cat_l1_profit[i].cat_l1_name,
                    value: _self.cat_l1_profit[i].cat_l1_profit
                })
            }
            for (var i=0; i < _self.cat_l2_profit.length; i++) {
                cat_l2_pdata.push({
                    name: _self.cat_l2_profit[i].cat_l2_name,
                    value: _self.cat_l2_profit[i].value
                })
            }
            var salesOption = {
                title: {
                    text: "销售额旭日图",
                    left: "center"
                },
                legend: {
                    type: 'scroll',
                    orient: "vertical",
                    x: "right",
                    data: cat_l1_names,
                    selectedMode: 'multiple'
                },
                series: [
                    {
                        name:"一级分类",
                        type:"pie",
                        selectedMode: "single",
                        radius: ["35%", "55%"],
                        avoidLabelOverlap: false,
                        legendHoverLink: false,
                        label: {
                            normal: {
                                show: false,
                                position: 'center'
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: '14',
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: false
                            }
                        },
                        itemStyle: {
                            normal: {
                                color: function (params) {
                                    return cat_lv1_colordata[params.name]
                                }
                            }
                        },
                        data: cat_l1_data
                    },
                    {
                        name:"二级分类",
                        type:"pie",
                        radius: ["56%", "75%"],
                        cursor: "pointer",
                        selectedMode: "single",
                        avoidLabelOverlap: false,
                        legendHoverLink: false,
                        label: {
                            normal: {
                                position: "center",
                                show: false
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: 12,
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: false
                            }
                        },
                        itemStyle: {
                            normal: {
                                color: function (params) {
                                    return cat_lv2_colordata[params.name]
                                }
                            }
                        },
                        data: cat_l2_data
                    }
                ]
            }
            var profitOption = {
                title: {
                    text: "毛利额旭日图",
                    left: "center",
                },
                legend: {
                    type: 'scroll',
                    orient: "vertical",
                    x: "right",
                    data: cat_l1_pnames,
                    selectedMode: 'multiple'
                },
                series: [
                    {
                        name:"一级分类",
                        type:"pie",
                        selectedMode: "single",
                        radius: ["35%", "55%"],
                        avoidLabelOverlap: false,
                        label: {
                            normal: {
                                show: false,
                                position: 'center'
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: '14',
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: false
                            }
                        },
                        itemStyle: {
                            normal: {
                                color: function (params) {
                                    return cat_lv1_colordata[params.name]
                                }
                            }
                        },
                        data: cat_l1_pdata
                    },
                    {
                        name:"二级分类",
                        type:"pie",
                        selectedMode: "single",
                        radius: ["56%", "75%"],
                        avoidLabelOverlap: false,
                        cursor: "pointer",
                        label: {
                            normal: {
                                position: "center",
                                show: false
                            },
                            emphasis: {
                                show: true,
                                textStyle: {
                                    fontSize: 12,
                                    fontWeight: 'bold'
                                }
                            }
                        },
                        labelLine: {
                            normal: {
                                show: false
                            }
                        },
                        itemStyle: {
                            normal: {
                                color: function (params) {
                                    return cat_lv2_colordata[params.name]
                                }
                            }
                        },
                        data: cat_l2_pdata
                    }
                ]
            }
            salesChart.setOption(salesOption)
            profitChart.setOption(profitOption)
            // salesChart.group = 'group1'
            // profitChart.group = 'group1'
            // echarts.connect('group1')
            salesChart.on('mouseover', function (params) {
                salesChart.dispatchAction({
                    type: 'highlight',
                    seriesName: params.seriesName,
                    name: params.name
                })
                profitChart.dispatchAction({
                    type: 'highlight',
                    seriesName: params.seriesName,
                    name: params.name
                })
            })
            salesChart.on('mouseout', function (params) {
                salesChart.dispatchAction({
                    type: 'downplay',
                    seriesName: params.seriesName,
                    name: params.name
                })
                profitChart.dispatchAction({
                    type: 'downplay',
                    seriesName: params.seriesName,
                    name: params.name
                })
            })
            profitChart.on('mouseover', function (params) {
                salesChart.dispatchAction({
                    type: 'highlight',
                    seriesName: params.seriesName,
                    name: params.name
                })
                profitChart.dispatchAction({
                    type: 'highlight',
                    seriesName: params.seriesName,
                    name: params.name
                })
            })
            profitChart.on('mouseout', function (params) {
                salesChart.dispatchAction({
                    type: 'downplay',
                    seriesName: params.seriesName,
                    name: params.name
                })
                profitChart.dispatchAction({
                    type: 'downplay',
                    seriesName: params.seriesName,
                    name: params.name
                })
            })
            salesChart.on('legendselectchanged', function (params) {
                if (params.selected[params.name]) {
                    for (var i = 0; i < _self.cat_l1_sales.length; i++) {
                        if (_self.cat_l1_sales[i].cat_l1_name === params.name) {
                            for (var j = 0; j < _self.cat_l2_sales.length; j++) {
                                if (_self.cat_l2_sales[j].cat_l1_id === _self.cat_l1_sales[i].cat_l1_id) {
                                    salesChart.dispatchAction({
                                        type: 'legendSelect',
                                        name: _self.cat_l2_sales[j].cat_l2_name
                                    })
                                    profitChart.dispatchAction({
                                        type: 'legendSelect',
                                        name: _self.cat_l2_sales[j].cat_l2_name
                                    })
                                }
                            }
                        }
                    }
                    salesChart.dispatchAction({
                        type: 'legendSelect',
                        name: params.name
                    })
                    profitChart.dispatchAction({
                        type: 'legendSelect',
                        name: params.name
                    })
                } else {
                    for (var i = 0; i < _self.cat_l1_sales.length; i++) {
                        if (_self.cat_l1_sales[i].cat_l1_name === params.name) {
                            for (var j = 0; j < _self.cat_l2_sales.length; j++) {
                                if (_self.cat_l2_sales[j].cat_l1_id === _self.cat_l1_sales[i].cat_l1_id) {
                                    salesChart.dispatchAction({
                                        type: 'legendUnSelect',
                                        name: _self.cat_l2_sales[j].cat_l2_name
                                    })
                                    profitChart.dispatchAction({
                                        type: 'legendUnSelect',
                                        name: _self.cat_l2_sales[j].cat_l2_name
                                    })
                                }
                            }
                        }
                    }
                    salesChart.dispatchAction({
                        type: 'legendUnSelect',
                        name: params.name
                    })
                    profitChart.dispatchAction({
                        type: 'legendUnSelect',
                        name: params.name
                    })
                }

                zhuge.track('销售额旭日图(品类销售环比分析)', {
                    '类别': params.name
                })
                ga('send', 'event', '品类销售环比分析', '点击销售额图例', params.name)
            })
            profitChart.on('legendselectchanged', function (params) {
                if (params.selected[params.name]) {
                    for (var i = 0; i < _self.cat_l1_sales.length; i++) {
                        if (_self.cat_l1_sales[i].cat_l1_name === params.name) {
                            for (var j = 0; j < _self.cat_l2_sales.length; j++) {
                                if (_self.cat_l2_sales[j].cat_l1_id === _self.cat_l1_sales[i].cat_l1_id) {
                                    salesChart.dispatchAction({
                                        type: 'legendSelect',
                                        name: _self.cat_l2_sales[j].cat_l2_name
                                    });
                                    profitChart.dispatchAction({
                                        type: 'legendSelect',
                                        name: _self.cat_l2_sales[j].cat_l2_name
                                    });
                                }
                            }
                        }
                    }
                    salesChart.dispatchAction({
                        type: 'legendSelect',
                        name: params.name
                    });
                    profitChart.dispatchAction({
                        type: 'legendSelect',
                        name: params.name
                    });

                } else {
                    for (var i = 0; i < _self.cat_l1_sales.length; i++) {
                        if (_self.cat_l1_sales[i].cat_l1_name === params.name) {
                            for (var j = 0; j < _self.cat_l2_sales.length; j++) {
                                if (_self.cat_l2_sales[j].cat_l1_id === _self.cat_l1_sales[i].cat_l1_id) {
                                    salesChart.dispatchAction({
                                        type: 'legendUnSelect',
                                        name: _self.cat_l2_sales[j].cat_l2_name
                                    });
                                    profitChart.dispatchAction({
                                        type: 'legendUnSelect',
                                        name: _self.cat_l2_sales[j].cat_l2_name
                                    });
                                }
                            }
                        }
                    }
                    salesChart.dispatchAction({
                        type: 'legendUnSelect',
                        name: params.name
                    });
                    profitChart.dispatchAction({
                        type: 'legendUnSelect',
                        name: params.name
                    });
                }

                zhuge.track('毛利额旭日图(品类销售环比分析)', {
                    '类别': params.name
                })
                ga('send', 'event', '品类销售环比分析', '点击毛利额图例', params.name)
            })
            salesChart.on('pieselectchanged', function (params) {
                salesChart.dispatchAction({
                    type: 'pieSelect',
                    seriesName: params.seriesName,
                    name: params.name
                })
                profitChart.dispatchAction({
                    type: 'pieSelect',
                    seriesName: params.seriesName,
                    name: params.name
                })
                salesChart.dispatchAction({
                    type: 'pieUnSelect',
                    seriesName: params.seriesName,
                    name: params.name
                })
                profitChart.dispatchAction({
                    type: 'pieUnSelect',
                    seriesName: params.seriesName,
                    name: params.name
                })

                ga('send', 'event', '品类销售环比分析', '点击销售额旭日图', params.name)

            })
            profitChart.on('pieselectchanged', function (params) {
                salesChart.dispatchAction({
                    type: 'pieSelect',
                    seriesName: params.seriesName,
                    name: params.name
                })
                profitChart.dispatchAction({
                    type: 'pieSelect',
                    seriesName: params.seriesName,
                    name: params.name
                })
                salesChart.dispatchAction({
                    type: 'pieUnSelect',
                    seriesName: params.seriesName,
                    name: params.name
                })
                profitChart.dispatchAction({
                    type: 'pieUnSelect',
                    seriesName: params.seriesName,
                    name: params.name
                })

                ga('send', 'event', '品类销售环比分析', '点击毛利额旭日图', params.name)
            })
            $(window).on("resize", function (){
                if (salesChart != undefined && salesChart != null) {
                    var el = salesChart.getDom()
                    if ($(el).is(":visible")) {
                        salesChart.need_resize = false
                        salesChart.resize()
                    } else {
                        salesChart.need_resize = true
                    }
                }
                if (profitChart != undefined && profitChart != null) {
                    var el = profitChart.getDom()
                    if ($(el).is(":visible")) {
                        profitChart.need_resize = false
                        profitChart.resize()
                    } else {
                        profitChart.need_resize = true
                    }
                }
            })
        },
        cat_l2_chart (resize) {
            var _self = this
            var el = document.getElementById("cat-l2-sales")
            if (resize) {
                var chart = echarts.getInstanceByDom(el)
                if (chart && chart.need_resize) {
                    chart.resize()
                }
                return
            }
            var chart = echarts.init(el, 'cmTheme')
            var cat_names = []
            var cat_sales = []
            var cat_sales_r = []
            var cat_profit_rates = []
            var cat_profit_rates_r = []
            var max_sale = 0.0
            var max_pro_rate = 0.0
            var min_sale = 0.0
            var min_pro_rate = 0.0
            var count = Math.min(_self.cat_lv2_sales.length, 30)
            var revenue,revenue_r,gross_profit,gross_profit_r
            for(var i = 0; i < count; i++) {
                revenue = Number(_self.cat_lv2_sales[i].sales).toFixed(0)
                revenue_r = Number(_self.cat_lv2_sales[i].last_week_sales).toFixed(0)
                max_sale = Math.max(max_sale, revenue, revenue_r)
                min_sale = Math.min(min_sale, revenue, revenue_r)
                cat_sales.push(revenue)
                cat_sales_r.push(revenue_r)

                gross_profit = Number(_self.cat_lv2_sales[i].rate).toFixed(1)
                gross_profit_r = Number(_self.cat_lv2_sales[i].last_week_rate).toFixed(1)
                max_pro_rate = Math.max(max_pro_rate, gross_profit, gross_profit_r)
                min_pro_rate = Math.min(min_pro_rate, gross_profit, gross_profit_r)
                cat_profit_rates.push(gross_profit)
                cat_profit_rates_r.push(gross_profit_r)

                cat_names.push(_self.cat_lv2_sales[i].name)
            }
            max_sale = _self.beautify_value(max_sale)
            max_pro_rate = _self.beautify_value(max_pro_rate)
            min_sale = _self.beautify_value(min_sale)
            min_pro_rate = _self.beautify_value(min_pro_rate)
            var option = {
                title: {
                    text: "二级分类销售差值柱状图",
                    left: "center",
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross'
                    }
                },
                legend: {
                    data: ["T-1周销售额", "T周销售额", "T-1周毛利率", "T周毛利率"],
                    top: "6%",
                    selectedMode: "multiple"
                },
                grid: {
                    top: "14%"
                },
                yAxis: {
                    type: "category",
                    data: cat_names,
                    inverse: true,
                    axisLabel: {
                        interval: 0,
                    }
                    // axisLine: {
                    //     show: false
                    // },
                    // axisTick: {
                    //     show: false
                    // }
                },
                xAxis: [
                    {
                        type: "value",
                        max: max_pro_rate,
                        min: min_pro_rate,
                        // interval: max_pro_rate / 2,
                        name: "毛利率 (%)",
                        nameLocation: "end",
                        splitLine: {
                            show: false
                        }
                    },
                    {
                        type: "value",
                        max: max_sale,
                        min: min_sale,
                        // interval: max_sale / 2,
                        name: "销售额 (元)",
                        nameLocation: "end",
                        splitLine: {
                            show: false
                        }
                    }
                ],
                series: [
                    {
                        name: "T-1周销售额",
                        type: "bar",
                        data: cat_sales_r,
                        xAxisIndex: 1,
                    },
                    {
                        name: "T周销售额",
                        type: "bar",
                        data: cat_sales,
                        xAxisIndex: 1,
                        barCategoryGap: "30%",
                    },
                    {
                        name: "T-1周毛利率",
                        type: "line",
                        data: cat_profit_rates_r,
                        xAxisIndex: 0,
                    },
                    {
                        name: "T周毛利率",
                        type: "line",
                        data: cat_profit_rates,
                        xAxisIndex: 0,
                    },
                ]
            }
            chart.setOption(option)
            chart.on('legendselectchanged', function (params) {
                if (params.selected[params.name]) {
                    zhuge.track(params.name + ':二级(品类销售环比分析)', {
                        '状态': '启用'
                    })
                } else {
                    zhuge.track(params.name + ':二级(品类销售环比分析)', {
                        '状态': '停用'
                    })
                }

                ga('send', 'event', '品类销售环比分析', '点击二级分类销售差值柱状图' + params.name + '图例')
            })

            $(window).on("resize", function (){
                if (chart != undefined && chart != null) {
                    var el = chart.getDom()
                    if ($(el).is(":visible")) {
                        chart.need_resize = false
                        chart.resize()
                    } else {
                        chart.need_resize = true
                    }
                }
            })
        },
        cat_l3_chart (resize) {
            var _self = this
            var el = document.getElementById("cat-l3-sales")
            if (resize) {
                var chart = echarts.getInstanceByDom(el)
                if (chart && chart.need_resize) {
                    chart.resize()
                }
                return
            }
            var chart = echarts.init(el, 'cmTheme')
            var cat_names = []
            var cat_sales = []
            var cat_sales_r = []
            var cat_profit_rates = []
            var cat_profit_rates_r = []
            var max_sale = 0.0
            var max_pro_rate = 0.0
            var min_sale = 0.0
            var min_pro_rate = 0.0
            var count = Math.min(_self.cat_l3_sales.length, 30)
            var sale, sale_r, pro, pro_r
            for(var i = 0; i < count; i++) {
                sale = Number(_self.cat_l3_sales[i].sales).toFixed(0)
                sale_r = Number(_self.cat_l3_sales[i].last_week_sales).toFixed(0)
                max_sale = Math.max(max_sale, sale, sale_r)
                min_sale = Math.min(min_sale, sale, sale_r)
                cat_sales.push(sale)
                cat_sales_r.push(sale_r)

                pro = Number(_self.cat_l3_sales[i].rate).toFixed(1)
                pro_r = Number(_self.cat_l3_sales[i].last_week_rate).toFixed(1)
                max_pro_rate = Math.max(max_pro_rate, pro, pro_r)
                min_pro_rate = Math.min(min_pro_rate, pro, pro_r)
                cat_profit_rates.push(pro)
                cat_profit_rates_r.push(pro_r)

                cat_names.push(_self.cat_l3_sales[i].name)
            }
            max_sale = _self.beautify_value(max_sale)
            max_pro_rate = _self.beautify_value(max_pro_rate)
            min_sale = _self.beautify_value(min_sale)
            min_pro_rate = _self.beautify_value(min_pro_rate)

            var option = {
                title: {
                    text: "三级分类销售额/毛利率(top30)",
                    left: "center",
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'cross'
                    }
                },
                legend: {
                    data: ["T-1周销售额", "T周销售额", "T-1周毛利率", "T周毛利率"],
                    top: "6%",
                    selectedMode: "multiple"
                },
                grid: {
                    top: "14%"
                },
                yAxis: [
                    {
                        type: "category",
                        data: cat_names,
                        inverse: true,
                        axisLabel: {
                            interval: 0,
                        }
                    }
                ],
                xAxis: [
                    {
                        type: "value",
                        max: max_pro_rate,
                        min: min_pro_rate,
                        // interval: max_pro_rate / 2,
                        name: "毛利率 (%)",
                        nameLocation: "end",
                        splitLine: {
                            show: false
                        }
                    },
                    {
                        type: "value",
                        max: max_sale,
                        min: min_sale,
                        // interval: max_sale / 2,
                        name: "销售额 (元)",
                        nameLocation: "end",
                        splitLine: {
                            show: false
                        }
                    },
                ],
                series: [
                    {
                        name: "T-1周销售额",
                        type: "bar",
                        data: cat_sales_r,
                        xAxisIndex: 1,
                    },
                    {
                        name: "T周销售额",
                        type: "bar",
                        data: cat_sales,
                        xAxisIndex: 1,
                        barCategoryGap: "30%",
                    },
                    {
                        name: "T-1周毛利率",
                        type: "line",
                        data: cat_profit_rates_r,
                        xAxisIndex: 0,
                    },
                    {
                        name: "T周毛利率",
                        type: "line",
                        data: cat_profit_rates,
                        xAxisIndex: 0,
                    },
                ]
            }
            chart.setOption(option)

            chart.on('legendselectchanged', function (params) {
                if (params.selected[params.name]) {
                    zhuge.track(params.name + ':三级(品类销售环比分析)', {
                        '状态': '启用'
                    })
                } else {
                    zhuge.track(params.name + ':三级(品类销售环比分析)', {
                        '状态': '停用'
                    })
                }

                ga('send', 'event', '品类销售环比分析', '点击三级分类销售差值柱状图' + params.name + '图例')
            })

            $(window).on("resize", function () {
                if (chart != undefined && chart != null) {
                    var el = chart.getDom()
                    if ($(el).is(":visible")) {
                        chart.need_resize = false
                        chart.resize()
                    } else {
                        chart.need_resize = true
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

<style scoped>
    #cat-l1-l2-sales, #cat-l1-l2-profit {
        width: 100%;
        height: 300px;
    }
    #cat-l2-sales, #cat-l3-sales {
        min-height: 400px;
        width:100%;
        margin-bottom: 15px;
        height: 700px;
    }
</style>
