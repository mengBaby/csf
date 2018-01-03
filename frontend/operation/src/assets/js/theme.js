(function (echarts) {
    var log = function (msg) {
        if (typeof console !== 'undefined') {
            console && console.error && console.error(msg);
        }
    };
    if (!echarts) {
        log('ECharts is not Loaded');
        return;
    }

    var cmTheme = {
        "seriesCnt": "5",
        "backgroundColor": "rgba(0, 0, 0, 0)",
        "titleColor": "#333",
        "subtitleColor": "#aaa",
        "textColorShow": false,
        "textColor": "#333",
        "markTextColor": "#eee",
        "color": [
            "#3789ff",
            "#ff415b",
            "#ffbe00",
            "#0dddff",
            "#6fa9fb",
            "#fe8c9c",
            "#fad876"
        ],
        "borderColor": "#ccc",
        "borderWidth": 0,
        "visualMapColor": [
            "#ff415b",
            "#fe8c9c",
            "#6fa9fb"
        ],
        "legendTextColor": "#333",
        "kColor": "#3789ff",
        "kColor0": "#ff415b",
        "kBorderColor": "#0dddff",
        "kBorderColor0": "#fe8c9c",
        "kBorderWidth": "1",
        "lineWidth": "2",
        "symbolSize": "3",
        "symbol": "circle",
        "symbolBorderWidth": "1",
        "lineSmooth": false,
        "graphLineWidth": 1,
        "graphLineColor": "#aaaaaa",
        "mapLabelColor": "#000",
        "mapLabelColorE": "rgb(100,0,0)",
        "mapBorderColor": "#ffffff",
        "mapBorderColorE": "#444",
        "mapBorderWidth": "0.5",
        "mapBorderWidthE": "0",
        "mapAreaColor": "#eee",
        "mapAreaColorE": "#fad876",
        "axes": [
            {
                "type": "all",
                "name": "通用坐标轴",
                "axisLineShow": true,
                "axisLineColor": "#333",
                "axisTickShow": true,
                "axisTickColor": "#333",
                "axisLabelShow": true,
                "axisLabelColor": "#333",
                "splitLineShow": true,
                "splitLineColor": [
                    "#ccc"
                ],
                "splitAreaShow": false,
                "splitAreaColor": [
                    "rgba(250,250,250,0.3)",
                    "rgba(200,200,200,0.3)"
                ]
            },
            {
                "type": "category",
                "name": "类目坐标轴",
                "axisLineShow": true,
                "axisLineColor": "#dbdbdb",
                "axisTickShow": true,
                "axisTickColor": "#dbdbdb",
                "axisLabelShow": true,
                "axisLabelColor": "#333",
                "splitLineShow": false,
                "splitLineColor": [
                    "#ccc"
                ],
                "splitAreaShow": false,
                "splitAreaColor": [
                    "rgba(250,250,250,0.3)",
                    "rgba(200,200,200,0.3)"
                ]
            },
            {
                "type": "value",
                "name": "数值坐标轴",
                "axisLineShow": true,
                "axisLineColor": "#dbdbdb",
                "axisTickShow": true,
                "axisTickColor": "#dbdbdb",
                "axisLabelShow": true,
                "axisLabelColor": "#333333",
                "splitLineShow": true,
                "splitLineColor": [
                    "#dbdbdb"
                ],
                "splitAreaShow": false,
                "splitAreaColor": [
                    "rgba(250,250,250,0.3)",
                    "rgba(200,200,200,0.3)"
                ]
            },
            {
                "type": "log",
                "name": "对数坐标轴",
                "axisLineShow": true,
                "axisLineColor": "#333",
                "axisTickShow": true,
                "axisTickColor": "#333",
                "axisLabelShow": true,
                "axisLabelColor": "#333",
                "splitLineShow": true,
                "splitLineColor": [
                    "#ccc"
                ],
                "splitAreaShow": false,
                "splitAreaColor": [
                    "rgba(250,250,250,0.3)",
                    "rgba(200,200,200,0.3)"
                ]
            },
            {
                "type": "time",
                "name": "时间坐标轴",
                "axisLineShow": true,
                "axisLineColor": "#333",
                "axisTickShow": true,
                "axisTickColor": "#333",
                "axisLabelShow": true,
                "axisLabelColor": "#333",
                "splitLineShow": true,
                "splitLineColor": [
                    "#ccc"
                ],
                "splitAreaShow": false,
                "splitAreaColor": [
                    "rgba(250,250,250,0.3)",
                    "rgba(200,200,200,0.3)"
                ]
            }
        ],
        "axisSeperateSetting": true,
        "toolboxColor": "#999",
        "toolboxEmpasisColor": "#666",
        "tooltipAxisColor": "#ccc",
        "tooltipAxisWidth": 1,
        "timelineLineColor": "#293c55",
        "timelineLineWidth": 1,
        "timelineItemColor": "#293c55",
        "timelineItemColorE": "#a9334c",
        "timelineCheckColor": "#e43c59",
        "timelineCheckBorderColor": "rgba(194,53,49, 0.5)",
        "timelineItemBorderWidth": 1,
        "timelineControlColor": "#293c55",
        "timelineControlBorderColor": "#293c55",
        "timelineControlBorderWidth": 0.5,
        "timelineLabelColor": "#293c55",
        "datazoomBackgroundColor": "rgba(47,69,84,0)",
        "datazoomDataColor": "rgba(47,69,84,0.3)",
        "datazoomFillColor": "rgba(167,183,204,0.4)",
        "datazoomHandleColor": "#a7b7cc",
        "datazoomHandleWidth": "100",
        "datazoomLabelColor": "#333"
    };

    echarts.registerTheme('cmTheme', cmTheme);
})(echarts);
