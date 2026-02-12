import {Container, Typography} from '@mui/material';
import {useParams} from "react-router-dom";
import GroceryDetail from "../components/grocery_components/GroceryDetail.tsx";
import useGroceryStore from "../store/useGroceryStore.ts";
import {useEffect} from "react";

import MonthlyGroceryAppError from "../components/common/MonthlyGroceryAppError.tsx";


function GroceryDetailPage() {
    const {getGroceryDetail, grocery, isLoading, error} = useGroceryStore();
    const {id} = useParams<{ id: string }>();

    useEffect(() => {
        if (id != null) {
            getGroceryDetail(id).then();
        }
    }, [id, getGroceryDetail]);

    // 1. If there's an error and no grocery data, show Error
    if (error || grocery == null) {
        return (
            <Container>
                <Typography variant="h4" sx={{mb: 2}}>Monthly Grocery Detail</Typography>
                <MonthlyGroceryAppError message={error}></MonthlyGroceryAppError>
            </Container>
        );
    }


    return (
        <Container>
            <Typography variant="h4" sx={{fontWeight: 'regular'}}>
                Monthly Grocery Detail
            </Typography>
            <GroceryDetail grocery={grocery} isLoading={isLoading}></GroceryDetail>
        </Container>

    );
}

export default GroceryDetailPage;