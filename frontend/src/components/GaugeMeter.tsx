import {useEffect, useState} from "react"
import {Box, Container, Typography} from '@mui/material'
import {styled} from '@mui/system';
import GaugeChart from "react-gauge-chart"
import axios from 'axios';


interface OverviewSentiment {
    prev_close: number,
    last_week: number,
    last_month: number,
    last_year: number
}

function FearGreedMeter() {

    // MUI customization
    const container = {
        position: "relative",
        padding: "0px !important",
        border: "solid",
    }

    const graph = {
        position: "relative",
        display: "inline-block",
        width: "70%",
        verticalAlign: "middle",
        boxSizing: "border-box"
    }

    const detail = {
        position: "relative",
        display: "inline-block",
        width: "28%",
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
    const [error, setError] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState<boolean>(true)
    const [bttn, setBttn] = useState<boolean>(false)


    useEffect(() => {
        const fetchData = async () => {
            try{      
                const response = await axios.get( 'http://127.0.0.1:8000/api/market-sentiment/fear_greed_score')
                const fetched_data = response.data["fear_greed_score"]
                const data = {
                    prev_close: fetched_data[fetched_data.length - 1]["fear_greed_score"].toFixed(0),
                    last_week: fetched_data[fetched_data.length - 1 - 7]["fear_greed_score"].toFixed(0),
                    last_month: fetched_data[fetched_data.length - 1 - 30]["fear_greed_score"].toFixed(0),
                    last_year: fetched_data[0]["fear_greed_score"].toFixed(0)
                }
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
    <Container sx={container}>
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

        {bttn && (
            <></>
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
    </Container>

    </>
    )

}

export default FearGreedMeter