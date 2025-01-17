import StockSentimentGraph from './components/StockSentimentGraph'
import NavBar from './components/layout/navbar'
import {useState} from "react"
import {styled } from '@mui/system';
import { Container, Typography} from '@mui/material'
import StarBorderIcon from '@mui/icons-material/StarBorder';


function App() {
  // MUI customization
  const container = {
    position: "relative",
    width: "100%",
    maxWidth: "1300px !important",
    margin: 0,
    backgroundColor: "white",
    padding: "14px 20px",
    marginLeft: "auto",
    marginRight: "auto"
  }
  
  const Subtitle = styled(Typography)({
    position: "relative",
    color: "gray",
    fontWeight: 500,
    fontSize: 12,
    marginTop: 20
  })

  const Title = styled(Typography)({
    position: "relative",
    display: "inline-block",
    color: "black",
    fontWeight: "600",
    fontSize: 28,
    marginBottom: 20
  })

  const FollowBttn = styled(Typography)({
    position: "relative",
    display: "inline-block",
    color: "black",
    border: "1px solid grey",
    borderRadius: 20,
    fontSize: "13px",
    padding: "0px 10px",
    paddingLeft: "17px",
    marginLeft: "10px",
    verticalAlign: "middle",
    cursor: "pointer"
  })

  // Logic
  const [ticker, setTicker] = useState<string>("AAPL")
  const [company, setCompany] = useState<string>("APPLE")

  const handleSearch = (company: string, ticker: string) => {
    setCompany(company.toUpperCase())
    setTicker(ticker.toUpperCase())    
  }


  return (
    <>
    <NavBar onSearch={handleSearch}/>
    <Container sx={container}>
      <Subtitle>{company} Real Time Setiment and Price • USD</Subtitle>
      {/* Add Follow Button here to get live update of extreme sentiment */}
      <div>
        <Title>{company} ({ticker})</Title>
        <FollowBttn>
          <StarBorderIcon sx={{
            position: "absolute",
           fontSize: 15,
           left: 2,
           transform: "translateY(-50%)",
           top: "48%",
          }}/>Follow
        </FollowBttn>
      </div>
      <StockSentimentGraph company={company} ticker={ticker}/>
    </Container>
    </>
  )
}

export default App
