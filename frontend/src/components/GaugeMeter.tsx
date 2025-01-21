import {useEffect, useState} from "react"
import {Box, Typography} from '@mui/material'
import {styled} from '@mui/system';
import GaugeChart from "react-gauge-chart"
import axios from 'axios';
import { FearGreedData } from "../types/FearGreedData";
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Legend,
  Tooltip,
  Plugin
} from 'chart.js';
import "chartjs-adapter-date-fns";


// Register necessary Chart.js components
ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend);


interface ChartData {
    labels: string[];
    datasets: {
      label: string;
      data: number[];
      borderColor: string;
      backgroundColor?: string;
      fill?: boolean;
      tension?: number;
      pointRadius?: number[];
      pointBackgroundColor?: string[];
    }[];
  }

interface OverviewSentiment {
    prev_close: number,
    last_week: number,
    last_month: number,
    last_year: number
}

function FearGreedMeter() {

    // MUI customization
    const graph = {
        position: "relative",
        display: "inline-block",
        width: "68%",
        verticalAlign: "middle",
        boxSizing: "border-box",
    }

    const detail = {
        position: "relative",
        display: "inline-block",
        width: "32%",
        paddingLeft: "20px",
        verticalAlign: "top",
        height: "380px",
        boxSizing: "border-box"
    }

    const SwitchBg = styled(Typography)({
        backgroundColor: "lightgrey",
        width: "fit-content",
        borderRadius: "10px",
        marginLeft: "auto",
        marginRight: "0"
    })

    const SwitchBttn = styled(Typography)({
        backgroundColor: "transparent",
        display: "inline-block",
        color: "black",
        cursor: "pointer",
        margin: "3px 5px",
        padding: "2px 6px",
        borderRadius: "10px",
        fontWeight:500,
        fontSize: 13,
    })

    
    const Sentiment =  styled(Typography)({
        fontSize: 18,
        fontWeight: 600,
    })

    const SentimentTime = styled(Typography)({
        fontSize: 12,
        fontWeight: 500,
        borderTop: "1px dotted black",
    })

    const SentimentScore = styled(Typography)({
        fontSize: 15,
        display:  "inline-block",
        marginLeft: 10,
        borderRadius: "100%",
        padding: "5px",
        float: "right"
    })

    // Logic
    const [gaugeData, setGaugeData] = useState<OverviewSentiment>({
        prev_close: 0,
        last_week:  0,
        last_month: 0,
        last_year: 0
    })
    const [chartData, setChartData] = useState<ChartData>()
    const [error, setError] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState<boolean>(true)
    const [bttn, setBttn] = useState<boolean>(false)


    useEffect(() => {
        const fetchData = async () => {
            try{
                // Prepare data for gauge meter
                const response = await axios.get( 'http://127.0.0.1:8000/api/market-sentiment/fear_greed_score')
                const fetched_data = response.data["fear_greed_score"]
                const data = {
                    prev_close: fetched_data[fetched_data.length - 1]["fear_greed_score"].toFixed(0),
                    last_week: fetched_data[fetched_data.length - 1 - 7]["fear_greed_score"].toFixed(0),
                    last_month: fetched_data[fetched_data.length - 1 - 30]["fear_greed_score"].toFixed(0),
                    last_year: fetched_data[0]["fear_greed_score"].toFixed(0)
                }
                setGaugeData(data)

                // Prepare data for chart
                const chart_data: FearGreedData[] = fetched_data
                const timestamps = chart_data.map((item) => item.timestamp)
                const scores = chart_data.map((item) => item.fear_greed_score)

                setChartData({
                    labels: timestamps,
                    datasets: [
                        {
                            label: "Fear-Greed Score",
                            data: scores,
                            borderColor: "#FF6347",
                            tension: 0.4
                        },
                    ],
                },
                )


                setIsLoading(false)
            }catch (error){
                console.log(error)
                setError(`Failed to fetch data: ${error}`)
                setIsLoading(false)
            }
        }
        
        fetchData()
    }, [])


    useEffect(() => {
        console.log(gaugeData)
    }, [gaugeData])

    const gaugeColor  = [
        "rgba(217, 83, 79, 0.9)", // extreme fear
        "rgba(240, 173, 78, 0.9)", // fear
        "rgba(92, 184, 92, 0.9)", // greed
        "rgba(76, 174, 76, 0.9)",// extreme greed
    ]

    const getGaugeColorSentiment = (score: number) => {
        if (score < 25) return [gaugeColor[0], "Extreme Fear"]
        else if (score >= 25 && score < 50) return [gaugeColor[1], "Fear"]
        else if (score >= 50 && score < 75) return [gaugeColor[2], "Greed"]
        else return [gaugeColor[-1], "Extreme Greed"]
    }


    if (isLoading) return <div>Loading ...</div>
    if (error) return  <div>{error}</div>

    return (
    <>
        {!bttn && (
        <Box sx={graph}>
            <GaugeChart
                id="fear-greed-meter"
                colors={gaugeColor}
                percent={gaugeData.prev_close / 100}
                arcWidth={0.3}
                arcsLength={[0.25, 0.25, 0.25, 0.25]} // Evenly distribute arcs
                hideText
            />
        </Box>)
        }

        {bttn && chartData && (
        <Box sx={graph}>
            <Line
            data={chartData}
            options={{
              responsive: true,
              plugins:{
                tooltip: {
                    enabled: true,
                    mode: "index",
                    intersect: false,
                  },
              },
              scales: {
                x: {
                  type: "time",
                  time: {
                    unit: "month",
                    displayFormats: {
                      month: "MMM yyyy",
                    },
                  },
                  title: {
                    display: true,
                    text: "Time",
                  },
                },
                y: {
                  type: "linear",
                  position: "left",
                  title: {
                    display: true,
                    text: "Fear-Greed Score",
                  },
                },
              },
            }}
            plugins={[verticalLinePlugin]}
          />
        </Box> 
        )}
        <Box sx={detail}>
            <SwitchBg>
                <SwitchBttn onClick={ () => setBttn(false)} sx={{backgroundColor: !bttn ? 'white' : "transparent"}}>Overview</SwitchBttn>
                <SwitchBttn onClick={ () => setBttn(true)} sx={{backgroundColor: bttn ? 'white' : "transparent"}}>Timeline</SwitchBttn>
            </SwitchBg>
            <div style={{margin: "20px 0px"}}>
                <SentimentTime>Previous Close</SentimentTime>
                <Sentiment>
                    {getGaugeColorSentiment(gaugeData.prev_close)[1]}
                    <SentimentScore sx={{backgroundColor: getGaugeColorSentiment(gaugeData.prev_close)[0]}}>{gaugeData.prev_close}</SentimentScore>
                </Sentiment>
            </div>
            <div style={{margin: "20px 0px"}}>
                <SentimentTime>Last Week</SentimentTime>
                <Sentiment>
                    {getGaugeColorSentiment(gaugeData.last_week)[1]}
                    <SentimentScore  sx={{backgroundColor: getGaugeColorSentiment(gaugeData.last_week)[0]}}>{gaugeData.last_week}</SentimentScore>
                </Sentiment>
            </div>
            <div style={{margin: "20px 0px"}}>
                <SentimentTime>Last Month</SentimentTime>
                <Sentiment>
                    {getGaugeColorSentiment(gaugeData.last_month)[1]}
                    <SentimentScore sx={{backgroundColor: getGaugeColorSentiment(gaugeData.last_month)[0]}}>{gaugeData.last_month}</SentimentScore>
                </Sentiment>
            </div>
            <div style={{margin: "20px 0px"}}>
                <SentimentTime>Last Year</SentimentTime>
                <Sentiment>
                    {getGaugeColorSentiment(gaugeData.last_year)[1]}
                    <SentimentScore sx={{backgroundColor: getGaugeColorSentiment(gaugeData.last_year)[0]}}>{gaugeData.last_year}</SentimentScore>
                </Sentiment>
            </div>
        </Box>

    </>
    )

}


const verticalLinePlugin: Plugin<'line'> = {
    id: 'verticalLine',
    beforeDraw: (chart) => {
      const activeElements = chart.tooltip?.getActiveElements();
      if (activeElements && activeElements.length > 0) {
        const ctx = chart.ctx;
        const x = activeElements[0].element.x;
        const topY = chart.chartArea.top;
        const bottomY = chart.chartArea.bottom;
  
        // Draw a continuous vertical dashed line
        ctx.save();
        ctx.beginPath();
        ctx.setLineDash([5, 5]); // Dashed line style
        ctx.moveTo(x, topY);
        ctx.lineTo(x, bottomY);
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.5)'; // Semi-transparent gray
        ctx.stroke();
        ctx.restore();
  
        // Draw hover points for all datasets at the active index
        chart.data.datasets.forEach((dataset, datasetIndex) => {
          const meta = chart.getDatasetMeta(datasetIndex);
          if (meta && meta.data[activeElements[0].index]) {
            const point = meta.data[activeElements[0].index];
            if (point) {
              ctx.save();
              ctx.beginPath();
              ctx.arc(point.x, point.y, 6, 0, 2 * Math.PI); // Slightly larger circle for hover
              ctx.fillStyle = dataset.borderColor as string; // Match the dataset color
              ctx.fill();
              ctx.lineWidth = 2;
              ctx.strokeStyle = '#fff'; // Add a white outline for contrast
              ctx.stroke();
              ctx.restore();
            }
          }
        });
      }
    },
  };
  



export default FearGreedMeter