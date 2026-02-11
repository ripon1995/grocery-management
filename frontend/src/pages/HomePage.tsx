import {useNavigate} from 'react-router-dom';
import {Typography} from '@mui/material';
import GroceryTable from "../components/grocery_components/GroceryList.tsx";
import Box from "@mui/material/Box";
import {MonthlyGroceryAppAddButton} from "../components/common/MonthlyGroceryAppButton.tsx";
import PATHS from "../constants/paths.ts";


function HomePage() {
    const navigate = useNavigate();

    const handleSave = () => {
        navigate(PATHS.ADD_GROCERY);
    };

    return (
        <Box>
            {/* Header Row Container */}
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center', // Centers the Typography
                    position: 'relative',    // Allows button to be positioned absolutely
                    mb: 4                    // Spacing below the header
                }}
            >
                {/* 1. The Title (Centered) */}
                <Typography variant="h4" sx={{fontWeight: 'bold'}}>
                    Monthly Grocery List
                </Typography>

                {/* 2. The Button (Pushed to Right) */}
                <Box sx={{position: 'absolute', right: 0}}>
                    <MonthlyGroceryAppAddButton onClick={handleSave}/>
                </Box>
            </Box>
            <GroceryTable></GroceryTable>
        </Box>
    );
}

export default HomePage;