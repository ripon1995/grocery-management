import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import MonthlyGroceryAppInputField from "../common/MonthlyGroceryAppInputField.tsx";
import {MonthlyGroceryAppSaveButton} from "../common/MonthlyGroceryAppButton.tsx";
import {MonthlyGroceryAppCancelButton} from "../common/MonthlyGroceryAppButton.tsx";
import Stack from "@mui/material/Stack";
import {useState} from "react";

function GroceryCreateForm() {

    // Initial state for all fields
    const [formData, setFormData] = useState({
        name: '',
        brand: '',
        type: '',
        price: '',
        seller: '',
        threshold: '',
        stock: ''
    });

    // Helper to update specific fields
    const handleChange = (field: string) => (value: string) => {
        setFormData((prev) => ({...prev, [field]: value}));
    };

    const handleSave = () => {
        console.log("Saving Grocery Data:", formData);
        // You can now see all values in your console!
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
                height: 700,
                gap: 1,                   // Adds consistent spacing between inputs
                p: 4                       // Add padding so items don't touch edges
            }}>
                <MonthlyGroceryAppInputField
                    label={'Name'}
                    value={formData.name}
                    onChange={handleChange('name')}>
                </MonthlyGroceryAppInputField>
                <MonthlyGroceryAppInputField
                    label='Brand'
                    value={formData.brand}
                    onChange={handleChange('brand')}
                />
                <MonthlyGroceryAppInputField
                    label='Type'
                    value={formData.type}
                    onChange={handleChange('type')}
                />
                <MonthlyGroceryAppInputField
                    label='Current Price'
                    value={formData.price}
                    onChange={handleChange('price')}
                />
                <MonthlyGroceryAppInputField
                    label='Current Seller'
                    value={formData.seller}
                    onChange={handleChange('seller')}
                />
                <MonthlyGroceryAppInputField
                    label='Low Stock Threshold'
                    value={formData.threshold}
                    onChange={handleChange('threshold')}
                />
                <MonthlyGroceryAppInputField
                    label='Quantity in stock'
                    value={formData.stock}
                    onChange={handleChange('stock')}
                />
                <Stack
                    direction="row"
                    spacing={40}
                    sx={{mt: 4, width: '100%', justifyContent: 'center'}}
                >
                    <MonthlyGroceryAppSaveButton onClick={handleSave}></MonthlyGroceryAppSaveButton>
                    <MonthlyGroceryAppCancelButton onClick={() => setFormData({
                        name: '',
                        brand: '',
                        type: '',
                        price: '',
                        seller: '',
                        threshold: '',
                        stock: ''
                    })}/>
                </Stack>
            </Paper>
        </Box>
    );
}


export default GroceryCreateForm;