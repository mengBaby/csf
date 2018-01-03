<template>
    <div class="loss">
        <h3 class="ui header">机会损失分析周报</h3>
        <div class="ui borderless stackable menu loss-menu" id="loss-menu">
            <div class="ui item">报告周期：</div>

            <div class="ui item">
                <Selection addClass="selection year-loss-v0.7pc" name="year"
                           defaultText="请选择" :class="{ disabled: loading }"
                           :options="years" v-model="selectedYear"
                           id="yearSelection"
                ></Selection>
                <span style="margin-left:1rem">年</span>
            </div>

            <div class="ui item">
                <Selection addClass="selection month-loss-v0.7pc" name="month"
                           defaultText="请选择" :class="{ disabled: loading }"
                           :options="mons" v-model="selectedMonth"
                           id="monthSelection"
                ></Selection>
                <span style="margin-left:1rem">月</span>
            </div>

            <div class="ui item">
                <Selection addClass="selection time-loss-v0.7pc" name="week"
                           defaultText="请选择" :class="{ disabled: loading }"
                           textFiled="text" valueFiled="val"
                           :options="weeks" v-model="selectedWeek"
                           id="weekSelection"
                ></Selection>
            </div>
        </div>

        <div id="stats" class="stats">
            <div class="ui active centered inline large text loader qwq"
                 v-show="loading">加载中</div>
            <div class="ui fluid card" style="display:none"
                 v-show="!loading && !cat_stats.length">
                <div class="center aligned content">
                    <i class="big meh icon"></i>
                    <p>暂时还没有生成数据</p>
                </div>
            </div>

            <div class="ui styled fluid accordion" v-for="cat in cat_stats"
                 v-show="cat_stats.length" style="display:none">
                <div class="ui header title category-loss-v0.7pc"
                     v-on:click="categoryLossZhuge(cat.category_name)">
                    <i class="dropdown icon"></i>
                    <span class="header">
                        品类: {{ cat.category_name }}&nbsp;&nbsp;&nbsp;
                        {{ cat.cat_sales | toFixed }}
                    </span>
                </div>

                <div class="content">
                    <table class="ui striped orange sortable table">
                        <thead>
                            <tr>
                                <th>序号</th>
                                <th>商品内码</th>
                                <th>商品名称</th>
                                <th>周不动销天数</th>
                                <th class="no-sort">
                                    <span>周不动销天数</br>趋势图</span>
                                </th>
                                <th>该周期末库存</th>
                                <th>周销量</th>
                                <th class="no-sort">
                                    <span>周销量</br>趋势图</span>
                                </th>
                                <th>本周巡查反馈</th>
                                <th>本周巡查人</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="stats in cat.cat_stats">
                                <td :data-sort-value="stats.row_num">{{ stats.row_num }}</td>
                                <td :data-sort-value="stats.item_id">{{ stats.item_id }}</td>
                                <td>{{ stats.item_name }}</td>
                                <td :data-sort-value="stats.us_dates" class="danger">{{ stats.us_dates }}</td>
                                <td :data-bar-values="stats.weeks_unsale_days" class="inline-bar unsale">
                                    <span class="ui active centered inline loader"></span>
                                </td>
                                <td :data-sort-value="stats.sun_inv_qty" class="danger">
                                    {{ stats.sun_inv_qty }}
                                </td>
                                <td :data-sort-value="stats.weeks_sale_qty[6]" class="danger">
                                    {{ stats.weeks_sale_qty[6] }}
                                </td>
                                <td :data-bar-values="stats.weeks_sale_qty" class="inline-bar qunatity">
                                    <span class="ui active centered inline loader"></span>
                                </td>
                                <td :data-sort-value="stats.feedback_text">
                                    {{ stats.feedback_text }}
                                </td>
                                <td :data-sort-value="stats.feedback_by">
                                    {{ stats.feedback_by }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
// test data
import json from '@/assets/json/loss.json'
import 'jquery-tablesort'
import Selection from '@/components/Selection.vue'

export default {
    name: 'loss',
    data () {
        return {
            cs_id: this.$route.params.cs_id,
            s_id: this.$route.params.s_id,

            periods: {},
            years: [],
            mons: [],
            weeks: [],
            selectedYear: null,
            selectedMonth: null,
            selectedWeek: null,

            cat_stats: [],
            loading: true,
        }
    },

    components: {
        'Selection': Selection
    },

    watch: {
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
            if(oldValue !== null && newValue !== null) {
                this.weeks = this.periods[this.selectedYear][newValue]

                $('#weekSelection').dropdown('set text', '请选择')
            }
        },

        selectedWeek: function(newValue, oldValue) {
            if(oldValue !== null && newValue !== null) {
                this.loadData(newValue)
            }
        },
    },

    mounted() {
        this.getPeriods()
    },

    filters: {
        toFixed: function(num) {
            if (Number.isNaN(num)) {
                return num
            } else {
                return num.toFixed(2).toString().replace(/^\d+/g,
                    (m) => m.replace(/(?=(?!^)(\d{3})+$)/g, ','))
            }
        },
    },

    methods: {
        getPeriods: function() {
            var self = this,
                url = '/api/v1/operation/chain-store/' + self.cs_id +
                      '/store/' + self.s_id + '/loss/periods'

            $.get(url, function (res) {
                if (res.code == 0){
                    self.periods = res.periods
                    self.years = Object.keys(res.periods)
                        .sort(function(a, b){return b-a})
                    self.selectedYear = self.years[0]

                    self.mons = Object.keys(res.periods[self.selectedYear])
                        .sort(function(a, b){return b-a})
                    self.selectedMonth = self.mons[0]

                    self.weeks = res.periods[self.selectedYear][self.selectedMonth]
                    self.selectedWeek = self.weeks[0].val

                    self.loadData(self.selectedWeek)
                }
            })
        },

        categoryLossZhuge: function (name) {
            zhuge.track('品类(机会损失分析)', {
                '品类': name
            })
        },

        loadData: function(period) {
            var self = this,
                period_arr = period.split('@'),
                url = '/api/v1/operation/chain-store/' + self.cs_id +
                      '/store/' + self.s_id + '/loss' + '?start=' +
                      period_arr[0] + '&end=' + period_arr[1]

            if (period_arr.length != 2) {
                console.error('period error: ' + period)
                return
            }

            self.cat_stats = []
            self.loading = true

            // $.get(url, function(res) {
            //     if (res.code == 0) {
                    var res = json //test data

                    self.cat_stats = res.stats

                    self.$nextTick(function (){
                        $('table.sortable').tablesort({})

                        self.drawSparklines()

                        $('#stats .accordion').accordion()
                            .filter(':first').accordion('toggle', 0)
                    })
                // }
                self.loading = false
            // })
        },

        drawSparklines: function() {
            $('td.inline-bar').each(function(){
                var data = $(this).data('bar-values'),
                    hasUnsale = $(this).hasClass('unsale')

                if (data){
                    var chartSpan = $(this).children('span').eq(0)

                    chartSpan.removeClass()

                    if (hasUnsale) {
                        chartSpan.sparkline(data.split(','), {
                            type: 'bar',
                            barColor: '#f2711c',
                            height: '25',
                            barWidth: '9',
                            barSpacing: '3',
                            chartRangeMax: 7,
                            chartRangeMin: 0
                        })
                    } else {
                        chartSpan.sparkline(data.split(','), {
                            type: 'bar',
                            barColor: '#9933ff',
                            height: '25',
                            barWidth: '9',
                            barSpacing: '3',
                            chartRangeMin: 0
                        })
                    }
                }
            })
        }
    } //methods
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    @media (max-width: 900px) and (min-width: 800px) {
        .loss-menu .ui.item {
            padding-right: 0;
        }
    }

    @media (max-width: 1250px) and (min-width: 800px) {
        table {
            display: inline-block!important;
            overflow-x: scroll;
        }
    }

    .ui.dropdown.year,
    .ui.dropdown.mon {
        min-width: 4rem;
    }

    .ui.ui.dropdown.week {
        min-width: 15rem;
    }

    .stats {
        padding-bottom: 14px;
    }

    .stats .accordion {
        margin-bottom: 10px;
    }

    .stats .accordion table thead tr th {
        cursor: pointer;

        color: #f2711c;
    }

    table tbody td.danger {
        color: red;
    }

    table tbody td.success {
        color: green;
    }

    span.ui.loader {
        z-index: 100;
    }

    .ui.sortable.table thead th:not(.no-sort):not(.sorted):after {
        display: inline-block;

        content: '\f0dc';
    }
</style>

<style>
    .jqstooltip {
        height: 40px;
        width: 55px;
    }
</style>
