import {Box, Paper} from '@mui/material';
import Stack from "@mui/material/Stack";
import {MonthlyGroceryAppCancelButton, MonthlyGroceryAppSaveButton} from "../common/MonthlyGroceryAppButton.tsx";
import type {IPayloadGroceryItemUpdate} from "../../api/types/requests/UpdateGroceryItem.ts";
import MonthlyGroceryAppInputFieldSmall from "../common/MonthlyGroceryAppInputFieldSmall.tsx";
import MonthlyGroceryAppSelectFieldSmall from "../common/MonthlyGroceryAppSelectFieldSmall.tsx";
import {GroceryType, Seller} from "../../constants/enums.ts";


interface IGroceryUpdateProps {
    formData: IPayloadGroceryItemUpdate
    onStringChange: (field: keyof IPayloadGroceryItemUpdate) => (value: string) => void;
    onNumberChange: (field: keyof IPayloadGroceryItemUpdate) => (value: string) => void;
    handleSaveAction: () => void;
    handleCancelAction: () => void;
}


const renderGroceryContent = (
    formData: IPayloadGroceryItemUpdate,
    onStringChange: (field: keyof IPayloadGroceryItemUpdate) => (value: string) => void,
    onNumberChange: (field: keyof IPayloadGroceryItemUpdate) => (value: string) => void,
    handleSaveAction: () => void,
    handleCancelAction: () => void,
) => (
    <Paper elevation={6} sx={{
        borderRadius: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: 900,
        height: 'auto',
        gap: 1,
        p: 4
    }}>
        <MonthlyGroceryAppInputFieldSmall
            label={'Name'}
            value={formData.name}
            onChange={onStringChange('name')}
        />
        <MonthlyGroceryAppInputFieldSmall
            label="Brand"
            value={formData.brand}
            onChange={onStringChange('brand')}
        />
        <MonthlyGroceryAppSelectFieldSmall
            options={Object.values(GroceryType)}
            label="Type"
            value={formData.type}
            onChange={onStringChange('type')}
        />
        <MonthlyGroceryAppInputFieldSmall
            onChange={onNumberChange('current_price')}
            label="Current Price"
            value={`$${formData.current_price.toFixed(0)}`}
        />
        <MonthlyGroceryAppSelectFieldSmall
            options={Object.values(Seller)}
            onChange={onStringChange('current_seller')}
            label="Current Seller"
            value={formData.current_seller}
        />
        <MonthlyGroceryAppInputFieldSmall
            onChange={onNumberChange('low_stock_threshold')}
            label="Low Stock Threshold"
            value={formData.low_stock_threshold}
        />
        <MonthlyGroceryAppInputFieldSmall
            onChange={onNumberChange('quantity_in_stock')}
            label="Quantity In Stock"
            value={formData.quantity_in_stock}
        />
        <MonthlyGroceryAppInputFieldSmall
            onChange={onNumberChange('should_include')}
            label="Include?"
            value={formData.should_include ? 'YES' : 'NO'}
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
);


function GroceryUpdate(props: IGroceryUpdateProps) {
    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'flex-start',
                minHeight: '100vh',
                pt: 4
            }}
        >

            {renderGroceryContent(props.formData, props.onStringChange, props.onNumberChange, props.handleSaveAction, props.handleCancelAction)}

        </Box>
    );
}

export default GroceryUpdate;