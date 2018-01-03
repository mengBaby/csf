<template>
    <div class="overview">
        <el-card class="box-card">
            <el-form :inline="true" class="demo-form-inline">
                <el-form-item label="展示时间">
                    <el-select v-model="selectedTimeUnit" placeholder="请选择" v-show="false">
                        <el-option v-for="option in timeUnitList" :key="option.value"
                                   :label="option.text" :value="option.value"
                        ></el-option>
                    </el-select>
                </el-form-item>

                <div class="block time-slider">
                    <span>{{ formatStartTime }}</span>
                    <el-slider
                        v-model="timeInterval"
                        range
                        :max="sliderLength"
                        :format-tooltip="timeTooltipFormat"
                        :show-stops="showStops"
                    >
                    </el-slider>
                    <span>{{ formatEndTime }}</span>

                    <el-button-group class="slider-toolbar">
                        <el-tooltip class="item" effect="dark" content="整体左移" placement="bottom">
                            <el-button size="mini" icon="arrow-left"
                                      @click="moveSlider('left')"
                            >
                            </el-button>
                        </el-tooltip>

                        <el-tooltip class="item" effect="dark" content="整体右移" placement="bottom">
                            <el-button size="mini" icon="arrow-right"
                                       @click="moveSlider('right')"
                            ></el-button>
                        </el-tooltip>
                    </el-button-group>
                </div>

                <el-form-item label="店铺区域">
                    <div class="custom-selection" id="customSelection" @click="showTreeBox('area')">
                        <div class="item" id="area">
                            <p v-show="selectedAreaList.length <= 0">请选择</p>
                            <span v-for="item in selectedAreaList" :id="item.id">
                                {{ item.text }}
                                <i class="el-icon-close"
                                   @click.stop="deleteOption('area', item.id)"
                                ></i>
                            </span>
                        </div>
                        <i :class="treeBoxStatus.area.customSelectionIcon"></i>
                    </div>
                    <div class="custom-tree-box" v-show="treeBoxStatus.area.show">
                        <el-input placeholder="输入关键字进行过滤" v-model="filterAreaText"></el-input>
                        <el-tree
                            :data="areaList"
                            :props="areaTreeDefaultProps"
                            show-checkbox
                            node-key="id"
                            ref="area"
                            @check-change="getCheckedNode('selectedAreaList', 'area')"
                            :filter-node-method="filterNode"
                        >
                        </el-tree>
                    </div>
                </el-form-item>

                <el-form-item label="商品品类">
                    <div class="custom-selection" id="customSelection" @click="showTreeBox('cat')">
                        <div class="item" id="cat">
                            <p v-show="selectedCatList.length <= 0">请选择</p>
                            <span v-for="item in selectedCatList" :id="item.id">
                                {{ item.text }}
                                <i class="el-icon-close"
                                   @click.stop="deleteOption('cat', item.id)"
                                ></i>
                            </span>
                        </div>
                        <i :class="treeBoxStatus.cat.customSelectionIcon"></i>
                    </div>
                    <div class="custom-tree-box" v-show="treeBoxStatus.cat.show">
                        <el-input placeholder="输入关键字进行过滤" v-model="filterCatText"></el-input>
                        <el-tree
                            :data="catList"
                            :props="catTreeDefaultProps"
                            show-checkbox
                            node-key="id"
                            ref="cat"
                            @check-change="getCheckedNode('selectedCatList', 'cat')"
                            :filter-node-method="filterNode"
                        >
                        </el-tree>
                    </div>
                </el-form-item>

                <el-form-item label="店铺类别" v-show="typeList.length > 1">
                    <el-select v-model="selectedType" placeholder="请选择">
                        <el-option v-for="option in typeList" :key="option.value"
                                   :label="option.text" :value="option.value"
                        ></el-option>
                    </el-select>
                </el-form-item>

                <el-form-item label="展示维度">
                    <el-select v-model="selectedDimension" placeholder="请选择">
                        <el-option v-for="option in dimensionList" :key="option.value"
                                   :label="option.text" :value="option.value"
                        ></el-option>
                    </el-select>
                </el-form-item>

                <el-form-item label="参考值">
                    <el-select v-model="selectedReference" placeholder="请选择">
                        <el-option v-for="option in referenceList" :key="option.value"
                                   :label="option.text" :value="option.value"
                        ></el-option>
                    </el-select>
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" :disabled="submitDisabled" @click="submit">
                        {{ submitDisabled ? 'loading' : '应用' }}
                    </el-button>
                </el-form-item>
            </el-form>
        </el-card>

        <div class="ui active centered inline large text loader" v-show="loading">加载中</div>
        <div class="ui fluid card" v-show="!loading && isNull">
            <div class="center aligned content">
                <i class="big meh icon"></i>
                <p>暂时还没有生成数据</p>
            </div>
        </div>

        <el-card class="box-card" v-show="!isNull && !loading">
            <div class="block map-chart" id="mapChart"></div>
            <el-row>
                <el-col class="dashbord-chart" :span="6" id="dashbordSalesChart"></el-col>
                <el-col class="dashbord-chart" :span="6" id="dashbordProfitChart"></el-col>
                <el-col class="dashbord-chart" :span="6" id="dashbordOrderChart"></el-col>
                <el-col class="dashbord-chart" :span="6" id="dashbordPriceChart"></el-col>
            </el-row>
        </el-card>
    </div>
</template>

<script>
    import 'echarts/extension/bmap/bmap'

    export default {
        data() {
            return {
                cs_id: this.$route.params.cs_id,
                s_id: this.$route.params.s_id,

                areaList: [
                    {
                        id: '0',
                        label: '全部',
                        children: [
                        ]
                    }
                ],
                areaTreeDefaultProps: {
                    children: 'children',
                    label: 'label'
                },
                selectedAreaList: [],

                catList: [
                    {
                        id: '0',
                        label: '全部',
                        children: [
                        ]
                    }
                ],
                catTreeDefaultProps: {
                    children: 'children',
                    label: 'label'
                },
                selectedCatList: [],

                treeBoxStatus: {
                    area: {
                        show: false,
                        customSelectionIcon: 'el-icon-caret-bottom',
                    },
                    cat: {
                        show: false,
                        customSelectionIcon: 'el-icon-caret-bottom',
                    }
                },
                filterAreaText: '',
                filterCatText: '',

                timeUnitList: [
                    // {
                    //     value: 'month',
                    //     text: '月'
                    // },
                    // {
                    //     value: 'week',
                    //     text: '周'
                    // },
                    {
                        value: 'day',
                        text: '日'
                    }
                ],
                selectedTimeUnit: 'day',
                startTime: new Date(),
                endTime: new Date(),
                // 日期间隔为从当前日期向前推 range 个月
                range: 3,
                sliderLength: 2,
                showStops: true,
                timeInterval: [0, 0],

                typeList: [],
                selectedType: null,

                dimensionList: [
                    {
                        value: 'sales',
                        text: '销售额'
                    },
                    {
                        value: 'profit',
                        text: '毛利额'
                    },
                    {
                        value: 'traffic',
                        text: '单次'
                    },
                    {
                        value: 'order',
                        text: '客单价'
                    },
                ],
                selectedDimension: 'sales',

                referenceList: [
                    {
                        value: '0',
                        text: '平均值'
                    },
                    {
                        value: '1',
                        text: '中位数'
                    },
                    {
                        value: '2',
                        text: 'top20'
                    },
                ],
                selectedReference: '0',

                mapChart: null,
                dashbordChart: {},

                loading: false,
                isNull: false,

                isDataGetOver: {
                    areaData: false,
                    catData: false,
                    storeType: false
                },
                submitDisabled: true
            }
        },

        watch: {
            filterAreaText: function(newVal) {
                this.$refs.area.filter(newVal)
            },

            filterCatText: function(newVal) {
                this.$refs.cat.filter(newVal)
            },

            selectedTimeUnit: function(newVal) {
                if(newVal === 'week') {
                    this.calcSliderLengthByWeek()
                } else if(newVal === 'day') {
                    this.calcSliderLengthByDay()
                } else {
                    this.calcSliderLengthByMonth()
                }
            },

            isDataGetOver: function(newValue) {
                var self = this,
                    flag = true

                for(let name in newValue) {
                    if(newValue[name] === false) {
                        flag = false
                    }
                }

                if(flag) {
                    this.submitDisabled = false
                    this.$nextTick(function (){
                        self.submit()
                    })
                }
            }
        },

        computed: {
            formatStartTime: function() {
                return this.formatDate(this.startTime)
            },

            formatEndTime: function() {
                return this.formatDate(this.endTime)
            }
        },

        mounted() {
            this.initTime()
            this.calcSliderLengthByDay()

            this.renderSelection()
        },

        methods: {
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

            initTime: function() {
                var start = new Date()

                start.setMonth(start.getMonth() - this.range)
                start.setDate(1)

                this.startTime = start
            },

            calcSliderLengthByMonth: function() {
                this.sliderLength = this.range

                this.showStops = true
            },

            calcSliderLengthByWeek: function() {
                this.sliderLength = Math.floor(((this.endTime.getTime() - this.startTime.getTime())
                    / (1000 * 60 * 60 * 24 * 7)))

                this.showStops = true
            },

            calcSliderLengthByDay: function() {
                this.sliderLength = Math.floor(((this.endTime.getTime() - this.startTime.getTime())
                    / (1000 * 60 * 60 * 24))) + 1

                // 以 日 分断点太多不展示
                this.showStops = false

                // 初始化 显示天数
                this.initTimeInterval()
            },

            initTimeInterval: function() {
                // 显示最近一天
                this.timeInterval = [this.sliderLength - 1, this.sliderLength]
            },

            getTimeValue: function(value) {
                var date = new Date(this.startTime.getTime())

                if(this.selectedTimeUnit === 'month') {
                    date.setMonth(date.getMonth() + value)

                    return this.formatDate(date)
                }

                if(this.selectedTimeUnit === 'week') {
                    if(value === this.sliderLength) {
                        // 最后一段可能不足一整周，固定为endTime
                        return this.formatDate(this.endTime)
                    } else {
                        date.setDate(date.getDate() + (value * 7))

                        return this.formatDate(date)
                    }
                }

                if(this.selectedTimeUnit === 'day') {
                    date.setDate(date.getDate() + value)

                    return this.formatDate(date)
                }
            },

            timeTooltipFormat: function(value) {
                return this.getTimeValue(value)
            },

            moveSlider: function(direction) {
                var n = this.timeInterval[1] - this.timeInterval[0]

                this.timeInterval =
                    direction === 'left'
                        ? this.timeInterval[0] - n < 0
                            ? [0, n]
                            : this.timeInterval.map((num) => { return num - n })
                        : this.timeInterval[1] + n > this.sliderLength
                            ? [this.sliderLength - n, this.sliderLength]
                            : this.timeInterval.map((num) => { return num + n })
            },

            showTreeBox: function(key) {
                this.treeBoxStatus[key].show = !this.treeBoxStatus[key].show

                this.treeBoxStatus[key].customSelectionIcon = this.treeBoxStatus[key].show
                    ? 'el-icon-caret-top'
                    : 'el-icon-caret-bottom'
            },

            getCheckedNode: function(list, ref) {
                var self = this,
                    selectedNodes = this.$refs[ref].getCheckedNodes()

                //如果只要叶子节点
                // if(ref === 'area') {
                //     selectedNodes = this.$refs[ref].getCheckedNodes(true)
                // }

                this[list] = []

                selectedNodes.reverse().forEach(function(item) {
                    self[list].push({
                        id: item.id,
                        text: item.label
                    })

                    // only parent node
                    // if(ref !== 'area') {
                    if(item.children) {
                        item.children.forEach(function(node) {
                            var index = self[list].findIndex((option) => {
                                return option.id === node.id
                            })

                            self[list].splice(index, 1)
                        })
                    }
                    // }
                })
            },

            filterNode: function(value, data) {
                if (!value){
                    return true
                }

                return data.label.indexOf(value) !== -1
            },

            deleteOption: function(ref, id) {
                this.$refs[ref].setChecked(id, false, true)
            },

            renderSelection: function() {
                this.getCatList()
                this.getAreaList()
                this.getTypeList()
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

            getCatList: function() {
                var self = this

                $.get(
                    '/api/overview/v0/category',
                    function(res) {
                        if(res.code === 0) {
                            var obj = Object.keys(res.data)

                            self.recurTree(obj, res.data)

                            self.catList[0].children = obj

                            self.$nextTick(function(){
                                self.$refs.cat.setChecked(self.catList[0].id, true, true)

                                self.isDataGetOver = Object.assign({}, self.isDataGetOver, {
                                    catData: true
                                })
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

            getAreaList: function() {
                var self = this

                $.get(
                    '/api/overview/v0/area',
                    function(res) {
                        if(res.code === 0) {
                            // var obj = Object.keys(res.data)

                            // self.recurTree(obj, res.data)

                            // self.areaList[0].children = obj

                            self.areaList[0].children = res.data

                            self.$nextTick(function(){
                                self.$refs.area.setChecked(self.areaList[0].id, true, true)

                                self.isDataGetOver = Object.assign({}, self.isDataGetOver, {
                                    areaData: true
                                })
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

            getTypeList: function() {
                var self = this

                $.get(
                    '/api/manage/v0/store-type',
                    function(res) {
                        if(res.code === 0) {
                            self.typeList = res.data.map((item) => {
                                return {
                                    value: item.id,
                                    text: item.type_name
                                }
                            })

                            self.selectedType = self.typeList[0].value

                            self.isDataGetOver = Object.assign({}, self.isDataGetOver, {
                                storeType: true
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
                    areaList = this.selectedAreaList.map((item) => { return item.id }),
                    catList = this.selectedCatList.map((item) => { return item.id }),
                    data = {
                        start_date: this.getTimeValue(this.timeInterval[0]),
                        end_date: this.getTimeValue(this.timeInterval[1]),
                        area_id: null,
                        cat_id: null,
                        store_type: this.selectedType,
                        latitude: this.selectedDimension,
                        reference: this.selectedReference
                    }

                data.area_id = areaList.length <= 0 ? JSON.stringify(['0']) : JSON.stringify(areaList)
                data.cat_id = catList.length <= 0 ? JSON.stringify(['0']) : JSON.stringify(catList)

                this.loading = true

                console.log(data, areaList, catList)

                $.ajax({
                    url: '/api/overview/v0/list',
                    type: 'GET',
                    data: data,
                    success: function(res) {
                        if(res.code === 0) {
                            console.log(res)
                            self.loading = false
                            // self.isNull = true

                            self.$nextTick(function (){
                                var reference = self.referenceList.find((item) => {
                                    return item.value === self.selectedReference
                                })

                                var dimension = self.dimensionList.find((item) => {
                                    return item.value === self.selectedDimension
                                })

                                self.loadMapChart(reference.text, dimension, res.data)
                            })
                        } else {
                            self.$message({
                                message: res.error_msg,
                                type: 'error'
                            })
                        }
                    },

                    error: function() {
                        self.$message({
                            message: '失败',
                            type: 'error'
                        })
                    }
                })

                $.ajax({
                    url: '/api/overview/v0/list/bottom',
                    type: 'GET',
                    data: data,
                    success: function(res) {
                        if(res.code === 0) {
                            self.loading = false
                            // self.isNull = true

                            // 后端数据：traffic：单次，order：客单价
                            self.$nextTick(function (){
                                self.loadDashboardChart({
                                    id: 'dashbordSalesChart',
                                    value: res.data.sales.value,
                                    max: res.data.sales.max * 1.25,
                                    name: '销售额'
                                })
                                self.loadDashboardChart({
                                    id: 'dashbordProfitChart',
                                    value: res.data.profit.value,
                                    max: res.data.profit.max * 1.25,
                                    name: '毛利额'
                                })
                                self.loadDashboardChart({
                                    id: 'dashbordOrderChart',
                                    value: res.data.traffic.value,
                                    max: res.data.traffic.max * 1.25,
                                    name: '单次'
                                })
                                self.loadDashboardChart({
                                    id: 'dashbordPriceChart',
                                    value: res.data.order.value,
                                    max: res.data.order.max * 1.25,
                                    name: '客单价'
                                })
                            })
                        } else {
                            self.$message({
                                message: res.error_msg,
                                type: 'error'
                            })
                        }
                    },

                    error: function() {
                        self.$message({
                            message: '失败',
                            type: 'error'
                        })
                    }
                })
            },

            loadMapChart: function(referenceText, dimension, data) {
                var topData = data.top_data.map((item) => {
                        return {
                            name: item.name,
                            value: [item.lng, item.lat, item.value]
                        }
                    }),
                    otherData = data.other_data.map((item) => {
                        return {
                            name: item.name,
                            value: [item.lng, item.lat, item.value]
                        }
                    }),
                    reference = data.reference,

                    colorList = {
                        sales: 'purple',
                        profit: 'darkslategray',
                        traffic: 'darkred',
                        order: 'darkblue'
                    }

                if(!this.mapChart) {
                    this.mapChart = echarts.init($('#mapChart')[0])
                }

                this.mapChart.setOption({
                    tooltip: {
                        trigger: 'item',
                        formatter: function(params) {
                            return params.seriesName +
                                '</br>' + params.name +
                                ',</br>2017.7.1' +
                                ',</br>' + dimension.text + ': ' + params.value[2] +
                                ',</br>参考值(' + referenceText + '): ' + reference
                        }
                    },
                    bmap: {
                        center: [104.114129, 37.550339],
                        zoom: 5,
                        roam: true,
                        mapStyle: {
                            styleJson: [
                                {
                                    'featureType': 'water',
                                    'elementType': 'all',
                                    'stylers': {
                                        'color': '#d1d1d1'
                                    }
                                },
                                {
                                    'featureType': 'land',
                                    'elementType': 'all',
                                    'stylers': {
                                        'color': '#f3f3f3'
                                    }
                                },
                                {
                                    'featureType': 'railway',
                                    'elementType': 'all',
                                    'stylers': {
                                        'visibility': 'off'
                                    }
                                },
                                {
                                    'featureType': 'highway',
                                    'elementType': 'all',
                                    'stylers': {
                                        'color': '#fdfdfd'
                                    }
                                },
                                {
                                    'featureType': 'highway',
                                    'elementType': 'labels',
                                    'stylers': {
                                        'visibility': 'off'
                                    }
                                },
                                {
                                    'featureType': 'arterial',
                                    'elementType': 'geometry',
                                    'stylers': {
                                        'color': '#fefefe'
                                    }
                                },
                                {
                                    'featureType': 'arterial',
                                    'elementType': 'geometry.fill',
                                    'stylers': {
                                        'color': '#fefefe'
                                    }
                                },
                                {
                                    'featureType': 'poi',
                                    'elementType': 'all',
                                    'stylers': {
                                        'visibility': 'off'
                                    }
                                },
                                {
                                    'featureType': 'green',
                                    'elementType': 'all',
                                    'stylers': {
                                        'visibility': 'off'
                                    }
                                },
                                {
                                    'featureType': 'subway',
                                    'elementType': 'all',
                                    'stylers': {
                                        'visibility': 'off'
                                    }
                                },
                                {
                                    'featureType': 'manmade',
                                    'elementType': 'all',
                                    'stylers': {
                                        'color': '#d1d1d1'
                                    }
                                },
                                {
                                    'featureType': 'local',
                                    'elementType': 'all',
                                    'stylers': {
                                        'color': '#d1d1d1'
                                    }
                                },
                                {
                                    'featureType': 'arterial',
                                    'elementType': 'labels',
                                    'stylers': {
                                        'visibility': 'off'
                                    }
                                },
                                {
                                    'featureType': 'boundary',
                                    'elementType': 'all',
                                    'stylers': {
                                        'color': '#fefefe'
                                    }
                                },
                                {
                                    'featureType': 'building',
                                    'elementType': 'all',
                                    'stylers': {
                                        'color': '#d1d1d1'
                                    }
                                },
                                {
                                    'featureType': 'label',
                                    'elementType': 'labels.text.fill',
                                    'stylers': {
                                        'color': '#999999'
                                    }
                                }
                            ]
                        }
                    },
                    series: [
                        {
                            name: ' ',
                            type: 'scatter',
                            coordinateSystem: 'bmap',
                            data: otherData,
                            symbol: 'triangle',
                            symbolSize: 20,
                            label: {
                                normal: {
                                    formatter: '{b}',
                                    position: 'right',
                                    show: false
                                },
                                emphasis: {
                                    show: true
                                }
                            },
                            itemStyle: {
                                normal: {
                                    color: colorList[dimension.value]
                                }
                            }
                        },
                        {
                            name: ' ',
                            type: 'scatter',
                            coordinateSystem: 'bmap',
                            data: topData.slice(5),
                            symbolSize: 20,
                            label: {
                                normal: {
                                    formatter: '{b}',
                                    position: 'right',
                                    show: false
                                },
                                emphasis: {
                                    show: true
                                }
                            },
                            itemStyle: {
                                normal: {
                                    color: colorList[dimension.value]
                                }
                            }
                        },
                        {
                            name: 'Top5',
                            type: 'effectScatter',
                            coordinateSystem: 'bmap',
                            data: topData.slice(0, 5),
                            symbolSize: 20,
                            showEffectOn: 'render',
                            rippleEffect: {
                                brushType: 'stroke'
                            },
                            hoverAnimation: true,
                            label: {
                                normal: {
                                    formatter: '{b}',
                                    position: 'right',
                                    show: true
                                }
                            },
                            itemStyle: {
                                normal: {
                                    color: colorList[dimension.value],
                                    shadowBlur: 10,
                                    shadowColor: '#333'
                                }
                            },
                            zlevel: 1
                        }
                    ]
                })
            },

            // 1. 7.5 取到 8
            // 2. 23 取到 30
            // 3. 232 取到 240; 2345 取到 2400; 23455 取到 24000
            integer: function(num) {
                var n = Math.floor(num)

                if(n < 0) {
                    return 0
                } else if(n < 10) {
                    return Math.ceil(n)
                } else if(n < 100) {
                    return n % 10 === 0 ? n : (n - (n % 10)) + 1 * 10
                } else {
                    var len = n.toString().length

                    return n % Math.pow(10, len - 2 ) === 0
                        ? n
                        : n - (n % Math.pow(10, len - 2 )) + Math.pow(10, len - 2 )
                }
            },

            loadDashboardChart: function(data) {
                var self = this

                if(!this.dashbordChart[data.id]) {
                    this.dashbordChart[data.id] = echarts.init($('#' + data.id)[0])
                }

                this.dashbordChart[data.id].setOption({
                    series: [
                        {
                            name: data.name,
                            type: 'gauge',
                            radius: '100%',
                            startAngle: 180,
                            endAngle: 0,
                            min: 0,
                            max: self.integer(data.max),
                            axisLine: {
                                lineStyle: {
                                    width: 10,
                                }
                            },
                            splitLine: {
                                show: false,
                                length: 10
                            },
                            axisTick: {
                                show: true,
                                lineStyle: {
                                    color: 'rgba(255, 255, 255, .5)'
                                }
                            },
                            axisLabel: {
                                formatter: function (value) {
                                    return (0 >= value || value >= self.integer(data.max)) ? value : ''
                                }
                            },
                            detail: {
                                offsetCenter: [0, '-40%'],
                                color: '#333',
                                fontSize: 20
                            },
                            title: {
                                offsetCenter: [0, 30],
                                fontWeight: 'bold'
                            },
                            data: [{value: self.integer(data.value), name: data.name}]
                        }
                    ]
                })
            },
        }
    }
</script>

<style scoped>
    @media (max-width: 1250px) and (min-width: 800px) {
        .time-slider {
            width: 100%;
        }
    }

    @media (min-width: 1250px) {
        .time-slider {
            width: 90%;
        }
    }

    .box-card {
        margin-bottom: 15px;
    }

    .custom-selection {
        box-sizing: border-box;
        min-width: 300px;
        padding-right: 2px;

        line-height: 0;

        cursor: pointer;

        border: 1px solid #bfcbd9;
        border-radius: 4px;
    }

    .custom-selection > .item {
        width: 93%;
        min-height: 32px;
        padding-right: 2px;

        display: inline-block;
    }

    .custom-selection > .item > p {
        padding-top: 3px;
        padding-left: 7px;

        font-size: 1em;
        line-height: 2em;

        color: #bfcbd9;
    }

    .custom-selection > .item > span {
        margin: 4px 2px;
        padding: 2px 4px;

        display: inline-block;

        line-height: 20px;

        color: #20a0ff;
        border: 1px solid rgba(32,160,255,.2);
        border-radius: 4px;
        background-color: rgba(32,160,255,.1);
    }

    .custom-selection > .item .el-icon-close {
        font-size: 13px;

        cursor: pointer;
        transform: scale(.75);
    }

    .custom-selection > .item .el-icon-close:hover {
        color: #fff;
        border-radius: 4px;
        background-color: #20a0ff;
    }

    .custom-selection > i {
        width: 10%;

        position: absolute;

        font-size: 12px;
        line-height: 3em;

        color: #bfcbd9;
    }

    .custom-tree-box {
        margin-top: 4px;

        box-shadow: 0 2px 4px rgba(0,0,0,.12), 0 0 6px rgba(0,0,0,.04);
    }

    .custom-tree-box > .el-tree {
        padding-right: 4px;
    }

    .time-slider {
        display: inline-block;
    }

    .time-slider .el-slider {
        width: 62%;

        display: inline-block;
    }

    .time-slider .slider-toolbar {
        margin-bottom: 20px;
        margin-left: 10px;
    }

    .map-chart {
        width: 100%;
        height: 800px;
        margin-bottom: 50px;
    }

    .dashbord-chart {
        height: 200px;
    }
</style>

<style>
    .el-slider__button-wrapper {
        z-index: 98;
    }
</style>
