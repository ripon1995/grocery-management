import {Container, Typography} from '@mui/material';
import {useParams} from "react-router-dom";
import GroceryDetail from "../components/grocery_components/GroceryDetail.tsx";
import useGroceryStore from "../store/useGroceryStore.ts";
import {useEffect} from "react";


function GroceryDetailPage() {
    const {getGroceryDetail, grocery, isLoading} = useGroceryStore();
    const {id} = useParams<{ id: string }>();

    useEffect(() => {
        if (id != null) {
            getGroceryDetail(id).then();
        }
    }, [id, getGroceryDetail]);

    if (grocery == null) {
        return;
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