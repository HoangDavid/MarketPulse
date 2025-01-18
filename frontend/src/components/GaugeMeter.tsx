import {useEffect, useState} from "react"
import GaugeChart from "react-gauge-chart"
import axios from 'axios';

function FearGreedMeter() {

    const [gaugeData, setGaugeData] = useState<any>(null)
    const [error, setError] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState<boolean>(true)


    useEffect(() => {
        const fetchData = async () => {
            try{      
                const response = await axios.get( 'http://127.0.0.1:8000/api/market-sentiment/fear_greed_score')
                const data = response.data["fear_greed_score"]
                setGaugeData(data)
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
        "#d9534f", // extreme fear
        "#f0ad4e", // fear
        "#5cb85c", // greed
        "#4cae4c", // extreme greed
    ]

    const getGaugeColor = (score: number) => {
        if (score < 25) return gaugeColor[score]
        if (score >= 25 && score < 50) return gaugeColor[score]
        if (score >= 50 && score < 75) return gaugeColor[score]
        if (score >=75) return gaugeColor[score]
    }

    if (isLoading) return <div>Loading ...</div>
    // if (error) return  <div>{error}</div>
    return (
    <>
    <GaugeChart
        id="fear-greed-meter"
        nrOfLevels={30}
        colors={[
          "#d9534f",
          "#f0ad4e",
          "#5bc0de",
          "#5cb85c",
          "#4cae4c",
        ]}
        percent={20 / 100}
        arcWidth={0.3}
        arcsLength={[0.2, 0.2, 0.2, 0.2, 0.2]} // Evenly distribute arcs
        textColor="#333"
        needleColor={getGaugeColor(20)}
      />

    </>
    )

}

export default FearGreedMeter