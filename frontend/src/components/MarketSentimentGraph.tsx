import {useEffect, useState} from 'react'
import { Box, Typography } from '@mui/material';
import { Line } from 'react-chartjs-2';
import {styled} from '@mui/system';
import axios from 'axios'
import { MomentumData } from '../types/MomentumData';
import { SafeHavenData } from '../types/SafeHavenData';
import { VixData } from '../types/VixData';
import { YieldSpreadData } from '../types/YieldSpreadData';
import { ChartData } from '../types/ChartData';
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

function MarketSentimentGraph(){
    
    // MUI customization
    const graph = {
        position: 'relative',
        display: 'inline-block',
        width: '68%',
        boxSizing: 'border-box'
    }

    const Detail = styled(Typography)({
        position: 'relative',
        display: 'inline-block',
        width: '32%',
        boxSizing: 'border-box',
        paddingLeft: '35px',
        verticalAlign: 'top',
        fontWeight: 500,
        paddingTop: '25px'
    })

    const Title = styled(Typography)({
        position: 'relative',
        fontWeight: 600,
        fontSize: 25,
        marginTop: "20px",
    })

    // Logic
    const [momentumChart, setMomentumChart] = useState<ChartData | undefined>()
    const [safeHavenChart, setSafeHavenChart] = useState<ChartData | undefined>()
    const [vixChart, setVixChart] = useState<ChartData | undefined>()
    const [yieldSpreadChart, setYieldSpreadChart] = useState<ChartData | undefined>() 

    useEffect(() => {
        const fetchData = async() => {
            const momentumResponse = await axios.get('http://127.0.0.1:8000/api/market-sentiment/market_momentum')
            const safeHavenResponse = await axios.get('http://127.0.0.1:8000/api/market-sentiment/safe_haven')
            const vixResponse = await axios.get('http://127.0.0.1:8000/api/market-sentiment/vix')
            const yieldSpreadResponse = await axios.get('http://127.0.0.1:8000/api/market-sentiment/yield_spread')

            const momentumData: MomentumData[] = momentumResponse.data['market_momentum']
            const safeHavenData: SafeHavenData[] = safeHavenResponse.data['safe_haven']
            const vixData: VixData[] = vixResponse.data['vix']
            const yieldSpreadData: YieldSpreadData[] = yieldSpreadResponse.data['yield_spread']

            console.log(momentumData)
            
            setMomentumChart({
                labels: momentumData.map((item) => item.timestamp),
                datasets: [
                  {
                    label: "S&P500",
                    data: momentumData.map((item) => item['S&P500']),
                    borderColor: "#002D62",
                    tension: 0.3,
                    pointRadius: momentumData.map(() => 0), 
                    yAxisID: "y",
                  },
                  {
                    label: "S&P500 Moving Average 125",
                    data: momentumData.map((item) => item['S&P500_125']),
                    borderColor: "#FF6347",
                    tension: 0.3,
                    pointRadius: momentumData.map(() => 0), 
                    yAxisID: "y", 
                  },
                ],
              });

            setSafeHavenChart({
                labels: safeHavenData.map((item) => item.timestamp),
                datasets:[
                {
                    label: "Safe Haven",
                    data: safeHavenData.map((item) => item.safe_haven * 100),
                    yAxisID: "y",
                    borderColor: "#002D62",
                    pointRadius: safeHavenData.map(() => 0), 
                    tension: 0.3
                }
                ]
            })

            setVixChart({
                labels: vixData.map((item) => item.timestamp),
                datasets:[
                {
                    label: "VIX",
                    data: vixData.map((item) => item.VIX),
                    yAxisID: "y",
                    borderColor: "#002D62",
                    pointRadius: vixData.map(() => 0), 
                    tension: 0.3
                },
                {
                    label: "VIX Moving Average 50",
                    data: vixData.map((item) => item.VIX_50),
                    yAxisID: "y",
                    borderColor: "#FF6347",
                    pointRadius: vixData.map(() => 0), 
                    tension: 0.3
                }
                ]
            })

            setYieldSpreadChart({
                labels: yieldSpreadData.map((item) => item.timestamp),
                datasets: [
                {
                    label: "Yield Spread",
                    data: yieldSpreadData.map((item) => item.yield_spread * 100),
                    yAxisID: "y",
                    borderColor: "#002D62",
                    pointRadius: yieldSpreadData.map(() => 0), 
                    tension: 0.3
                }
                ]
            })
            
        }

        fetchData()
    }, [])

    useEffect(() => {
        console.log(momentumChart)
    }, [momentumChart, safeHavenChart, vixChart, yieldSpreadChart])

    return (
        <>
        {/* Market Momentum */}
        <div>
            <Title> Market Momentum</Title>
            <Box sx={graph}>
            {momentumChart && (
               <Line
               data={momentumChart}
               options={{
                 responsive: true,
                 plugins: {
                   tooltip: {
                     enabled: true,
                     mode: "index",
                     intersect: false,
                   },
                   legend: {
                     display: true,
                     position: "top",
                     labels: {
                       usePointStyle: true,
                       boxWidth: 15,
                     },
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
                       text: "Value",
                     },
                   },
                 },
               }}
               plugins={[verticalLinePlugin]}
             />
            )}
            </Box>

            <Detail>
            Examining stock market levels relative to their performance over the past few months can provide valuable insights. 
            When the S&P 500 is trading above its 125-day moving average, it indicates positive momentum in the market. 
            Conversely, when the index falls below this average, it suggests increased caution among investors. 
            The Fear & Greed Index interprets weakening momentum as a sign of Fear and strengthening momentum as a signal of Greed.
            </Detail>

        </div>
        
        {/* VIX */}
        <div>
            <Title> Market Votality </Title>
            <Box sx={graph}>
            {vixChart && (
               <Line
               data={vixChart}
               options={{
                 responsive: true,
                 plugins: {
                   tooltip: {
                     enabled: true,
                     mode: "index",
                     intersect: false,
                   },
                   legend: {
                     display: true,
                     position: "top",
                     labels: {
                       usePointStyle: true,
                       boxWidth: 15,
                     },
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
                       text: "Value",
                     },
                   },
                 },
               }}
               plugins={[verticalLinePlugin]}
             />
            )}
            </Box>
            
            <Detail>
            The CBOE Volatility Index (VIX) is one of the most widely recognized indicators of market sentiment. 
            It tracks expected price fluctuations or volatility in S&P 500 Index options over the next 30 days. 
            Typically, the VIX declines on days when the market surges and spikes during sharp market declines. 
            However, its true value lies in observing trends over time: lower levels are often associated with bull markets, while higher levels indicate bear market conditions. 
            The Fear & Greed Index interprets rising market volatility as a sign of Fear.
            </Detail>
        </div>

        {/* Yield Spread */}
        <div>
            <Title> Junk Bond Demand </Title>
            <Box sx={graph}>
            {yieldSpreadChart && (
               <Line
               data={yieldSpreadChart}
               options={{
                 responsive: true,
                 plugins: {
                   tooltip: {
                     enabled: true,
                     mode: "index",
                     intersect: false,
                   },
                   legend: {
                     display: true,
                     position: "top",
                     labels: {
                       usePointStyle: true,
                       boxWidth: 15,
                     },
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
                       text: "Value",
                     },
                     ticks: {
                        callback: (value) => `${value}%`,
                    },
                   },
                 },
               }}
               plugins={[verticalLinePlugin]}
             />
            )}
            </Box>

            <Detail>
            Junk bonds are riskier than other types of bonds due to their higher likelihood of default. 
            When investors show increased demand for junk bonds, their prices rise and yields—returns on investment—fall. 
            Conversely, yields increase when investors sell off these bonds. A narrowing spread between yields for junk bonds and safer government bonds indicates that investors are more willing to take on risk. 
            On the other hand, a widening spread signals greater caution. 
            The Fear & Greed Index interprets strong demand for junk bonds as an indicator of Greed.
            </Detail>
        </div>

        {/* Safe Haven */}
        <div>
            <Title> Safe Haven Demand </Title>
            <Box sx={graph}>
            {safeHavenChart && (
               <Line
               data={safeHavenChart}
               options={{
                 responsive: true,
                 plugins: {
                   tooltip: {
                     enabled: true,
                     mode: "index",
                     intersect: false,
                   },
                   legend: {
                     display: true,
                     position: "top",
                     labels: {
                       usePointStyle: true,
                       boxWidth: 15,
                     },
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
                       text: "Value",
                     },
                     ticks: {
                        callback: (value) => `${value}%`,
                    },
                   },
                 },
               }}
               plugins={[verticalLinePlugin]}
             />
            )}
            </Box>

            <Detail>
            Stocks carry more risk than bonds but tend to deliver higher returns over the long term. 
            However, in the short term, bonds can sometimes outperform stocks. 
            The Safe Haven Demand metric highlights the difference in returns between Treasury bonds and stocks over the last 20 trading days. 
            When bonds outperform, it often signals investor caution. 
            The Fear & Greed Index interprets rising demand for safe haven assets as an indicator of Fear.
            </Detail>
        </div>

        </>
    )
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

export default MarketSentimentGraph