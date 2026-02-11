import {useNavigate} from 'react-router-dom';
import {useState} from "react";
import {Container, Typography} from '@mui/material';
import CreateGroceryForm from "../components/grocery_components/CreateGroceryForm.tsx";
import PATHS from "../constants/paths.ts";
import type {IGroceryCreateItem} from "../api/types/requests/CreateGroceryItem.ts";
import {GroceryType, Seller} from "../constants/enums.ts";

const INITIAL_GROCERY_STATE: IGroceryCreateItem = {
    name: '',
    brand: '',
    type: GroceryType.CAN,
    current_price: 0,
    current_seller: Seller.MEENA,
    low_stock_threshold: 2,
    quantity_in_stock: 0
};


function AddGroceryPage() {

    const navigate = useNavigate();

    // Initial state for all fields
    const [formData, setFormData] = useState<IGroceryCreateItem>(INITIAL_GROCERY_STATE);

    // Handle string inputs (name, brand)
    const handleStringChange = (field: keyof IGroceryCreateItem) => (value: string) => {
        setFormData(prev => ({...prev, [field]: value}));
    };

    // Handle number inputs (price, threshold, stock)
    const handleNumberChange = (field: keyof IGroceryCreateItem) => (value: string) => {
        setFormData(prev => ({...prev, [field]: Number(value) || 0}));
    };

    const handleSave = () => {
        console.log("Saving Grocery Data:", formData);
        // You can now see all values in your console!
    };

    const navigateToBack = () => {
        navigate(PATHS.HOME);
    };

    return (
        <Container>
            <Typography variant="h4">Let's add a new Grocery!</Typography>
            <CreateGroceryForm
                formData={formData}
                onStringChange={handleStringChange}
                onNumberChange={handleNumberChange}
                handleSaveAction={handleSave}
                handleCancelAction={navigateToBack}>
            </CreateGroceryForm>
        </Container>
    );
}

export default AddGroceryPage;