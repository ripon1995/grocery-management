import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import MonthlyGroceryAppInputField from "../common/MonthlyGroceryAppInputField.tsx";
import {MonthlyGroceryAppSaveButton} from "../common/MonthlyGroceryAppButton.tsx";
import {MonthlyGroceryAppCancelButton} from "../common/MonthlyGroceryAppButton.tsx";
import Stack from "@mui/material/Stack";
import type {IGroceryCreateItem} from "../../api/types/requests/CreateGroceryItem.ts";
import {GroceryType, Seller} from "../../constants/enums.ts";
import MonthlyGroceryAppSelectField from "../common/MonthlyGroceryAppSelectField.tsx";


interface IGroceryFormProps {
    formData: IGroceryCreateItem;
    onStringChange: (field: keyof IGroceryCreateItem) => (value: string) => void;
    onNumberChange: (field: keyof IGroceryCreateItem) => (value: string) => void;
    handleSaveAction: () => void;
    handleCancelAction: () => void;
}


function GroceryCreateForm(
    {
        formData,
        onStringChange,
        onNumberChange,
        handleSaveAction,
        handleCancelAction,
    }: IGroceryFormProps
) {


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
                borderRadius: 1,
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
                    onChange={onStringChange('name')}>
                </MonthlyGroceryAppInputField>
                <MonthlyGroceryAppInputField
                    label='Brand'
                    value={formData.brand}
                    onChange={onStringChange('brand')}
                />
                <MonthlyGroceryAppSelectField
                    label='Type'
                    value={formData.type}
                    options={Object.values(GroceryType)}
                    onChange={onStringChange('type')}
                />

                <MonthlyGroceryAppInputField
                    label='Current Price'
                    value={formData.current_price.toString()}
                    onChange={onNumberChange('current_price')}
                />
                <MonthlyGroceryAppSelectField
                    label='Current Seller'
                    value={formData.current_seller}
                    options={Object.values(Seller)}
                    onChange={onStringChange('current_seller')}
                />
                <MonthlyGroceryAppInputField
                    label='Low Stock Threshold'
                    value={formData.low_stock_threshold.toString()}
                    onChange={onNumberChange('low_stock_threshold')}
                />
                <MonthlyGroceryAppInputField
                    label='Quantity in stock'
                    value={formData.quantity_in_stock.toString()}
                    onChange={onNumberChange('quantity_in_stock')}
                />
                <Stack
                    direction="row"
                    spacing={40}
                    sx={{mt: 4, width: '100%', justifyContent: 'center'}}
                >
                    <MonthlyGroceryAppSaveButton onClick={handleSaveAction}></MonthlyGroceryAppSaveButton>
                    <MonthlyGroceryAppCancelButton onClick={handleCancelAction}></MonthlyGroceryAppCancelButton>
                </Stack>
            </Paper>
        </Box>
    );
}


export default GroceryCreateForm;