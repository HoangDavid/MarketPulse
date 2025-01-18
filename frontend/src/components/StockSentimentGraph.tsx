import {useEffect, useState} from 'react';
import {Box, Typography, Tooltip} from '@mui/material'
import {styled} from '@mui/system';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Legend,
  Filler,
  Plugin
} from 'chart.js';
import "chartjs-adapter-date-fns";
import Chart from 'chart.js/auto';
import axios from 'axios';
import { MarketData } from '../types/MarketData';

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Legend, Filler);

interface StockSentimentProps {
  company: string,
  ticker: string,
}

interface ChartData {
  labels: string[]; 
  datasets: {
    label: string; 
    data: number[];
    yAxisID: string;
    borderColor: string;
    backgroundColor?: string;
    fill?: boolean;
    tension?: number;
    pointRadius?: number[];
    pointBackgroundColor?: string[];
  }[];
}

interface TopEvents {
  timestamp: string,
  action: string,
  value: number,
  headline: string,
  url: string,
  top_comment: string,
  correlation: number
}

const  StockSentimentGraph= ({company, ticker}: StockSentimentProps) => {

  // MUI customization
  const graph = {
    position: "relative",
    display: "inline-block",
    width: "70%",
    boxSizing: "border-box",
    verticalAlign: "middle"
  }

  const leaderBoard = {
    position: "relative",
    display: "inline-block",
    padding: "30px",
    width: "30%",
    boxSizing: "border-box",
    verticalAlign: "middle",
    height: "435px",
    backgroundColor: "#f5f8fa"
  }

  const boardDetail = {
    position: "relative",
    backgroundColor: "white",
    padding: "20px",
    marginTop: "10px",
    borderRadius: 5,
    height: "80%",
    overflowY: "scroll"
  }

  const Event = styled(Typography)({
    position: "relative",
    marginBottom: 10,
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
    cursor: "pointer",
    fontSize: 14
  })

  const BoardTitle = styled(Typography)({
    position: "relative",
    fontWeight: 600,
    fontColor: "black",
    fontSize: 20,
  })

  // Logic
  const [chartData, setChartData] = useState<ChartData>()
  const [topEvents, setTopEvents] = useState<TopEvents[]>()
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);


  // Fetch data from the backend
  useEffect(() => {
    const FetchData = async () => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/api/analyze-market/${company}?ticker=${ticker}&time_filter=month`
        );
                
        // Prepare Chart Data
        const data: MarketData[] = response.data["market_analyzed"]
        const timestamps = data.map((item) => item.timestamp);
        const prices = data.map((item) => item.price)
        const sentiments = data.map((item) => item.sentiment)
        const actions = data
          .filter((item) =>
            ["Mixed signal", "Potential exit", "Momentum trade"].includes(item.action)
          )
          .map((item) => ({
            timestamp: item.timestamp,
            action: item.action,
            value: Math.abs(item.sentiment),
            headline: item.title,
            url: item.article_url,
            top_comment:item.top_comment,
            correlation: item.correlation
          }));
        
        // Take top 3 events over time
        const events = actions
          .sort((a, b) => b.value - a.value)
          .slice(0, 8)

        setTopEvents(events)

        const PointRadius = timestamps.map((timestamp) =>
          actions.some((a) => a.timestamp === timestamp) ? 5 : 0
        );

        const PointBackgroundColor = timestamps.map((timestamp) => {
          const action = actions.find((a) => a.timestamp === timestamp)?.action;
          if (action === "Mixed signal") return "#FFD700";
          if (action === "Potential exit") return "#FF4500";
          if (action === "Momentum trade") return "#3CB371";
          return "rgba(0, 0, 0, 0)";
        });

        setChartData({
          labels: timestamps,
          datasets: [
            {
              label: "Stock Price",
              data: prices,
              yAxisID: "yPrice",
              borderColor: "#002D62",
              tension: 0.3,
              pointRadius: PointRadius,
              pointBackgroundColor: PointBackgroundColor,
            },
            {
              label: "Sentiment",
              data: sentiments,
              yAxisID: "ySentiment",
              borderColor: "#FF6347",
              tension: 0.3,
              pointRadius: PointRadius,
              pointBackgroundColor: PointBackgroundColor,
            },
          ],
        });
        
        setIsLoading(false);
      } catch (error) {
        // Catch Error during API call
        console.log(error)
        setError(`Failed to fetch data: ${error}`);
        setIsLoading(false);
      }
    };

  
    FetchData()
  }, [ticker, company])

  const actionColors: { [key: string]: string } = {
    "Mixed signal": "#FFC000",
    "Potential exit": "#FF4500",
    "Momentum trade": "#3CB371",
  };

  
  // Add loading animation
  if (isLoading) return <p>Loading...</p>

  // Add 
  if (error) return <p>{error}</p>

  return (
    <>
    <Box sx={graph}>
    {chartData && (
          <Line
            data={chartData}
            options={{
              responsive: true,
              plugins: {
                legend: {
                  display: true,
                  position: "top",
                  labels: {
                    generateLabels: (chart) => {
                      const originalLabels = Chart.defaults.plugins.legend.labels.generateLabels(chart).map((label) => ({
                        ...label,
                        usePointStyle: true,
                        fillStyle: label.strokeStyle,
                        boxWidth: 40,
                        borderRadius: 10,
                      }));
                    
                      const customLabels = [
                        {
                          text: "Actions:",
                          fillStyle: "rgba(0, 0, 0, 0)",
                          strokeStyle: "rgba(0, 0, 0, 0)",
                          hidden: false,
                          borderRadius: 0,
                          boxWidth: 0,
                          fontColor: "black",
                          fontStyle: "bold",
                        },
                        {
                          text: "Mixed Signal",
                          fillStyle: "#FFD700",
                          strokeStyle: "#FFD700",
                          hidden: false,
                          lineDash: [],
                          lineWidth: 0,
                          datasetIndex: undefined,
                          borderRadius: 10,
                        },
                        {
                          text: "Potential Exit",
                          fillStyle: "#FF4500",
                          strokeStyle: "#FF4500",
                          hidden: false,
                          lineDash: [],
                          lineWidth: 0,
                          datasetIndex: undefined,
                          borderRadius: 10,
                        },
                        {
                          text: "Momentum Trade",
                          fillStyle: "#3CB371",
                          strokeStyle: "#3CB371",
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
                  },
                },
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
                yPrice: {
                  type: "linear",
                  position: "left",
                  title: {
                    display: true,
                    text: "Stock Price",
                  },
                },
                ySentiment: {
                  type: "linear",
                  position: "right",
                  title: {
                    display: true,
                    text: "Sentiment",
                  },
                  grid: {
                    drawOnChartArea: false,
                  },
                },
              },
            }}
            plugins={[verticalLinePlugin]}
          />
        )}
    </Box>

    <Box sx={leaderBoard}>
      <BoardTitle>Top Events</BoardTitle>
      <Box sx={boardDetail}>
        {topEvents?.map((event, index)=> (
          <>
          <Event key={index}>
          <Tooltip title={
            <div style={{ textAlign: "left", padding: "5px", maxWidth: "300px" }}>
              <div style={{ fontWeight: "bold", marginBottom: "5px" }}>{event.headline}</div>
              <div style={{ fontSize: "12px", marginBottom: "5px" }}>
                <strong>Date:</strong> {event.timestamp}
              </div>
              <div style={{ fontSize: "14px", fontStyle: "italic" }}>
                <strong>Others saying:</strong> "{event.top_comment}"
              </div>
            </div>}>
            <a
              href={event.url}
              style={{ textDecoration: "none", color: "blue"}}
            >
              {index + 1}. {event.headline}
            </a>
          </Tooltip>
          <div style={{ marginTop: "5px", fontSize: "14px", color: "#555" }}>
            <strong>Date:</strong> {event.timestamp} <br/>
            <strong>Action:</strong> <span style={{color: actionColors[event.action],fontWeight: 600,}}>{event.action}</span> <br/>
            <strong>Others saying:</strong> "{event.top_comment}"
          </div>
          </Event>
          </>
        ))}
      </Box>
    </Box>
    </>
  );
}


const verticalLinePlugin: Plugin<'line'> = {
  id: 'verticalLine',
  afterDatasetsDraw: (chart) => {
    const activeElements = chart.tooltip?.getActiveElements();
    if (activeElements && activeElements.length > 0) {
      const ctx = chart.ctx;
      const activePoint = activeElements[0];
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
      ctx.restore();

      // Draw circles at active points
      chart.data.datasets.forEach((dataset, index) => {
        const meta = chart.getDatasetMeta(index);
        const point = meta.data[activePoint.index];
        if (point) {
          ctx.save();
          ctx.beginPath();
          ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
          ctx.fillStyle = dataset.borderColor as string;
          ctx.fill();
          ctx.restore();
        }
      });
    }
  },
};

export default StockSentimentGraph