import type {IGroceryDetail} from "../../types/IGroceryDetail.ts";
import {Box} from '@mui/material';
import {Paper} from '@mui/material';
import {formatDate} from "../../constants/utils.ts";
import MonthlyGroceryAppDisplayField from "../common/MonthlyGroceryAppDiplayField.tsx";


// 2. Function for the Data View
const renderGroceryContent = (data: IGroceryDetail) => (
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
        <MonthlyGroceryAppDisplayField label="Name" value={data.name}/>
        <MonthlyGroceryAppDisplayField label="Brand" value={data.brand}/>
        <MonthlyGroceryAppDisplayField label="Type" value={data.type.toUpperCase()}/>
        <MonthlyGroceryAppDisplayField label="Current Price" value={`$${data.current_price.toFixed(2)}`}/>
        <MonthlyGroceryAppDisplayField label="Current Seller" value={data.current_seller.toUpperCase()}/>
        <MonthlyGroceryAppDisplayField label="Low Stock Threshold" value={data.low_stock_threshold}/>
        <MonthlyGroceryAppDisplayField label="Quantity In Stock" value={data.quantity_in_stock}/>
        <MonthlyGroceryAppDisplayField label="Include?" value={data.should_include ? 'YES' : 'NO'}/>
        <MonthlyGroceryAppDisplayField label="Best Seller" value={data.best_seller.toUpperCase()}/>
        <MonthlyGroceryAppDisplayField label="Best Price" value={`$${data.best_price.toFixed(2)}`}/>
        <MonthlyGroceryAppDisplayField label="Stock Status" value={data.stock_status.toUpperCase()}/>
        <MonthlyGroceryAppDisplayField label="Created At" value={formatDate(data.created_at)}/>
        <MonthlyGroceryAppDisplayField label="Updated At" value={formatDate(data.updated_at)}/>
    </Paper>
);


interface IGroceryDetailProps {
    grocery: IGroceryDetail
    isLoading: boolean
}


function GroceryDetail(props: IGroceryDetailProps) {
    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'center', // Centers the Paper horizontally in the screen
                alignItems: 'flex-start',     // Centers the Paper vertically in the screen
                minHeight: '100vh',       // Ensures the box takes full screen heigh
                pt: 4
            }}
        >

            {renderGroceryContent(props.grocery)}

        </Box>
    );
}

export default GroceryDetail;