<template>
    <div class="advent">
        <div class="ui container" id="simstore-menu">
            <div class="ui modal small" id="modal">
                <div class="header">修改临期规则</div>
                <div class="content">
                    <form class="ui form">
                        <div class="field">
                            <label>保质期</label>
                            <input type="text" name="best_before" v-model="input_best_before" :disabled="disabled">
                        </div>
                        <label style="font-weight: 700;">临期（距离生产日）</label>
                        <div class="two fields">
                            <div class="field">
                                <label>国产商品</label>
                                <input type="text" name="acc_date_nationa" placeholder="单位：天" v-model="input_acc_date_nationa">
                            </div>
                            <div class="field">
                                <label>进口商品</label>
                                <input type="text" name="acc_date_intl" placeholder="单位：天" v-model="input_acc_date_intl">
                            </div>
                        </div>
                    </form>
                </div>
                <div class="ui bottom negative message" v-show="errorMassage != ''">{{ errorMassage }}</div>
                <div class="actions">
                    <button class="ui primary button approve">确定</button>
                    <button class="ui button cancel">取消</button>
                </div>
            </div>
            <div class="ui segment">
                <h3>临期设置</h3>
                <h5 style="color: #ff4a0c;margin-top: 0;">注：临期设置修改一周后生效</h5>
                <div class="ui grid left aligned">
                    <div class="eight wide column">
                        <table class="ui celled structured table">
                            <thead>
                                <tr>
                                    <th rowspan="2">保质期</th>
                                    <th colspan="2">临期（距生产日）／天</th>
                                    <th rowspan="2">操作</th>
                                </tr>
                                <tr>
                                    <th>国产商品</th>
                                    <th>进口商品</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(item, index) in settingTableData" :id="item.id">
                                    <td>{{ item.rule_name }}</td>
                                    <td>{{ item.made_in_china }}天以内</td>
                                    <td>{{ item.made_in_import }}天以内</td>
                                    <td><a @click="setTableRow(item.id,item.rule_name,item.made_in_china,item.made_in_import)">修改</a></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div class="ui segment">
                <h3>商品临期操作日志</h3>
                <div class="ui form check time-select">
                    <div class="inline field">
                        <label>报告周期：</label>
                        <div class="ui selection dropdown year">
                            <input type="hidden" name="year" :value="selectedYear">
                            <i class="dropdown icon"></i>
                            <div class="default text">请选择</div>
                            <div class="menu">
                                <div class="item" v-for="year in years" :data-value="year">
                                    {{ year }}
                                </div>
                            </div>
                        </div>
                        <span class="selection-label">年</span>
                        <div class="ui selection dropdown mon">
                            <input type="hidden" name="month" :value="selectedMonth">
                            <i class="dropdown icon"></i>
                            <div class="default text">请选择</div>
                            <div class="menu">
                                <div class="item" v-for="mon in months" :data-value="mon">{{ mon }}</div>
                            </div>
                        </div>
                        <span class="selection-label">月</span>
                        <div class="ui selection dropdown week">
                            <input type="hidden" name="week" :value="selectedWeek">
                            <i class="dropdown icon"></i>
                            <div class="default text">请选择</div>
                            <div class="menu">
                                <div class="item" v-for="week in weeks" :data-value="week">{{ week }}</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="ui active centered inline large text loader" v-show="loading">加载中</div>
                <div class="ui styled fluid accordion" v-for="(catItem, catIndex) in reportData" v-show="!loading&&catItem.class_data.length>0">
                    <div class="ui header title" :class="{ active: catIndex === 0 }">
                        <i class="dropdown icon"></i>
                        <span class="header">品类: {{catItem.cat_name}}</span>
                    </div>
                    <div class="content" :class="{ active: catIndex === 0 }">
                        <table class="ui striped orange sortable celled table">
                            <thead>
                                <tr class="center aligned">
                                    <th>序号</th>
                                    <th>商品内码</th>
                                    <th>商品名</th>
                                    <th>保质期</th>
                                    <th>临期状态</th>
                                    <th>库存</th>
                                    <th>巡查反馈</th>
                                    <th>巡查日期</th>
                                    <th>巡查人</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(item, index) in catItem.class_data" class="center aligned">
                                    <td>{{ index - 0 + 1 }}</td>
                                    <td>{{ item.id }}</td>
                                    <td>{{ item.item_name }}</td>
                                    <td>{{ item.shelf_life }}</td>
                                    <td>{{ item.near_status }}</td>
                                    <td>{{ item.stock }}</td>
                                    <td>{{ item.feedback_text }}</td>
                                    <td>{{ item.feedback_time }}</td>
                                    <td>{{ item.feedback_by }}</td>
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
    name: 'advent',
    props: ['csId', 'sId'],
    data () {
        return {
            cs_id: this.csId,
            s_id: this.sId,
            periods: {},
            years: [],
            months: [],
            weeks: [],
            selectedYear: null,
            selectedMonth: null,
            selectedWeek: null,
            reportData: [],
            settingTableData: [],
            // 临期 model中input
            input_acc_date_nationa: null,
            input_acc_date_intl: null,
            input_best_before: null,
            disabled: false,
            errorMassage: '',
            loading: true
        }
    },
    computed: {
        isEmpty() {
            var _self = this
            return ($.trim(_self.input_acc_date_nationa === '') ||
                $.trim(_self.input_acc_date_intl === '') ||
                $.trim(_self.input_best_before === ''))
        }
    },
    mounted: function() {
        var _self = this
        _self.init()
        _self.getRulesData()
        _self.getDateOptions()
    },
    methods: {
        init: function() {
            var _self = this
            $('.ui.dropdown.year').dropdown({
                action: 'activate',
                onChange: function(value) {
                    _self.selectedYear = value
                    _self.selectedMonth = null
                    _self.months = Object.keys(_self.periods[value])
                        .sort(function(a, b) { return b - a })
                    _self.weeks = null

                    $('.ui.dropdown.mon').dropdown('set text', '请选择')
                    $('.ui.dropdown.week').dropdown('set text', '请选择')
                }
            })
            $('.ui.dropdown.mon').dropdown({
                action: 'activate',
                onChange: function(value) {
                    _self.selectedMonth = value
                    _self.selectedWeek = null
                    _self.weeks = _self.periods[_self.selectedYear][value]

                    $('.ui.dropdown.week').dropdown('set text', '请选择')
                }
            })
            $('.ui.dropdown.week').dropdown({
                action: 'activate',
                onChange: function(value) {
                    _self.selectedWeek = value
                    _self.getReportData(value)
                    _self.loading = true
                }
            })
        },
        //获取规则表格
        getRulesData: function() {
            var _self = this;
            $.ajax({
                url: '/api/v1/operation/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/near/rules',
                type: 'get',
                dataType: 'json',
                success: function(data) {
                    _self.settingTableData = data.data
                }
            })
        },
        // 获取日期列表项
        getDateOptions: function() {
            var _self = this;
            $.ajax({
                url: '/api/v1/operation/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/near/date',
                type: 'get',
                dataType: 'json',
                success: function(data) {
                    _self.periods = data.data

                    _self.years = Object.keys(_self.periods)
                        .sort(function(a, b) { return b - a })
                    _self.selectedYear = _self.years[0]

                    _self.months = Object.keys(_self.periods[_self.selectedYear])
                        .sort(function(a, b) { return b - a })
                    _self.selectedMonth = _self.months[0]

                    var weekList = _self.periods[_self.selectedYear][_self.selectedMonth]
                    weekList.forEach(function(item) {
                        _self.weeks.push(item)
                    });
                    _self.selectedWeek = _self.weeks[0]

                    $('.ui.dropdown.year').dropdown('set text', _self.selectedYear)
                    $('.ui.dropdown.mon').dropdown('set text', _self.selectedMonth)
                    $('.ui.dropdown.week').dropdown('set text', _self.selectedWeek)

                    // 以第一个week为默认值传递
                    _self.getReportData(_self.selectedWeek)
                }
            })
        },
        // 获取报告表格数据
        getReportData: function(date) {
            var _self = this
            $.ajax({
                url: '/api/v1/operation/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/near/data',
                type: 'get',
                dataType: 'json',
                data: {
                    periods: date
                },
                success: function(data) {
                    _self.reportData = data.data
                    _self.$nextTick(function() {
                        $('.ui.accordion').accordion('refresh')
                    })
                    _self.loading = false
                }
            })
        },
        // 重置以避免add和set互相影响
        resetValue: function() {
            var _self = this;
            _self.disabled = false
            _self.input_acc_date_nationa = ''
            _self.input_acc_date_intl = ''
            _self.input_best_before = ''
            _self.errorMassage = ''
        },
        // 编辑临期规则
        setTableRow: function(id, rule_name, made_in_china, made_in_import) {
            var _self = this
            _self.resetValue()
            var old_acc_date_nationa = _self.input_acc_date_nationa = made_in_china
            var old_acc_date_intl = _self.input_acc_date_intl = made_in_import
            _self.input_best_before = rule_name
            _self.disabled = true
            $('#modal').modal({
                onApprove: function() {
                    if (Number(_self.input_acc_date_nationa) === Number(old_acc_date_nationa) &&
                        Number(_self.input_acc_date_intl) === Number(old_acc_date_intl)) {
                        _self.errorMassage = '没有任何修改'
                        return false
                    }
                    if (_self.input_acc_date_nationa === '' &&
                        old_acc_date_nationa !== null) {
                        _self.errorMassage = '不可以将默认值改为空'
                        return false
                    }
                    if (_self.input_acc_date_intl === '' &&
                        old_acc_date_intl !== null) {
                        _self.errorMassage = '不可以将默认值改为空'
                        return false
                    }
                    $.ajax({
                        url: '/api/v1/operation/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/near/rules',
                        type: 'post',
                        dataType: 'json',
                        data: {
                            'rule_name': _self.input_best_before,
                            'made_in_import': _self.input_acc_date_intl,
                            'id': id,
                            'made_in_china': _self.input_acc_date_nationa
                        },
                        success: function(data) {
                            _self.settingTableData = data.data
                        }
                    })
                }
            }).modal('show')
        }
    }
}
</script>

<style scoped>
    a {
        cursor: pointer;
    }

    .ui.bottom.negative.message {
        margin: 0;
    }

    .ui.fluid.accordion {
        margin-top: 10px;
    }
</style>
