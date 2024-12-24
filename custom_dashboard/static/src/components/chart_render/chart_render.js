/** @odoo-module */

import { registry } from "@web/core/registry"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks";

const { Component, onWillStart, useRef, onMounted, useState } = owl

export class ChartRender extends Component {

    setup() {
        this.state = useState({type: this.props.type, config: this.props.config, title: this.props.title})

        this.chartRef = useRef("chart") 
        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"),
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-datalabels/2.2.0/chartjs-plugin-datalabels.min.js")
        })

        onMounted(()=>this.renderChart())
    }

    renderChart(){
        new Chart(this.chartRef.el,
            {
                type: this.state.type,
                data: this.state.config.data,
                options:{
                    responsive: true,
                    plugins: {
                        datalabels: {
                            color: 'black',
                            anchor: 'center', // Position of label relative to the bar
                            align: 'center',  // Alignment of label
                            formatter: (value) => value, // Format value displayed
                            font: {
                                weight: 'bold'
                            }
                        },
                        title:{
                            display: true,
                            text: this.state.title,
                        },
                        legend: {
                            position: 'right',
                            display: true,
                            labels:this.state.config.labels,
                            
                            onClick: function(mouseEvent, legendItem, legend) {
                                // toggle the visibility of the dataset from what it currently is
                                legend.chart.getDatasetMeta(
                                    legendItem.datasetIndex
                                ).hidden = legend.chart.isDatasetVisible(legendItem.datasetIndex);
                                legend.chart.update();
                            }
                        },
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                const labelIndex = (context[0].datasetIndex * 2) + context[0].dataIndex;
                                return context[0].chart.data.labels[labelIndex] + ': ' + context[0].formattedValue;
                                }
                            }
                        }
                    },                    
                },
                plugins: [ChartDataLabels]
            }
        );
    }
}

ChartRender.template = "custom_dashboard.ChartRender";