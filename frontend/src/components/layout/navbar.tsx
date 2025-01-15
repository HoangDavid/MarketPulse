import { useState} from "react";
import {Box, Container, Typography} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search';
import { styled } from '@mui/system';


interface NavBarProps {
    onSearch: (company: string, ticker: string, ) => void
}

function NavBar({onSearch}: NavBarProps){
    // MUI customization
    const container ={
        position: "sticky",
        width: "100%",
        maxWidth: "2000px !important",
        margin: 0,
        padding: 0,
        backgroundColor: "#f5f8fa",
        borderBottom: "3px solid #4682B4",
    }

    const navbar = {
        position: "relative",
        marginLeft: "24px",
        marginRight: "24px",
        padding: "10px 0px",
        paddingTop: "15px"
    }

    const Logo = styled(Typography)({
        fontWeight: 600,
        fontSize: 25
    })

    const Sub = styled(Typography)({
        fontSize: 15,
        fontWeight: 600,
        fontColor: "black",
        borderRadius: "20px",
        border:"1px solid #e0e4e9",
        padding: "10px",
        cursor: "pointer"
    })

    // Search Logic
    const [inputValue, setInputValue] = useState('');
    const [error, setError] = useState(false); // Track for input format Eror


    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputValue(e.target.value);
        setError(false)
    }

    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            const regex = /^[A-Za-z]+:[A-Za-z]+$/ // Format: NAME:SYMBOL
            if (regex.test(inputValue)) {
                const [name, symbol] = inputValue.split(":")
                onSearch(name, symbol)
            } else {
                setError(true);
            }
        }
    }
    

    return (
        <Container sx={container}>
            <Box sx={navbar}>
                <div style={{display: "inline-block"}}>
                    <Logo>
                        Market <span style={{
                        background: "linear-gradient(90deg, #FF6347, #DC143C, #B22222)",
                        WebkitBackgroundClip: "text", 
                        color: "transparent",
                        }}>
                            Pulse!
                        </span>
                    </Logo>
                </div>
                
                <div style={{position: "relative", display: "inline-block",verticalAlign: "middle", marginBottom: "10px"}}>
                    <input style={{
                        width: "500px",
                        marginLeft: "20px",
                        borderRadius: "20px",
                        padding: "10px",
                        paddingLeft: "20px",
                        fontWeight: 500,
                        fontSize: 15,
                        border: error ? "1.5px solid red" : "1px solid #e0e4e9",
                        outline: error ? "none" : undefined,
                    }}
                    type="text"
                    value={inputValue}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyPress}
                    placeholder="Search for tech companies (Ex: APPLE:AAPL)"/>

                    <SearchIcon sx={{
                        position: "absolute",
                        right: "0px",
                        color: "white",
                        top: "50%",
                        padding: "8px 25px",
                        transform: "translateY(-50%)",
                        background: "#4682B4",
                        borderRadius: "20px",
                        cursor: "pointer"
                    }}/>
                </div>
                <div style={{float: "right", verticalAlign: "bottom"}}>
                    <Sub>Subscribe</Sub>
                </div>
                
            </Box>
        </Container>
    )
}


export default NavBar