import React, {useEffect, useState} from 'react';
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
import axios from 'axios';
import { Line } from 'react-chartjs-2';

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend, Filler);

interface TestData {
    timestamp: string;
    price: number;
    fear_greed_score: number;
    correlation: number;
    sentiment: number;
    "article url": string;
    title: string;
    "top comment": string;
    positive_spike: boolean;
    negative_spike: boolean;
    action: string;
  }
  
interface BackendResponse {
    latency: number;
    "extreme postive threshold": number;
    "extreme negative threshold": number;
    "market analyzed": TestData[];
  }

function StockSentimentGraph(){
    const [data, setData] = useState<BackendResponse | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);


    useEffect(() => {
        const FetchData = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/analyze-market/apple?ticker=AAPL&time_filter=month');
                setData(response.data)
                setIsLoading(false);
            } catch (err: any) {
                setError(err.message || 'Error while fetching data')
                setError('Failed to fetch data');
                setIsLoading(false);
            }
        };
        FetchData()
    }, [])

    useEffect(() => {
      if (data) {
          console.log(data['market analyzed']); 
      }
    }, [data]); 

    
    if (isLoading) return <p>Loading...</p>
    if (error) return <p>{error}</p>

    return (
    <>
        <div style={{ padding: '20px' }}>
      <h1>Backend Data</h1>
      <p><strong>Latency:</strong> {data?.latency} ms</p>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Price</th>
            <th>Fear/Greed Score</th>
            <th>Correlation</th>
            <th>Sentiment</th>
            <th>Article URL</th>
            <th>Title</th>
            <th>Top Comment</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
        {data?.['market analyzed'].map((item, index) => (
          <tr key={index}>
          <td>{item.timestamp}</td>
          <td>{item.price.toFixed(2)}</td>
          <td>{item.fear_greed_score.toFixed(2)}</td>
          <td>{item.correlation.toFixed(2)}</td>
          <td>
            {typeof item.sentiment === "number" ? item.sentiment.toFixed(2) : item.sentiment}
          </td>
          <td>{item["article url"] || "No URL"}</td>
          <td>{item.title || "No Title"}</td>
          <td>{item["top comment"] || "No Comment"}</td>
          <td>{item["action"]}</td>
        </tr>
        ))}
        </tbody>
      </table>
    </div>
    </>
    )

}

export default StockSentimentGraph