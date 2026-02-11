import {useNavigate} from 'react-router-dom';
import {Container, Typography} from '@mui/material';
import CreateGroceryForm from "../components/grocery_components/CreateGroceryForm.tsx";
import PATHS from "../constants/paths.ts";

function AddGroceryPage() {

    const navigate = useNavigate();

    const navigateToBack = () => {
        navigate(PATHS.HOME);
    };

    return (
        <Container>
            <Typography variant="h4">Let's add a new Grocery!</Typography>
            <CreateGroceryForm></CreateGroceryForm>
        </Container>
    );
}

export default AddGroceryPage;