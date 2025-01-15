import StockSentimentGraph from './components/StockSentimentGraph'
import { Container, Box, Typography} from '@mui/material'

function App() {

  // MUI customization
  const container = {
    position: "relative"
  }



  return (
    <Container sx={container}>
      <StockSentimentGraph/>
      
    </Container>
  )
}

export default App
