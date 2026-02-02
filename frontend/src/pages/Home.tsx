import {Typography} from '@mui/material';
import GroceryTable from "../components/grocery_components/GroceryList.tsx";
import Box from "@mui/material/Box";

function Home() {
    return (
        <Box>
            <Typography variant="h4">Monthly Grocery List</Typography>
            <GroceryTable></GroceryTable>
        </Box>
    );
}

export default Home;