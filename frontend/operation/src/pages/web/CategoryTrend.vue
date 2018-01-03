<template>
    <div class="trend">
        <el-tabs v-model="activeTab" type="border-card" @tab-click="zhugeClick">
            <el-tab-pane label="各品类13周趋势" name="week">
                <el-form :inline="true">
                    <TreeSelection
                        :treeList="catList"
                        treeRef="cat"
                        :defaultExpanded="['all']"
                        :label="'选择品类'"
                        @get-selected-list="(selectedList) => { selectedCatList = selectedList }"
                        @get-selected-option="(selectedObj) => { selectedCatOption = selectedObj }"
                    ></TreeSelection>

                    <el-form-item>
                        <el-button type="primary" class="sales-submit-btn" :disabled="submitDisabled" @click="submit(),gaTracker()">
                            {{ submitDisabled ? 'loading' : '确定' }}
                        </el-button>
                    </el-form-item>
                </el-form>

                <div class="ui active centered inline large text loader" v-show="loading">加载中</div>
                <div v-show="!loading">
                    <div class="ui three column doubling stackable grid">
                        <div class="row">
                            <div class="left floated column">
                                <h4 class="ui header">各品类13周销售额趋势图</h4>
                            </div>
                            <div class="right floated column">
                                <h4 class="ui header">报告日期：{{ reportDate }}</h4>
                            </div>
                        </div>

                        <div class="four wide column" v-for="item in idList" v-show="!isNull">
                            <div :id="'week' + item" style="min-height: 200px; width: 200px;">
                            </div>
                        </div>

                        <div class="centered column center aligned"
                             v-show="isNull">
                            <div class="ui large info message">
                                <i class="big meh icon"></i>
                                <p>暂时还没有生成数据</p>
                            </div>
                        </div>
                    </div>
                </div>
            </el-tab-pane>

            <el-tab-pane label="各品类月销售趋势" name="month">
                <MonthSales :actived="monthTabActived"></MonthSales>
            </el-tab-pane>
        </el-tabs>
    </div>
</template>

<script>
import TreeSelection from '@/components/TreeSelection.vue'
import MonthSales from './MonthSales.vue'

export default {
    name: 'trendWeek',
    data () {
        return {
            s_id: this.$route.params.s_id,

            activeTab: 'week',
            monthTabActived: false,

            catList: [],
            selectedCatList: [],
            selectedCatOption: [],

            submitDisabled: true,

            loading: true,
            isNull: false,

            reportDate: '',
            chartList: [],
            nameList: []
        }
    },

    components: {
        'MonthSales': MonthSales,
        'TreeSelection': TreeSelection
    },

    watch: {
        submitDisabled: function(newValue) {
            if(newValue === false) {
                this.submit()
            }
        },

        activeTab: function(newValue) {
            if(newValue === 'month') {
                this.monthTabActived = true
            }
        }
    },

    computed: {
        idList: function() {
            return Object.keys(this.chartList)
        }
    },

    mounted() {
        this.getCatList()
    },

    methods: {
        zhugeClick (data) {
            zhuge.track(data.label + '(品类销售趋势图)')
            ga('send', 'event', '品类销售趋势图', '选择' + data.label)
        },
        beautify_value: function(value) {
            if (value > 1000) {
                return Math.ceil(value / 1000) * 1000
            }
            else if (value > 100 && value <= 1000) {
                return Math.ceil(value / 100) * 100
            }
            else if (value >= 0) {
                return Math.ceil(value / 10) * 10
            }
            else if (value < 0  && value >= -100) {
                return Math.floor(value / 10) * 10
            }
            else if (value >= -1000 && value < -100) {
                return Math.floor(value / 100) * 100
            }
            else if (value < -1000) {
                return Math.floor(value / 1000) * 1000
            }
        },

        recurTree: function(obj) {
            var self = this

            // 把level拼进id里
            obj.forEach(function(item) {
                item.id = item.id + '#' + item.level

                if(item.children) {
                    self.recurTree(item.children)
                }
            })
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
                        // var obj = res.data

                        // self.recurTree(obj)

                        self.catList = [
                            {
                                id: 'all',
                                label: '全部一级品类',
                                children: res.data
                            }
                        ]

                        self.$nextTick(function() {
                            self.submitDisabled = false
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

        submit: function() {
            var self = this,
                idList = this.selectedCatList.length === 1 && this.selectedCatOption.children
                    ? this.selectedCatOption.children.map((item) => { return item.id })
                    : this.selectedCatList.map((item) => { return item.id }),

                nameList = this.selectedCatList.length === 1 && this.selectedCatOption.children
                    ? this.selectedCatOption.children.map((item) => { return item.label })
                    : this.selectedCatList.map((item) => { return item.label })

            self.loading = true
            self.nameList = nameList
            //zhuge 埋点
            zhuge.track('确定（各品类13周趋势）', {
                '品类': nameList
            })

            // ga('send', 'event', '品类销售趋势图', '确定(各品类13周趋势)', nameList.join(','))

            $.get(
                '/api/category_trend/v0/thirteen-weeks-sales',
                {
                    store_id: this.s_id,
                    cat_ids: this.selectedCatList.length <= 0 || this.selectedCatList[0].id === 'all'
                        ? JSON.stringify([])
                        : JSON.stringify(idList),
                    cat_names: this.selectedCatList.length <= 0 || this.selectedCatList[0].id === 'all'
                        ? JSON.stringify(['全部一级品类'])
                        : JSON.stringify(nameList)
                },
                function(res) {
                    self.loading = false

                    if(res.code === 0) {
                        if(Object.keys(res.data.cat_weeks_sales) <= 0) {
                            self.isNull = true
                            return
                        }

                        self.isNull = false

                        self.reportDate = res.data.date
                        self.chartList = res.data.cat_weeks_sales

                        self.$nextTick(function() {
                            console.log('drawing week data')
                            self.loadSalesChart()
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
        gaTracker: function () {
            var self = this
            ga('send', 'event', '品类销售趋势图', '确定(各品类13周趋势)', self.nameList.join(','))
        },

        loadSalesChart: function() {
            var self = this

            this.idList.forEach(function(id) {
                echarts.dispose($('#week'+ id)[0])

                var thisData = self.chartList[id]

                thisData.obj = echarts.init($('#week'+ id)[0], 'cmTheme')
                thisData.obj.setOption({
                    title: {
                        text: thisData.name,
                        left: 'center',
                        top: '10%',
                        textStyle: {
                            fontSize: 16
                        },
                    },
                    color: ['#FF5422'],
                    legend: {
                        show: false,
                    },
                    grid: {
                        show: true,
                        bottom: '15%',
                        containLabel: true
                    },
                    xAxis: [
                        {
                            type: 'category',
                            data: Array.apply(null, {length: 13}).map(Number.call, Number),
                            axisTick: {
                                alignWithLabel: true,
                                show: false,
                            },
                            axisLabel: {
                                show: false,
                            },
                        }
                    ],
                    yAxis: [
                        {
                            min: 0,
                            max: self.beautify_value(thisData.max),
                            interval: self.beautify_value(thisData.max) / 2
                        }
                    ],
                    series: [
                        {
                            name: '销售额',
                            type: 'bar',
                            barWidth: '50%',
                            data: thisData.sales,
                            itemStyle: {
                                normal: {
                                    color: '#ffbe00',
                                },
                            },
                        }
                    ]
                })
            })
        }
    }
}
</script>

<style scoped>
    .box-card {
        margin-bottom: 15px;
    }

    .chart-info {
        text-align: center;
    }
</style>
