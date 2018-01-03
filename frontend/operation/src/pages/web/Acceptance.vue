<template>
    <div id="acceptance">
        <div class="ui container" id="simstore-menu">
            <div class="ui modal small" id="modal">
                <div class="header">修改允收期规则</div>
                <div class="content">
                    <form class="ui form">
                        <div class="field">
                            <label>保质期</label>
                            <input type="text" name="best_before" v-model="input_best_before" :disabled="disabled">
                        </div>
                        <label style="font-weight: 700;">允收期（距离生产日）</label>
                        <div class="two fields">
                            <div class="field">
                                <label>国产商品</label>
                                <input type="number" name="acc_date_nationa" placeholder="单位：天" v-model="input_acc_date_nationa">
                            </div>
                            <div class="field">
                                <label>进口商品</label>
                                <input type="number" name="acc_date_intl" placeholder="单位：天" v-model="input_acc_date_intl">
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
                <h3>允收期设置</h3>
                <div class="ui grid left aligned">
                    <div class="eight wide column">
                        <table class="ui celled structured table">
                            <thead>
                                <tr>
                                    <th rowspan="2">保质期</th>
                                    <th colspan="2">允收期（距生产日）／天</th>
                                    <th rowspan="2">操作</th>
                                </tr>
                                <tr>
                                    <th>国产商品</th>
                                    <th>进口商品</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(item, index) in settingTableData" :id="item.id">
                                    <td>{{ item.shelf_life }}</td>
                                    <td>{{ item.china_acceptance_rules }}天以内</td>
                                    <td>{{ item.import_acceptance_rules }}天以内</td>
                                    <td><a @click="setTableRow(item.id,item.shelf_life,item.china_acceptance_rules,item.import_acceptance_rules)">修改</a></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div class="ui segment">
                <h3>商品允收操作日志</h3>
                <div class="ui form check time-select">
                    <div class="inline field">
                        <label>日期：</label>
                        <div class="ui selection dropdown date">
                            <input type="hidden" name="date">
                            <i class="dropdown icon"></i>
                            <div class="default text">请选择</div>
                            <div class="menu">
                                <div class="item" v-for="date in dateList" :data-value="date">{{date}}</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="ui active centered inline large text loader" v-show="loading">加载中</div>
                <div class="ui fluid card" v-show="!loading && (dateList.length<=0 || logTableData.length<=0)">
                    <div class="center aligned content">
                        <i class="big meh icon"></i>
                        <p>暂时还没有生成数据</p>
                    </div>
                </div>
                <table class="ui striped orange sortable celled table" v-show="!loading&&logTableData.length>0">
                    <thead>
                        <tr>
                            <th>允收时间</th>
                            <th>商品内码</th>
                            <th>商品条码</th>
                            <th>商品名</th>
                            <th>规格</th>
                            <th>保质期（天）</th>
                            <th>允收期</th>
                            <th>产地</th>
                            <th>是否允收</th>
                            <th>验收人</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in logTableData">
                            <td>{{ item.operate_time }}</td>
                            <td>{{ item.foreign_item_id }}</td>
                            <td>{{ item.barcode }}</td>
                            <td>{{ item.item_name }}</td>
                            <td>{{ item.spec }}</td>
                            <td>{{ item.shelf_life }}</td>
                            <td>{{ item.acceptance_period }}</td>
                            <td v-if="item.origin===0">国产</td>
                            <td v-else-if="item.origin===1">进口</td>
                            <td v-if="item.status===0">未处理</td>
                            <td v-else-if="item.status===1">允收</td>
                            <td v-else-if="item.status===2">不允收</td>
                            <td>{{ item.operator }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'acceptance',
    props: ['csId', 'sId'],
    data () {
        return {
            cs_id: this.csId,
            s_id: this.sId,
            dateList: [],
            logTableData: [],
            settingTableData: [],
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
    mounted () {
        var _self = this
        _self.init()
        _self.getRulesData()
        _self.getDateOptions()
    },
    methods: {
        //初始化 下拉菜单， 设定好change事件
        init: function() {
            var _self = this
            $(".ui.dropdown.date").dropdown({
                action: "activate",
                onChange: function(value) {
                    _self.getlogTableData(value)
                    _self.loading = true
                }
            });
        },
        //获取规则表格
        getRulesData: function() {
            var _self = this;
            $.ajax({
                url: '/api/v1.0/analytics/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/acceptance/rules',
                type: 'get',
                dataType: 'json',
                success: function(data) {
                    _self.settingTableData = data.data
                }
            })
        },
        //获取日期列表项
        getDateOptions: function() {
            var _self = this;
            $.ajax({
                url: '/api/v1.0/analytics/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/acceptance/date',
                type: 'get',
                dataType: 'json',
                success: function (res) {
                    if (res.code === 0) {
                        _self.dateList = res.data
                        $(".ui.dropdown.date").dropdown("set text", _self.dateList[0])
                        _self.getlogTableData(_self.dateList[0])
                    } else if (res.code === 4) {
                        _self.loading = false
                    }
                }
            })
        },

        //获取表格data
        getlogTableData: function(date) {
            var _self = this;
            $.ajax({
                url: '/api/v1.0/analytics/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/acceptance/log',
                type: 'get',
                dataType: 'json',
                data: {
                    date: date
                },
                success: function (res) {
                    _self.logTableData = res.data
                    _self.loading = false
                    
                }
            })
        },

        //重置各项
        resetValue: function() {
            var _self = this
            _self.disabled = false
            _self.input_acc_date_nationa = null
            _self.input_acc_date_intl = null
            _self.input_best_before = null
            _self.errorMassage = ''
        },

        //编辑一条允收期规则
        setTableRow: function(id, rule_name, made_in_china, made_in_import) {
            var _self = this
            _self.resetValue()
            var old_acc_date_nationa = _self.input_acc_date_nationa = made_in_china
            var old_acc_date_intl = _self.input_acc_date_intl = made_in_import
            _self.input_best_before = rule_name
            _self.disabled = true
            $('#modal').modal({
                onApprove: function() {
                    //新值和旧值相等，不能提交
                    if (Number(_self.input_acc_date_nationa) === Number(old_acc_date_nationa) &&
                        Number(_self.input_acc_date_intl) === Number(old_acc_date_intl)) {
                        _self.errorMassage = '没有任何修改'
                        return false
                    }
                    //有的国产商品默认为空，有的不为空，不为空的不可以修改为空
                    if (_self.input_acc_date_nationa === '' &&
                        old_acc_date_nationa !== null) {
                        _self.errorMassage = '不可以将默认值改为空'
                        return false
                    }
                    //进口商品同理
                    if (_self.input_acc_date_intl === '' &&
                        old_acc_date_intl !== null) {
                        _self.errorMassage = '不可以将默认值改为空'
                        return false
                    }
                    $.ajax({
                        url: '/api/v1.0/analytics/chain-store/' + _self.cs_id + '/store/' + _self.s_id + '/acceptance/rules',
                        type: 'post',
                        dataType: 'json',
                        data: {
                            'import_acceptance_rules': _self.input_acc_date_intl,
                            'id': id,
                            'china_acceptance_rules': _self.input_acc_date_nationa
                        },
                        success: function(data) {
                            _self.settingTableData = data.data;
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
</style>
