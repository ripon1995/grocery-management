import {Container, Typography} from '@mui/material';
import CreateGroceryForm from "../components/grocery_components/CreateGroceryForm.tsx";

function AddGrocery() {
    return (
        <Container>
            <Typography variant="h3">Let's add a new Grocery!</Typography>
            <CreateGroceryForm></CreateGroceryForm>
        </Container>
    );
}

export default AddGrocery;