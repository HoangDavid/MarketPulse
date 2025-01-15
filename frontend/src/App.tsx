import StockSentimentGraph from './components/StockSentimentGraph'
import NavBar from './components/layout/navbar'
import {useState} from "react"
import { border, styled } from '@mui/system';
import { Container, Typography} from '@mui/material'


function App() {
  // MUI customization
  const container = {
    position: "relative",
    width: "100%",
    maxWidth: "1300px !important",
    margin: 0,
    backgroundColor: "white",
    padding: "14px 20px",
    border: "solid",
    marginLeft: "auto",
    marginRight: "auto"
  }
  
  const Subtitle = styled(Typography)({
    position: "relative",
    color: "gray",
    fontWeight: 500,
    fontSize: 12
  })

  const Title = styled(Typography)({
    position: "relative",
    color: "black",
    fontWeight: "600",
    fontSize: 28
  })

  // Logic
  const [ticker, setTicker] = useState<string>("")
  const [company, setCompany] = useState<string>("")

  const handleSearch = (company: string, ticker: string) => {
    setCompany(company.toUpperCase())
    setTicker(ticker.toUpperCase())    
  }


  return (
    <>
    <NavBar onSearch={handleSearch}/>
    <Container sx={container}>
      <Subtitle>{company} Real Time Setiment and Price • USD</Subtitle>
      <Title>{company} ({ticker})</Title>
      <StockSentimentGraph/>
      
    </Container>
    </>
  )
}

export default App
