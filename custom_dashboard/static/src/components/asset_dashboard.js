/** @odoo-module */

import { registry } from "@web/core/registry"
import { KpiCard } from "./kpi_card/kpi_card"
import { ChartRender } from "./chart_render/chart_render"
import { loadJS } from "@web/core/assets"
import { useService } from "@web/core/utils/hooks";

const { Component, onWillStart, useRef, onMounted, useState } = owl

export class AssetDashboard extends Component{
    setup(){
        this.state = useState({
            fieldValue:"name_id",
            graphType:"pie",
            refresh_key: 0,
            total_assets:20,
            manager_count:5,
            department_count:3,
        })
        this.orm = useService("orm")
        this.actionService = useService("action")
        this.viewService = useService("view")

        onWillStart(async()=>{
            
            await this.getManagetCount()
            await this.getStatusValues()
            await this.getNameValues()
            await this.getDeptValues()
            await this.getselectedFieldValues()
        }),
        onMounted(async()=>{await this.showAssetList()})

    }
    
    async showAssetList() {
        const container = document.querySelector(".asset_list_container");

        if (container) {
            try {
                console.log("Attempting to load asset tree view...");

                // Use envService to access ref
                // const viewId = this.env.ref("asset_management.view_asset_tree"); // Correctly accessing view ID

                // Pass the specific view ID to load the tree view
                await this.viewService.mount(container, {
                    type: "ir.actions.act_window",
                    name: "Asset Management",
                    res_model: "asset.management.asset",
                    views: [["asset_management.view_asset_tree"]], // Use your view ID here
                    target: "inline",  // Ensures the view is embedded in the container
                });
            } catch (error) {
                console.error("Error loading view:", error);
            }
        } else {
            console.log("Container not found");
        }
    }
    
    
    
    async getManagetCount(){
        const data = await this.orm.readGroup("asset.management.asset",[],['manager'],['manager'])
        // console.log("manager data",data)
        this.state.manager_count = data.length 
    }
    // Asset v/s Status
    async getStatusValues(){
        const data = await this.orm.readGroup("asset.management.asset",[],['status'],['status'])
        // console.log(data)

        this.state.statusValues = {
            data: {
                labels: data.map(row => row.status) ,
                datasets: [{
                label: 'Number of Assets',
                data: data.map(row => row.status_count),
                hoverOffset: 10 
                }]
            },
            labels: {
                color:'black',
                font: {
                    weight: 'bold'
                },
                generateLabels: (chart) => {
                  const datasets = chart.data.datasets;
                  return datasets[0].data.map((data, i) => ({
                    text: `${chart.data.labels[i]} (${data})`,
                    fillStyle: datasets[0].backgroundColor[i],
                    index: i
                  }))
                }
            }
        }
    }

    // Asset v/s Name
    async getNameValues() {
        const name = await this.orm.searchRead("asset.management.asset", [], ["name_id", "status", "manager", "department_id"]);
        // console.log("name",name);
        this.state.total_assets = name.length
    
        // Count of Assets by Status (Inner Circle)
        const statusCount = {};
        name.forEach((item) => {
            statusCount[item.status] = (statusCount[item.status] || 0) + 1;
        });
        // console.log("statusCount", statusCount);
        const sortedstatusCount = Object.keys(statusCount)
        .sort() // Sort the keys alphabetically
        .reduce((acc, key) => {
            acc[key] = statusCount[key]; // Add the key-value pairs to the new object
            return acc;
        }, {});

        // console.log("sortedstatusCount",sortedstatusCount);
    
        // Count of Assets by Status + Asset Name (Outer Circle)
        const nameData = {};
        name.forEach((item) => {
            const key = `${item.status}-${item.name_id[1]}`; // Combine Status and Name_ID
            nameData[key] = (nameData[key] || 0) + 1;
        });
        // console.log("nameData ------", nameData);
        // Sort the object by keys
        const sortedNameData = Object.keys(nameData)
        .sort() // Sort the keys alphabetically
        .reduce((acc, key) => {
            acc[key] = nameData[key]; // Add the key-value pairs to the new object
            return acc;
        }, {});

        // console.log("sortedNameData",sortedNameData);

    
        // Create Combined Labels Array
        const combinedLabels = [
            ...Object.entries(sortedNameData).map(([key, value]) => `${key} (${value})`),    // Labels for outer circle (status + asset name)
            ...Object.entries(sortedstatusCount).map(([key, value]) => `${key} (${value})`), // Labels for inner circle (statuses)
        ];
        // console.log("combinedLabels", combinedLabels);

        const length = Object.keys(sortedstatusCount).length;
        // console.log("length",length); // Logs the number of keys in the statusCount object
    
        // Set Data for Chart.js
        this.state.nameValues = {
            data: {
                datasets: [
                    // Inner Circle - Number of Assets by Status
                    {
                        label: 'Number of Assets by Status',
                        data: Object.values(sortedNameData), // Status Counts
                        hoverOffset: 10,
                        // labels: statusLabels,  // Set labels for the first dataset
                    },
                    // Outer Circle - Number of Assets by Name_ID under each Status
                    {
                        label: 'Number of Assets by Name_ID',
                        data: Object.values(sortedstatusCount), // Name_ID Counts

                        hoverOffset: 10,
                        // labels: nameLabels,  // Set labels for the second dataset
                    },
                ],
                labels:combinedLabels,
            },
            labels:{
                color:'black',
                font: {
                    weight: 'bold'
                },
                generateLabels: function(chart) {
                    // Get the default label list
                    const original = Chart.overrides.pie.plugins.legend.labels.generateLabels;
                    const labelsOriginal = original.call(this, chart);
        
                    // Build an array of colors used in the datasets of the chart
                    let datasetColors = chart.data.datasets.map(function(e) {
                        return e.backgroundColor;
                    });
                    datasetColors = datasetColors.flat();
        
                    // Modify the color and hide state of each label
                    labelsOriginal.forEach(label => {
                        // There are n labels for the first dataset, and the rest belong to the second dataset.
                        // 'n' is the number of labels for the first dataset.
                        if (label.index < this.length ) {
                            label.datasetIndex = 0; // First 'n' labels correspond to the first dataset
                        } else {
                            label.datasetIndex = 1; // Remaining labels correspond to the second dataset
                            }
            
                        // The hidden state must match the dataset's hidden state
                        label.hidden = !chart.isDatasetVisible(label.datasetIndex);
            
                        // Change the color to match the dataset
                        label.fillStyle = datasetColors[label.index];
                    });
        
                    return labelsOriginal;
                }
            }
        };
    }

    // Asset v/s Departments
    async getDeptValues(){
        const data = await this.orm.readGroup("asset.management.asset",[],['department_id'],['department_id'])
        // console.log(data)
        this.state.department_count = data.length 
        // console.log("dept numbers",data.length)

        this.state.deptValues = {
            data: {
                labels: data.map(row => row.department_id[1]) ,
                datasets: [{
                label: 'Number of Assets',
                data: data.map(row => row.department_id_count),
                hoverOffset: 10 
                }]
            },
            labels: {
                color:'black',
                font: {
                    weight: 'bold'
                },
                generateLabels: (chart) => {
                  const datasets = chart.data.datasets;
                  return datasets[0].data.map((data, i) => ({
                    text: `${chart.data.labels[i]} (${data})`,
                    fillStyle: datasets[0].backgroundColor[i],
                    index: i
                  }))
                }
            }
        }
    }

    async onChangeValue(){
        // console.log(this.state.fieldValue)
        await this.getselectedFieldValues();
        this.state.refresh_key++;
    }

    async getselectedFieldValues(){
        // console.log(this.state.fieldValue)
        const data = await this.orm.readGroup("asset.management.asset",[],[this.state.fieldValue],[this.state.fieldValue])
        // console.log(data)

        this.state.selectedFieldValues = {
            data: {
                labels: data.map(row => row[this.state.fieldValue]) ,
                datasets: [{
                label: 'Number of Assets',
                data: data.map(row => row[this.state.fieldValue + '_count']),
                hoverOffset: 10 
                }]
            },
            labels: {
                color:'black',
                font: {
                    weight: 'bold'
                },
                generateLabels: (chart) => {
                  const datasets = chart.data.datasets;
                  return datasets[0].data.map((data, i) => ({
                    text: `${chart.data.labels[i]} (${data})`,
                    fillStyle: datasets[0].backgroundColor[i],
                    index: i
                  }))
                }
            }
        }

    }
    async onChangeGraphType(){
        // console.log(this.state.graphType)
        this.state.refresh_key++;
    }  

}

AssetDashboard.template = "custom_dashboard.AssetDashboard";
AssetDashboard.components = { KpiCard, ChartRender }

registry. category("actions").add( "custom_dashboard.asset_dashboard", AssetDashboard)
