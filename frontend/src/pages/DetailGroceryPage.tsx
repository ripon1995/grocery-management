import {Container, Typography} from '@mui/material';
import {useParams} from "react-router-dom";
import GroceryDetail from "../components/grocery_components/GroceryDetail.tsx";
import useGroceryStore from "../store/useGroceryStore.ts";
import {useEffect} from "react";
import MonthlyGroceryAppError from "../components/common/MonthlyGroceryAppError.tsx";
import MonthlyGroceryAppLoader from "../components/common/MonthlyGroceryAppLoader.tsx";


function GroceryDetailPage() {
    const {getGroceryDetail, grocery, isLoading, error} = useGroceryStore();
    const {id} = useParams<{ id: string }>();

    useEffect(() => {
        if (id != null) {
            getGroceryDetail(id).then();
        }
    }, [id, getGroceryDetail]);

    // 1. If there's an error and no grocery data, show Error
    if (error) {
        return (
            <Container>
                <Typography variant="h4" sx={{mb: 2}}>Monthly Grocery Detail</Typography>
                <MonthlyGroceryAppError message={error}/>
            </Container>
        );
    }

    // 2. Handle Loading State (Moved from Child to Page)
    if (isLoading || !grocery) {
        return (
            <Container>
                <Typography variant="h4" sx={{mb: 2}}>Monthly Grocery Detail</Typography>
                <MonthlyGroceryAppLoader message="Fetching Details..."/>
            </Container>
        );
    }


    return (
        <Container>
            <Typography variant="h4" sx={{fontWeight: 'regular'}}>
                Monthly Grocery Detail
            </Typography>
            <GroceryDetail grocery={grocery}></GroceryDetail>
        </Container>

    );
}

export default GroceryDetailPage;