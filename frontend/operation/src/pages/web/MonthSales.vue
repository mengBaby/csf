<template>
    <div class="month-sales">
        <el-form :inline="true">
            <TreeSelection
                :treeList="catList"
                treeRef="cat"
                :label="'选择品类'"
                :defaultExpanded="['all']"
                @get-selected-list="(selectedList) => { selectedCatList = selectedList}"
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
            <div class="centered column center aligned" v-show="isNull">
                <div class="ui large info message">
                    <i class="big meh icon"></i>
                    <p>暂时还没有生成数据</p>
                </div>
            </div>

            <div class="chart-box" v-show="!isNull">
                <h3 class="ui right aligned header">报告日期：{{ reportDate }}</h3>
                <div class="chart" v-for="item in idList" :id="'month' + item"></div>
            </div>
        </div>
    </div>
</template>

<script>
import TreeSelection from '@/components/TreeSelection.vue'

export default {
    name: 'trendMonth',
    props: {
        actived: {
            type: Boolean,
            default: false
        }
    },

    data () {
        return {
            s_id: this.$route.params.s_id,

            catList: [],
            selectedCatList: [],
            selectedCatOption: [],

            submitDisabled: true,

            chartList: {},
            reportDate: '',

            loading: false,
            isNull: false,
            nameList: []
        }
    },

    components: {
        'TreeSelection': TreeSelection
    },

    watch: {
        actived: function(newValue) {
            if(newValue === true) {
                this.getCatList()
            }
        },

        submitDisabled: function(newValue) {
            if(newValue === false) {
                this.submit()
            }
        }
    },

    computed: {
        idList: function() {
            return Object.keys(this.chartList)
        }
    },

    mounted() {
        // this.getCatList()
    },

    methods: {
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

        submit: function() {
            var self = this,
                idList = this.selectedCatList.length === 1 && this.selectedCatOption.children
                    ? this.selectedCatOption.children.map((item) => { return item.id })
                    : this.selectedCatList.map((item) => { return item.id }),

                nameList = this.selectedCatList.length === 1 && this.selectedCatOption.children
                    ? this.selectedCatOption.children.map((item) => { return item.label })
                    : this.selectedCatList.map((item) => { return item.label })

            this.loading = true
            self.nameList = nameList
            //zhuge 埋点
            zhuge.track('确定（各品类月销售趋势）', {
                '品类': nameList
            })

            // ga('send', 'event', '品类销售趋势图', '确定(各品类月销售趋势)', nameList)

            $.get(
                '/api/category_trend/v0/month-sales',
                {
                    store_id: this.s_id,
                    cat_ids: this.selectedCatList.length <= 0 || this.selectedCatList[0].id === 'all'
                        ? JSON.stringify([])
                        : JSON.stringify(idList),
                    cat_names: this.selectedCatList.length <= 0 || this.selectedCatList[0].id === 'all'
                        ? JSON.stringify(['全部一级品类'])
                        : JSON.stringify(nameList)
                },
                function (res){
                    self.loading = false

                    if(res.code === 0) {
                        if(Object.keys(res.data.sales) <= 0) {
                            self.isNull = true
                            return
                        }

                        self.isNull = false

                        self.chartList = res.data.sales
                        self.reportDate = res.data.date

                        self.$nextTick(function() {
                            console.log('drawing month data')
                            self.loadMonthChart()
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
            ga('send', 'event', '品类销售趋势图', '确定(各品类月销售趋势)', self.nameList.join(','))
        },
        loadMonthChart: function() {
            var self = this,
                currentYear = new Date().getFullYear()

            this.idList.forEach(function(key) {
                let thisData = self.chartList[key]

                echarts.dispose($('#month'+ key)[0])

                thisData.obj = echarts.init($('#month'+ key)[0], 'cmTheme')

                thisData.obj.setOption({
                    title: {
                        text: thisData.name,
                        left: 'center',
                        top: '20'
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross',
                            crossStyle: {
                                color: '#999'
                            }
                        }
                    },
                    legend: {
                        data: [(currentYear - 1).toString(), currentYear.toString()],
                    },
                    xAxis: [
                        {
                            type: 'category',
                            name: '月份',
                            data: ['1月', '2月', '3月', '4月', '5月', '6月',
                                '7月', '8月', '9月', '10月', '11月', '12月'],
                            axisPointer: {
                                type: 'shadow'
                            }
                        }
                    ],
                    yAxis: [
                        {
                            type: 'value',
                            name: '销售额／元',
                        }
                    ],
                    series: [
                        {
                            name: currentYear - 1,
                            type: 'bar',
                            barWidth: 15,
                            data: thisData.last_year_sales.map((num) => {
                                return num.toFixed(0)
                            })
                        },
                        {
                            name: currentYear,
                            type: 'bar',
                            barWidth: 15,
                            data: thisData.this_year_sales.map((num) => {
                                return num.toFixed(0)
                            })
                        }
                    ]
                })

                thisData.obj.on('legendselectchanged', function (params) {
                    ga('send', 'event', '品类销售趋势图', '点击' + thisData.name + params.name + '图例')
                })
            })
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .chart {
        height: 400px;
        width: 1000px;
    }
</style>
