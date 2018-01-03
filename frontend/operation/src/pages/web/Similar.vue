<template>
    <div class="similar">
        <div class="ui container" id="simstore-menu">
            <div class="ui segment">
                <div class="ui form check time-select">
                    <div class="inline field">
                        <label>报告周期：</label>
                        <Selection addClass="selection" name="year"
                                   defaultText="请选择"
                                   :options="years" v-model="selectedYear"
                                   id="yearSelection"
                        ></Selection>
                        <span class="selection-label">年</span>

                        <Selection addClass="selection" name="month"
                                   defaultText="请选择"
                                   :options="months" v-model="selectedMonth"
                                   id="monthSelection"
                        ></Selection>
                        <span class="selection-label">月</span>

                        <Selection addClass="selection" name="week"
                                   defaultText="请选择"
                                   :options="weeks" v-model="selectedWeek"
                                   id="weekSelection"
                        ></Selection>
                    </div>
                </div>
            </div>

            <div class="ui segment chart-box" id="chartBox">
                <div class="ui active centered inline large text loader"
                     v-show="loading">加载中</div>
                <div class="chart-group" v-for="item in chartList">
                    <h3>{{ item.catName }}</h3>
                    <div class="chart" :id="item.id + 'advantege'"></div>
                    <div class="chart" :id="item.id + 'disadvantege'" ></div>
                  </div>
            </div>
        </div>
    </div>
</template>

<script>
import Selection from '@/components/Selection.vue'

export default {
    name: 'similar',
    data () {
        return {
            cs_id: this.$route.params.cs_id,
            s_id: this.$route.params.s_id,

            chartList: [],

            periods: {},
            years: [],
            months: [],
            weeks: [],
            selectedYear: null,
            selectedMonth: null,
            selectedWeek: null,

            loading: true
        }
    },

    components: {
        'Selection': Selection
    },

    watch: {
        chartList: function(newValue) {
            var self = this

            this.$nextTick(function(){
                newValue.forEach(function(item){
                    self.loadChart(item, 'advantege')
                    self.loadChart(item, 'disadvantege')
                })
            })
        },

        selectedYear: function(newValue, oldValue) {
            if(oldValue !== null && newValue !== null) {
                this.months = Object.keys(this.periods[newValue])
                    .sort(function(a, b){return b - a})
                this.weeks = []

                $('#monthSelection').dropdown('set text', '请选择')
                $('#weekSelection').dropdown('set text', '请选择')
            }
        },

        selectedMonth: function(newValue, oldValue) {
            var self = this
            let tmpWeeks = []

            if(oldValue !== null && newValue !== null) {
                tmpWeeks = this.periods[this.selectedYear][newValue]

                self.weeks = tmpWeeks.map((item) => {
                    return item.replace('@', '到')
                })

                $('#weekSelection').dropdown('set text', '请选择')
            }
        },

        selectedWeek: function(newValue, oldValue) {
            if(oldValue !== null && newValue !== null) {
                if(this.selectedCatThree !== null) {
                    this.getData(newValue)

                    this.loading = true
                }
            }
        },
    },

    mounted() {
        this.getDateOptions()
    },

    methods: {
        getDateOptions: function() {
            var self = this,
                url = '/api/v1/operation/chain-store/' + self.cs_id +
                      '/store/' + self.s_id + '/similar/periods'

            $.get(url, function (res) {
                if (res.code == 0){
                    self.periods = res.periods
                    self.years = Object.keys(res.periods)
                        .sort(function(a, b){return b - a})
                    self.selectedYear = self.years[0]

                    self.months = Object.keys(res.periods[self.selectedYear])
                        .sort(function(a, b){return b - a})
                    self.selectedMonth = self.months[0]

                    var weekList = res.periods[self.selectedYear][self.selectedMonth]
                    self.weeks = weekList.map(function(item) {
                        return item.replace('@', '到')
                    })
                    self.selectedWeek = self.weeks[self.weeks.length - 1]

                    self.getData(self.selectedWeek)
                }
            })
        },

        getData: function(week) {
            var self = this,
                url = '/api/v1/operation/chain-store/' + self.cs_id +
                      '/store/' + self.s_id + '/similar'

            $.get(
                url,
                {
                    start: week.split('到')[0],
                    end: week.split('到')[1]
                },
                function(res) {
                    if (res.code == 0){
                        var params = JSON.parse(res.data)
                        self.initChart(params.charts)
                        self.loading = false
                    }
                }
            )
        },

        initChart: function(chartsData) {
            var self = this

            self.chartList = []

            for(var catId in chartsData) {
                self.chartList.push({
                    catName: chartsData[catId].cat_name,
                    id: catId,
                    advantege: chartsData[catId].advantege,
                    disadvantege: chartsData[catId].disadvantege,
                    advantegeChart: null,
                    disadvantegeChart: null
                })
            }
        },

        loadChart: function(data, category) {
            var xAxisValue = [],
                title = (category === 'advantege' ? '优势商品' : '劣势商品')

            // 如果这个品没有 优势商品／劣势商品，空着不画
            if(!data[category]) {
                return
            }

            data[category].item_id.forEach(function(id, index) {
                xAxisValue.push(id + data[category].item_name[index])
            })

            echarts.dispose($('#' + data.id + category)[0])
            data[category + 'chart'] = echarts.init($('#' + data.id + category)[0], 'cmTheme')
            data[category + 'chart'].setOption({
                title: {
                    text: title,
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
                    data: ['毛利额', '销量', '相似店毛利额', '相似店销量'],
                },
                xAxis: [
                    {
                        type: 'category',
                        data: xAxisValue,
                        axisPointer: {
                            type: 'shadow'
                        },
                        axisLabel: {
                            formatter: function(val){
                                return val.slice(0, 6)
                            }
                        },
                    }
                ],
                yAxis: [
                    {
                        type: 'value',
                        name: '毛利额／元',
                    },
                    {
                        type: 'value',
                        name: '销量',
                    }
                ],
                series: [
                    {
                        name: '毛利额',
                        type: 'bar',
                        barWidth: 15,
                        data: data[category].store_gross_profit
                    },
                    {
                        name: '销量',
                        type: 'line',
                        itemStyle: {
                            normal: {
                                color: '#d48265'
                            }
                        },
                        yAxisIndex: 1,
                        data: data[category].store_qty
                    },
                    {
                        name: '相似店毛利额',
                        type: 'bar',
                        barWidth: 15,
                        data: data[category].simstore_gross_profit
                    },
                    {
                        name: '相似店销量',
                        type: 'line',
                        yAxisIndex: 1,
                        data: data[category].simstore_qty
                    }
                ]
            })
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .chart-box .chart {
        height: 400px;
        width: 450px;
    }

    .chart-box > .chart-group > div {
        display: inline-block;
    }

    .selection-label {
        margin-left: 1rem;
    }
</style>
