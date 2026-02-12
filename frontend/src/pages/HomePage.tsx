import {useEffect} from "react";
import {useNavigate} from 'react-router-dom';
import {Container, Typography} from '@mui/material';
import GroceryTable from "../components/grocery_components/GroceryList.tsx";
import Box from "@mui/material/Box";
import {MonthlyGroceryAppAddButton} from "../components/common/MonthlyGroceryAppButton.tsx";
import PATHS from "../constants/paths.ts";
import useGroceryStore from "../store/useGroceryStore.ts";
import MonthlyGroceryAppLoader from "../components/common/MonthlyGroceryAppLoader.tsx";


function HomePage() {
    const navigate = useNavigate();

    // 1. Hook into the store at the Page level
    const {groceries, fetchGroceries, isLoading} = useGroceryStore();

    // 2. Trigger the fetch when the page mounts
    useEffect(() => {
        fetchGroceries().then();
    }, [fetchGroceries]);

    const handleSave = () => {
        navigate(PATHS.ADD_GROCERY);
    };
    const handleOnViewAction = (grocery_id: string) => {
        navigate(PATHS.DETAIL_GROCERY.replace(':id', grocery_id));
    };
    const handleOnEditAction = (grocery_id: string) => {
        navigate(PATHS.EDIT_GROCERY.replace(':id', grocery_id));
    };
    const handleOnDeleteAction = () => {
        navigate(PATHS.ADD_GROCERY);
    };


    // 2. Handle Loading State (Moved from Child to Page)
    if (isLoading || !groceries) {
        return (
            <Container>
                <Typography variant="h4" sx={{mb: 2}}>Monthly Grocery Detail</Typography>
                <MonthlyGroceryAppLoader message="Fetching list..."/>
            </Container>
        );
    }


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
            <GroceryTable
                groceries={groceries}
                onView={handleOnViewAction}
                onEdit={handleOnEditAction}
                onDelete={handleOnDeleteAction}>
            </GroceryTable>
        </Box>
    );
}

export default HomePage;