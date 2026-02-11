import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import MonthlyGroceryAppInputField from "../common/MonthlyGroceryAppInputField.tsx";
import {MonthlyGroceryAppSaveButton} from "../common/MonthlyGroceryAppButton.tsx";
import {MonthlyGroceryAppCancelButton} from "../common/MonthlyGroceryAppButton.tsx";
import Stack from "@mui/material/Stack";
import {useState} from "react";
import type {IGroceryCreateItem} from "../../api/types/requests/CreateGroceryItem.ts";
import {GroceryType, Seller} from "../../constants/enums.ts";
import MonthlyGroceryAppSelectField from "../common/MonthlyGroceryAppSelectField.tsx";

const INITIAL_GROCERY_STATE: IGroceryCreateItem = {
    name: '',
    brand: '',
    type: GroceryType.CAN,
    current_price: 0,
    current_seller: Seller.MEENA,
    low_stock_threshold: 2,
    quantity_in_stock: 0
};


function GroceryCreateForm() {
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
    const handleReset = () => {
        setFormData(INITIAL_GROCERY_STATE); // Use the constant again here
    };


    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'center', // Centers the Paper horizontally in the screen
                alignItems: 'center',     // Centers the Paper vertically in the screen
                minHeight: '100vh',       // Ensures the box takes full screen heigh
            }}
        >
            <Paper elevation={6} sx={{
                borderRadius: 2,
                display: 'flex',           // Turn Paper into a flex container
                flexDirection: 'column',  // Stack children vertically
                alignItems: 'center',      // Center children horizontally
                // justifyContent: 'center', // Center children vertically inside the paper
                width: 900,
                height: 'auto',
                gap: 1,                   // Adds consistent spacing between inputs
                p: 4                       // Add padding so items don't touch edges
            }}>
                <MonthlyGroceryAppInputField
                    label={'Name'}
                    value={formData.name}
                    onChange={handleStringChange('name')}>
                </MonthlyGroceryAppInputField>
                <MonthlyGroceryAppInputField
                    label='Brand'
                    value={formData.brand}
                    onChange={handleStringChange('brand')}
                />
                <MonthlyGroceryAppSelectField
                    label='Type'
                    value={formData.type}
                    options={Object.values(GroceryType)}
                    onChange={handleStringChange('type')}
                />

                <MonthlyGroceryAppInputField
                    label='Current Price'
                    value={formData.current_price.toString()}
                    onChange={handleNumberChange('current_price')}
                />
                <MonthlyGroceryAppSelectField
                    label='Current Seller'
                    value={formData.current_seller}
                    options={Object.values(Seller)}
                    onChange={handleStringChange('current_seller')}
                />
                <MonthlyGroceryAppInputField
                    label='Low Stock Threshold'
                    value={formData.low_stock_threshold.toString()}
                    onChange={handleNumberChange('low_stock_threshold')}
                />
                <MonthlyGroceryAppInputField
                    label='Quantity in stock'
                    value={formData.quantity_in_stock.toString()}
                    onChange={handleNumberChange('quantity_in_stock')}
                />
                <Stack
                    direction="row"
                    spacing={40}
                    sx={{mt: 4, width: '100%', justifyContent: 'center'}}
                >
                    <MonthlyGroceryAppSaveButton onClick={handleSave}></MonthlyGroceryAppSaveButton>
                    <MonthlyGroceryAppCancelButton onClick={handleReset}></MonthlyGroceryAppCancelButton>
                </Stack>
            </Paper>
        </Box>
    );
}


export default GroceryCreateForm;