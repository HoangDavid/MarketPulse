import React, {useEffect, useState} from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import Chart from 'chart.js/auto';
import axios from 'axios';
import { MarketData } from '../types/MarketData';


ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend, Filler);

const verticalLinePlugin = {
  id: 'verticalLine',
  afterDatasetsDraw: (chart: any) => {
    if (chart.tooltip._active && chart.tooltip._active.length) {
      const ctx = chart.ctx;
      const activePoint = chart.tooltip._active[0];
      const x = activePoint.element.x;
      const topY = chart.chartArea.top;
      const bottomY = chart.chartArea.bottom;

      // Draw the vertical line
      ctx.save();
      ctx.beginPath();
      ctx.setLineDash([5, 5]);
      ctx.moveTo(x, topY);
      ctx.lineTo(x, bottomY);
      ctx.lineWidth = 1;
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.3)';
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();

      
      // Draw the circle on the lines when hovering along the lines
      chart.data.datasets.forEach((dataset: any, index: number) => {
        const meta = chart.getDatasetMeta(index);
        const point = meta.data[activePoint.index];
        if (point) {
          ctx.save();
          ctx.beginPath();
          ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
          ctx.fillStyle = dataset.borderColor;
          ctx.fill();
          ctx.restore();
        }
      });
    }
  },
};


function StockSentimentGraph(){
  const [chartData, setChartData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);


  // Fetch data from the backend
  useEffect(() => {
    const FetchData = async () => {
      try {
        const response = await axios.get(
          'http://127.0.0.1:8000/api/analyze-market/nvidia?ticker=NVDA&time_filter=year'
        );
                
        // Prepare Chart Data
        const data: MarketData[] = response.data["market_analyzed"]
        const timestamps = data.map((item) => item.timestamp)
        const prices = data.map((item) => item.price)
        const sentiments = data.map((item) => item.sentiment)
        const actions = data
          .filter(
            (item) =>
              item.action === "Mixed signal" ||
              item.action === "Potential exit" ||
              item.action === "Momentum trade"
          )
          .map((item) => ({
            timestamp: item.timestamp,
            action: item.action,
          }));

          console.log(actions)

        // Determine point radius and background color for stock price
        const PointRadius = timestamps.map((timestamp) =>
          actions.some((a) => a.timestamp === timestamp) ? 3 : 0
        );

        const PointBackgroundColor = timestamps.map((timestamp) => {
          const action = actions.find((a) => a.timestamp === timestamp)?.action;
          if (action === "Mixed signal") return "orange";
          if (action === "Potential exit") return "red";
          if (action === "Momentum trade") return "green";
          return "rgba(0, 0, 0, 0)";
        });

        setChartData({
          labels: timestamps,
          datasets: [
            {
              label: 'Stock price',
              data: prices,
              yAxisID: 'yPrice',
              borderColor:  "rgba(54, 162, 235, 0.7)",
              backgroundColor: "rgba(54, 162, 235, 0.1)",
              fill: true,
              tension: 0.4,
              pointRadius: PointRadius,
              pointBackgroundColor: PointBackgroundColor
            },
            {
              label: 'Sentiment',
              data: sentiments,
              yAxisID: 'ySentiment',
              borderColor: "rgba(255, 99, 132, 0.7)",
              backgroundColor: "rgba(255, 99, 132, 0.1)",
              tension: 0.4,
              pointRadius: PointRadius,
              pointBackgroundColor: PointBackgroundColor
            }
          ]
        })
        
        setIsLoading(false);
      } catch (err) {
        // Catch Error during API call
        setError(err.message || 'Error while fetching data')
        setError('Failed to fetch data');
        setIsLoading(false);
      }
    };

  
    FetchData()
  }, [])

    
  if (isLoading) return <p>Loading...</p>
  if (error) return <p>{error}</p>

  return (
    <div>
      <h2>Stock Price and Sentiment Over Time</h2>
      {chartData && (
        <Line
          data={chartData}
          options={{
            responsive: true,
            plugins: {
              legend: {
                display: true,
                position: 'top',
                labels: {
                  generateLabels:(chart) => {
                    const originalLabels = Chart.defaults.plugins.legend.labels.generateLabels(chart).map((label) => ({
                      ...label,
                      usePointStyle: false, 
                      boxWidth: 40,
                      borderRadius: 0,
                    }));
        
                    const customLabels = [
                      {
                        text: 'Mixed Signal',
                        fillStyle: 'orange',
                        strokeStyle: 'orange',
                        hidden: false,
                        lineDash: [],
                        lineWidth: 0,
                        datasetIndex: undefined,
                        borderRadius: 10,
                      },
                      {
                        text: 'Potential Exit',
                        fillStyle: 'red',
                        strokeStyle: 'red',
                        hidden: false,
                        lineDash: [],
                        lineWidth: 0,
                        datasetIndex: undefined,
                        borderRadius: 10,
                      },
                      {
                        text: 'Momentum Trade',
                        fillStyle: 'green',
                        strokeStyle: 'green',
                        hidden: false,
                        lineDash: [],
                        lineWidth: 0,
                        datasetIndex: undefined,
                        borderRadius: 10,
                      },
                    ];
        
                    return [...originalLabels, ...customLabels];
                  },
                  boxWidth: 15,
                  usePointStyle: true, 
                }
              },
              tooltip: {
                enabled: true,
                mode: 'index',
                intersect: false,
              }
            },
            scales: {
              x: {
                title: {
                  display: true,
                  text: 'Time',
                },
              },
              yPrice: {
                type: 'linear',
                position: 'left',
                title: {
                  display: true,
                  text: 'Stock Price',
                },
              },
              ySentiment: {
                type: 'linear',
                position: 'right',
                title: {
                  display: true,
                  text: 'Sentiment',
                },
                grid: {
                  drawOnChartArea: false,
                },
              },
            }
          }}
          plugins={[verticalLinePlugin]}
        />
      )}
    </div>
  );
}

export default StockSentimentGraph