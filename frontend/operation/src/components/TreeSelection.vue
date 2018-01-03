<template>
    <el-form-item :label="label" class="selectuon-form-box">
        <div class="custom-selection" @click="showTreeBox()">
            <div class="item">
                <p v-show="selectedList.length <= 0">请选择</p>
                <span v-for="item in selectedList" :id="item.id">
                    {{ item.label }}
                    <i class="el-icon-close"
                       @click.stop="deleteOption(treeRef, item.id)"
                    ></i>
                </span>
            </div>
            <i :class="treeBoxStatus.customSelectionIcon"></i>
        </div>
        <div class="custom-tree-box" v-show="treeBoxStatus.show">
            <el-input placeholder="输入关键字进行过滤" v-model="filterText"></el-input>
            <el-tree
                :data="treeList"
                :default-expanded-keys="defaultExpanded"
                :props="treeDefaultProps"
                show-checkbox
                node-key="id"
                :ref="treeRef"
                @check-change="getCheckedNode(treeRef)"
                :filter-node-method="filterNode"
            >
            </el-tree>
        </div>
    </el-form-item>
</template>

<script>
export default {
    name: 'treeSelection',
    props: {
        treeList: {
            required: true
        },
        treeDefaultProps: {
            type: Object,
            default: function() {
                return {
                    children: 'children',
                    label: 'label',
                    disable: 'disable'
                }
            }
        },
        treeRef: {
            type: String,
            required: true
        },
        label: {
            type: String,
            required: true
        },
        defaultSelected: {
            type: String
        },
        defaultExpanded: {
            type: Array
        }
    },

    data() {
        return {
            treeBoxStatus: {
                show: false,
                customSelectionIcon: 'el-icon-caret-bottom',
            },

            selectedList: [],
            filterText: '',
        }
    },

    watch: {
        filterText: function(newVal) {
            this.$refs[this.treeRef].filter(newVal)
        },

        treeList: function(newValue) {
            var self = this

            this.$nextTick(function(){
                if(self.defaultSelected) {
                    self.$refs[self.treeRef].setChecked(
                        self.defaultSelected, true, true
                    )
                }
            })
        }
    },

    mounted() {
        var self = this

        // 点击确定 下拉合起
        $('.sales-submit-btn').on('click', function(e) {
            self.treeBoxStatus.show = false
        })
    },

    methods: {
        showTreeBox: function() {
            this.treeBoxStatus.show = !this.treeBoxStatus.show

            this.treeBoxStatus.customSelectionIcon = this.treeBoxStatus.show
                ? 'el-icon-caret-top'
                : 'el-icon-caret-bottom'
        },

        deleteOption: function(ref, id) {
            this.$refs[ref].setChecked(id, false, true)
        },

        getCheckedNode: function(ref) {
            var self = this,
                selectedNodes = this.$refs[ref].getCheckedNodes()

            //如果只要叶子节点
            // if(just leaf) {
            //     selectedNodes = this.$refs[ref].getCheckedNodes(true)
            // }

            this.selectedList = []

            selectedNodes.reverse().forEach(function(item) {
                self.selectedList.push({
                    id: item.id,
                    label: item.label
                })

                // only parent node 判断当前item的子级是在selected中，在，则删
                // if(just leaf) {
                if(item.children) {
                    item.children.forEach(function(node) {
                        var index = self.selectedList.findIndex((option) => {
                            return option.id === node.id
                        })

                        self.selectedList.splice(index, 1)
                    })
                }
                // }
            })

            // 当前选中节点的obj 仅限单选
            var selectedObj = selectedNodes.filter((item) => {
                return item.id === self.selectedList[0].id
            })

            this.$emit('get-selected-list', self.selectedList)
            this.$emit('get-selected-option', selectedObj[0])
        },

        filterNode: function(value, data) {
            if (!value){
                return true
            }

            return data.label.indexOf(value) !== -1
        },
    }
}
</script>

<style scoped>
    .custom-selection {
        min-width: 300px;
        padding-right: 2px;

        line-height: 0;

        border: 1px solid #bfcbd9;
        border-radius: 4px;

        box-sizing: border-box;
        cursor: pointer;
    }

    .custom-selection > .item {
        width: 93%;

        display: inline-block;
        padding-right: 2px;

        min-height: 32px;
    }

    .custom-selection > .item > p {
        padding-left: 7px;
        padding-top: 3px;

        font-size: 1em;
        color: #bfcbd9;
        line-height: 2em;
    }

    .custom-selection > .item > span {
        display: inline-block;

        padding: 2px 4px;
        margin: 4px 2px;

        color: #20a0ff;
        line-height: 20px;

        border-radius: 4px;
        border: 1px solid rgba(32,160,255,.2);
        background-color: rgba(32,160,255,.1);
    }

    .custom-selection > .item .el-icon-close {
        font-size: 13px;
        transform: scale(.75);

        cursor: pointer;
    }

    .custom-selection > .item .el-icon-close:hover {
        background-color: #20a0ff;
        color: #fff;

        border-radius: 4px;
    }

    .custom-selection > i {
        width: 10%;
        position: absolute;

        color: #bfcbd9;

        font-size: 12px;
        line-height: 3em;
    }

    .custom-tree-box {
        margin-top: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,.12), 0 0 6px rgba(0,0,0,.04);
    }

    .custom-tree-box > .el-tree{
        max-height: 200px;
        padding-right: 4px;

        overflow-y: scroll;
    }

    .selectuon-form-box {
        max-width: 90%;
    }
</style>

<style>
    .selectuon-form-box .el-form-item__content {
        max-width: 90%;
    }
</style>
