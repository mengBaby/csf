<template>
    <div class="price">
        <h3 class="ui header">价格带分析周报</h3>

        <el-card class="box-card">
            <el-form :inline="true">
                <el-form-item label="报告周期">
                    <el-date-picker
                        class="date-picker"
                        v-model="selectedDate"
                        type="week"
                        :clearable="false"
                        :format="dateFromat"
                        :picker-options="pickerOption"
                        @change="weekChangeGa"
                        placeholder="请选择">
                      </el-date-picker>
                </el-form-item>

                <el-form-item label="报告品类">
                    <el-cascader
                        id="catCascader"
                        class="cat-selection"
                        :options="catList"
                        :props="defaultProps"
                        @change="catChangeGa"
                        v-model="selectedCatList">
                    </el-cascader>
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" :disabled="submitDisabled" @click="submit(),gaTracker()">
                        {{ submitDisabled ? 'loading' : '确定' }}
                    </el-button>
                </el-form-item>
            </el-form>
        </el-card>

        <div class="ui active centered inline large text loader" v-show="loading">加载中</div>
        <el-card class="box-card" v-show="!loading">
            <div class="chart-box" v-show="!isNull">
                <el-form :inline="true">
                    <el-form-item label="价格统计粒度">
                        <el-select v-model="selectedPriceInterval" placeholder="请选择">
                            <el-option
                              v-for="item in priceIntervalList"
                              :key="item.value"
                              :label="item.text"
                              :value="item.value">
                            </el-option>
                          </el-select>
                    </el-form-item>
                </el-form>

                <div class="chart" id="mainChart"></div>
                <div class="chart" id="profitChart"></div>
                <div class="chart" id="salesChart"></div>
            </div>

            <div class="ui fluid card" v-show="isNull">
                <div class="center aligned content">
                    <i class="big meh icon"></i>
                    <p>暂时还没有生成数据</p>
                </div>
            </div>
        </el-card>
    </div>
</template>

<script>
export default {
    name: 'price',
    data () {
        return {
            s_id: this.$route.params.s_id,

            // 默认上周二
            selectedDate: new Date(new Date().getTime() - 3600 * 1000 * 24 * (new Date().getDay() - 2 + 7)),
            start: new Date(),
            end: new Date(),

            pickerOption: {
                firstDayOfWeek: 1,
                disabledDate(time) {
                    return time.getTime() > new Date().getTime()
                }
            },

            defaultProps: {
                value: 'id'
            },

            catList: [],
            selectedCatList: [],
            selectedCatLabels: [],

            submitDisabled: true,

            mainChart: {},
            profitChart: {},
            salesChart: {},

            loading: false,
            isNull: false,

            priceIntervalList: [
                {
                    value: 0.5,
                    text: '0.5元'
                },
                {
                    value: 1,
                    text: '1元'
                },
                {
                    value: 2,
                    text: '2元'
                },
                {
                    value: 3,
                    text: '3元'
                },
                {
                    value: 4,
                    text: '4元'
                },
                {
                    value: 5,
                    text: '5元'
                }
            ],
            selectedPriceInterval: 1,
        }
    },

    mounted(){
        this.getCatList()
    },

    watch: {
        selectedPriceInterval: function(newValue) {

            ga('send', 'event', '价格带分析', '选择价格统计粒度', newValue + '元')

            if(newValue !== null) {
                this.mergeMainChartAxis()
            }
        },

        submitDisabled: function(newValue) {
            if(newValue === false) {
                this.submit()
            }
        },

        selectedCatList: function(newValue) {
            var catList = this.catList
            this.selectedCatLabels = this.getSelectedCatLabels(newValue, catList);
        }
    },

    computed: {
        dateFromat: function() {
            if(this.selectedDate) {
                this.start = new Date(this.selectedDate)
                this.end = new Date(this.selectedDate)

                this.start.setDate(this.start.getDate() - 1)
                this.end.setDate(this.end.getDate() + 5)
            }

            return this.formatDate(this.start) + '到' + this.formatDate(this.end)
        }
    },

    methods: {
        weekChangeGa: function(date) {
            ga('send', 'event', '价格带分析', '选择报告时间', date)
        },
        catChangeGa: function(cat) {
            var catList = this.catList
            this.selectedCatLabels = this.getSelectedCatLabels(cat, catList)
            ga('send', 'event', '价格带分析', '选择报告品类', this.selectedCatLabels.slice(-1)[0].label)
        },
        formatDate: function(date) {
            var year = date.getFullYear(),
                month = (date.getMonth() + 1) < 10
                    ? '0' + (date.getMonth() + 1)
                    : date.getMonth() + 1,

                day = date.getDate() < 10
                    ? '0' + date.getDate()
                    : date.getDate()

            return year + '-' + month + '-' + day
        },

        recurTree: function(rootList, childJson) {
            var self = this

            rootList.forEach(function(idKey, index) {
                rootList[index] = {
                    id: childJson[idKey].id,
                    label: childJson[idKey].label
                }

                if(childJson[idKey].children) {
                    rootList[index].children = Object.keys(childJson[idKey].children)
                    self.recurTree(rootList[index].children, childJson[idKey].children)
                }
            })
        },

        recurToSelectFirst: function(arr, data) {
            arr.push(data[0].id)

            if(data[0].children) {
                this.recurToSelectFirst(arr, data[0].children)
            }
        },

        getCatList: function() {
            var self = this

            $.get(
                '/api/price_band/v0/category',
                {
                    store_id: this.s_id,
                },
                function(res) {
                    if(res.code === 0) {
                        // var obj = Object.keys(res.data)

                        // self.recurTree(obj, res.data)
                        self.catList = res.data

                        // 无限选中第一个
                        self.selectedCatList = []
                        self.recurToSelectFirst(self.selectedCatList, self.catList)

                        self.submitDisabled = false
                    } else {
                        self.$message({
                            message: res.error_msg,
                            type: 'error'
                        })
                    }
                }
            )
        },

        getSelectedCatLabels: function(idList, catList) {
            return idList.map(function (id) {
                for(let item of catList) {
                    if(item.id == id) {
                        catList = item.children
                        return item
                    }
                }

                return null;
            });
        },

        submit: function() {
            var self = this

            // ga('send', 'event', '价格带分析', '点击确定')

            self.loading = true
            self.isNull = false

            $.get(
                '/api/price_band/v0/list',
                {
                    store_id: this.s_id,
                    cat_id: JSON.stringify(self.selectedCatList),
                    start_date: this.formatDate(this.start),
                    end_date: this.formatDate(this.end),
                },
                function (res) {
                    self.loading = false

                    if (res.code == 0){
                        if(res.data.price_band.length <= 0) {
                            self.isNull = true
                            return
                        }

                        self.$nextTick(function() {
                            self.cacleMainChartData(res.data.sku)
                            self.renderProfitChart(res.data.price_band)
                            self.renderSalesChart(res.data.price_band)
                        })
                    }
                }
            )
        },

        gaTracker: function () {
            var self = this
            ga('send', 'event', '价格带分析', '点击确定')
        },
        getPriceInterval: function(v, k) {
            if(k < 1) {
                k = parseFloat(k)
            } else {
                k = parseInt(k)
            }

            var n = Math.floor(v / k)

            //k=3 2->0 3->0 (0, 3]
            if(v % k === 0) {
                n = n - 1
            }

            return {
                cycle: n,
                interval: '(' + n * k + ', ' + (n + 1) * k + ']'
            }
        },

        cacleMainChartData: function(priceBand) {
            var self = this

            this.mainChart.data = []

            priceBand.price.forEach(function(item, index) {
                self.mainChart.data.push([item, priceBand.sku_num[index]])
            })

            self.mergeMainChartAxis()
        },

        mergeMainChartAxis: function() {
            var self = this,
                result = {},
                tmpData = {},
                chartData = []

            if(!self.mainChart.data) {
                self.$message({
                    message: '图表数据未生成',
                    type: 'warning'
                })

                return
            } else {
                self.mainChart.data.forEach(function(item){
                    result = self.getPriceInterval(item[0], self.selectedPriceInterval)

                    if(tmpData[result.cycle]) {
                        tmpData[result.cycle].yAxis += item[1]
                    } else {
                        tmpData[result.cycle] = {}
                        tmpData[result.cycle].yAxis = item[1]
                        tmpData[result.cycle].xAxis = (result.cycle + 1) * self.selectedPriceInterval
                    }
                })

                for(var i in tmpData) {
                    chartData.push([tmpData[i].xAxis, tmpData[i].yAxis])
                }

                self.renderMainChart(chartData)
            }
        },

        renderMainChart: function(chartData) {
            var self = this

            if(!this.mainChart.obj) {
                this.mainChart.obj = echarts.init($('#mainChart')[0], 'cmTheme')
            }

            this.mainChart.obj.setOption({
                title: {
                    text: self.selectedCatLabels.slice(-1)[0].label + ' 价格带概览图',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    axisPointer: {
                        type: 'shadow'
                    },
                    formatter: function(params) {
                        var result = self.getPriceInterval(
                            params.value[0],
                            self.selectedPriceInterval)

                        return '售价: ' + result.interval +
                               ',</br>SKU数: ' + params.value[1]
                    }
                },
                xAxis: {
                    type: 'value',
                    name: '售价',
                    axisTick: {
                        show: false
                    },
                    splitLine: {
                        show: false
                    },
                    splitNumber: 10
                },
                yAxis: {
                    type: 'value',
                    name: 'SKU数',
                    axisLine: {
                        show: false
                    },
                    axisTick: {
                        show: false
                    },
                    splitLine: {
                        lineStyle: {
                            type: 'dashed'
                        }
                    },
                    splitNumber: 10
                },
                series: [
                    {
                        type: 'scatter',
                        data: chartData
                    },
                    {
                        type: 'bar',
                        barWidth: '1',
                        silent: true,
                        data: chartData
                    }
                ]
            })
        },

        //增加一条重复数据
        comparePrice: function(params) {
            var self = this

            params.price.forEach(function(val) {
                if( val !== 0 && val !== params.data.price) {
                    self[params.chart].yAxis.push(params.itemName)
                    self[params.chart].firstWeek.push(params.data.first_data.profit)
                    self[params.chart].secondWeek.push(params.data.second_data.profit)
                    self[params.chart].thirdWeek.push(params.data.third_data.profit)
                    self[params.chart].salePrice.push(val)
                }
            })
        },

        // 对value进行裁剪，每maxlength一行
        splitString: function(maxLength, value) {
            var str = ''

            for(var i = 0; i < Math.floor(value.length / maxLength) + 1; i++) {
                if(i === 0) {
                    str += value.slice(i * maxLength, (i + 1) * maxLength)
                } else {
                    str += '\n' + value.slice(i * maxLength, (i + 1) * maxLength)
                }
            }

            return str
        },

        renderProfitChart: function(charts) {
            var self = this,
                zoomSize = 6

            this.profitChart.yAxis = []
            this.profitChart.firstWeek = []
            this.profitChart.secondWeek = []
            this.profitChart.thirdWeek = []
            self.profitChart.salePrice = []

            for(var key in charts) {
                self.profitChart.yAxis.push(charts[key].item_name)

                self.profitChart.firstWeek.push(charts[key].first_data.profit)
                self.profitChart.secondWeek.push(charts[key].second_data.profit)
                self.profitChart.thirdWeek.push(charts[key].third_data.profit)
                self.profitChart.salePrice.push(charts[key].price)

                //判断三周价格是否有不同，不同的另加一条data
                // self.comparePrice({
                //     data: charts[key],
                //     itemName: charts[key].item_name,
                //     chart: 'profitChart',
                //     price: [
                //         charts[key].first_data.price,
                //         charts[key].second_data.price,
                //         charts[key].third_data.price
                //     ]
                // })
            }

            if(!this.profitChart.obj) {
                this.profitChart.obj = echarts.init($('#profitChart')[0], 'cmTheme')
            }

            this.profitChart.obj.setOption({
                title: {
                    text: self.selectedCatLabels.slice(-1)[0].label + ' 价格带毛利额图',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                legend: {
                    data: ['T-2周毛利额', 'T-1周毛利额', 'T周毛利额'],
                    left: 'right',
                    orient: 'vertical',
                    itemGap: 5
                },
                grid: {
                    top: '15%',
                    right: '16%',
                    left: '20%'
                },
                xAxis: [
                    {
                        type: 'value',
                        name: '毛利额',
                        position: 'top',
                        axisTick: {
                            show: false
                        },
                    }
                ],
                yAxis: [
                    {
                        type: 'category',
                        data: self.profitChart.yAxis,
                        axisTick: {
                            show: false
                        },
                        axisLabel: {
                            algin: 'left',
                            formatter: function(value) {
                                var index = self.profitChart.yAxis.indexOf(value)

                                var price = index !== -1 ? self.profitChart.salePrice[index] : ''

                                return '{name|' + self.splitString(17, value) + '}\t{price|' + price + '元}'
                            },
                            rich: {
                                name: {
                                    align: 'left'
                                },
                                price: {
                                    color: '#ce5d5a'
                                }
                            }
                        }
                    }
                ],
                dataZoom: [
                    {
                        type: 'slider',
                        right: 50,
                        top: 100,
                        height: '70%',
                        yAxisIndex: [0],
                        labelFormatter: (value) => {
                            return self.splitString(8, self.profitChart.yAxis[value])
                        },
                        start: 100,
                        end: 90
                    },
                    {
                        type: 'inside',
                        yAxisIndex: [0],
                        start: 100,
                        end: 90
                    }
                ],
                series: [
                    {
                        name: 'T-2周毛利额',
                        type: 'bar',
                        itemStyle: {
                            normal: {
                                color: '#0dddff'
                            }
                        },
                        data: self.profitChart.firstWeek
                    },
                    {
                        name: 'T-1周毛利额',
                        type: 'bar',
                        itemStyle: {
                            normal: {
                                color: '#ff425c'
                            }
                        },
                        data: self.profitChart.secondWeek
                    },
                    {
                        name: 'T周毛利额',
                        type: 'bar',
                        itemStyle: {
                            normal: {
                                color: '#3889ff'
                            }
                        },
                        data: self.profitChart.thirdWeek
                    }
                ]
            })

            this.profitChart.obj.on('click', function (params) {
                self.profitChart.obj.dispatchAction({
                    type: 'dataZoom',
                    startValue: self.profitChart.yAxis[Math.max(params.dataIndex - zoomSize / 2, 0)],
                    endValue: self.profitChart.yAxis[Math.min(params.dataIndex + zoomSize / 2,
                        self.profitChart.yAxis.length - 1)]
                })

                self.salesChart.obj.dispatchAction({
                    type: 'dataZoom',
                    startValue: self.salesChart.yAxis[Math.max(params.dataIndex - zoomSize / 2, 0)],
                    endValue: self.salesChart.yAxis[Math.min(params.dataIndex + zoomSize / 2,
                        self.salesChart.yAxis.length - 1)]
                })
            })

            this.profitChart.obj.on('datazoom', function(params) {
                if(params.batch) {
                    self.salesChart.obj.dispatchAction({
                        type: 'dataZoom',
                        start: params.batch[0].start,
                        end: params.batch[0].end
                    })
                } else {
                    self.salesChart.obj.dispatchAction({
                        type: 'dataZoom',
                        startValue: params.startValue,
                        endValue: params.endValue
                    })
                }
            })

            this.profitChart.obj.on('legendselectchanged', function (params) {
                ga('send', 'event', '价格带分析', '点击' + self.selectedCatLabels.slice(-1)[0].label + params.name + '图例')
            })

            this.profitChart.obj.on('datazoom', function (params) {
                ga('send', 'event', '价格带分析', '缩放' + self.selectedCatLabels.slice(-1)[0].label + '价格带毛利额图例')
            })
        },

        renderSalesChart: function(charts) {
            var self = this,
                zoomSize = 6

            this.salesChart.yAxis = []
            this.salesChart.firstWeek = []
            this.salesChart.secondWeek = []
            this.salesChart.thirdWeek = []
            this.salesChart.salePrice = []

            for(var key in charts) {
                self.salesChart.yAxis.push(charts[key].item_name)

                self.salesChart.firstWeek.push(charts[key].first_data.sales_volume)
                self.salesChart.secondWeek.push(charts[key].second_data.sales_volume)
                self.salesChart.thirdWeek.push(charts[key].third_data.sales_volume)
                self.salesChart.salePrice.push(charts[key].price)

                //判断三周价格是否有不同，不同的另加一条data
                // self.comparePrice({
                //     data: charts[key],
                //     itemName: charts[key].item_name,
                //     chart: 'salesChart',
                //     price: [
                //         charts[key].first_data.price,
                //         charts[key].second_data.price,
                //         charts[key].third_data.price
                //     ]
                // })
            }

            if(!this.salesChart.obj) {
                this.salesChart.obj = echarts.init($('#salesChart')[0], 'cmTheme')
            }

            this.salesChart.obj.setOption({
                title: {
                    text: self.selectedCatLabels.slice(-1)[0].label + ' 价格带销量图',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                legend: {
                    data: ['T-2周销量', 'T-1周销量', 'T周销量'],
                    left: 'right',
                    orient: 'vertical',
                    itemGap: 5
                },
                grid: {
                    top: '15%',
                    right: '16%',
                    left: '20%'
                },
                xAxis: [
                    {
                        type: 'value',
                        name: '销量',
                        position: 'top',
                        axisTick: {
                            show: false
                        },
                    }
                ],
                yAxis: [
                    {
                        type: 'category',
                        data: this.salesChart.yAxis,
                        axisTick: {
                            show: false
                        },
                        axisLabel: {
                            algin: 'left',
                            formatter: function(value) {
                                var index = self.salesChart.yAxis.indexOf(value),
                                    price = index !== -1 ? self.salesChart.salePrice[index] : ''

                                return '{name|' + self.splitString(17, value) + '}\t{price|' + price + '元}'
                            },
                            rich: {
                                name: {
                                    align: 'left'
                                },
                                price: {
                                    color: '#ce5d5a'
                                }
                            }
                        }
                    }
                ],
                dataZoom: [
                    {
                        type: 'slider',
                        right: 50,
                        top: 100,
                        height: '70%',
                        yAxisIndex: [0],
                        labelFormatter: (value) => {
                            return self.splitString(8, self.salesChart.yAxis[value])
                        },
                        start: 100,
                        end: 90
                    },
                    {
                        type: 'inside',
                        yAxisIndex: [0],
                        start: 100,
                        end: 90
                    }
                ],
                series: [
                    {
                        name: 'T-2周销量',
                        type: 'bar',
                        itemStyle: {
                            normal: {
                                color: '#0dddff'
                            }
                        },
                        data: self.salesChart.firstWeek
                    },
                    {
                        name: 'T-1周销量',
                        type: 'bar',
                        itemStyle: {
                            normal: {
                                color: '#ff425c'
                            }
                        },
                        data: self.salesChart.secondWeek
                    },
                    {
                        name: 'T周销量',
                        type: 'bar',
                        itemStyle: {
                            normal: {
                                color: '#3889ff'
                            }
                        },
                        data: self.salesChart.thirdWeek
                    }
                ]
            })


            this.salesChart.obj.on('click', function (params) {
                self.salesChart.obj.dispatchAction({
                    type: 'dataZoom',
                    startValue: self.salesChart.yAxis[Math.max(params.dataIndex - zoomSize / 2, 0)],
                    endValue: self.salesChart.yAxis[Math.min(params.dataIndex + zoomSize / 2,
                        self.salesChart.yAxis.length - 1)]
                })
            })

            this.salesChart.obj.on('legendselectchanged', function (params) {
                ga('send', 'event', '价格带分析', '点击' + self.selectedCatLabels.slice(-1)[0].label + params.name + '图例')
            })

            this.salesChart.obj.on('datazoom', function (params) {
                ga('send', 'event', '价格带分析', '缩放' + self.selectedCatLabels.slice(-1)[0].label + '价格带销量图例')
            })
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .chart-box .chart {
        height: 500px;
        width: 100%;
    }

    .box-card {
        margin-bottom: 15px;
    }

    .cat-selection,
    .date-picker {
        min-width: 300px
    }
</style>
