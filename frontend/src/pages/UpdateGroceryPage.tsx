import {Container, Typography} from '@mui/material';
import {useParams} from "react-router-dom";

function UpdateGroceryPage() {
    const {id} = useParams<{ id: string }>();
    return (
        <Container>
            <Typography variant="h4">Welcome to the Grocery Edit Page</Typography>
            <p>Grocery id : {id}</p>
        </Container>
    );
}

export default UpdateGroceryPage;