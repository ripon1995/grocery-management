import type {IGroceryDetail} from "../../types/IGroceryDetail.ts";
import {Box} from '@mui/material';
import {Paper} from '@mui/material';
import {formatDate} from "../../constants/utils.ts";
import MonthlyGroceryAppDisplayField from "../common/MonthlyGroceryAppDiplayField.tsx";

interface IGroceryDetailProps {
    grocery: IGroceryDetail
}

function GroceryDetail(props: IGroceryDetailProps) {
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
                <MonthlyGroceryAppDisplayField
                    label={"Name"}
                    value={props.grocery.name}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Brand"}
                    value={props.grocery.brand}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Type"}
                    value={props.grocery.type.toUpperCase()}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Current Price"}
                    value={props.grocery.current_price.toFixed(2)}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Current Seller"}
                    value={props.grocery.current_seller.toUpperCase()}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Low Stock Threshold"}
                    value={props.grocery.low_stock_threshold}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Quantity In Stock"}
                    value={props.grocery.quantity_in_stock}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Include?"}
                    value={props.grocery.should_include ? 'YES' : 'NO'}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Best Seller"}
                    value={props.grocery.best_seller.toUpperCase()}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Best Price"}
                    value={props.grocery.best_price.toFixed(2)}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Stock Status"}
                    value={props.grocery.stock_status.toUpperCase()}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Created At"}
                    value={formatDate(props.grocery.created_at)}>
                </MonthlyGroceryAppDisplayField>
                <MonthlyGroceryAppDisplayField
                    label={"Updated At"}
                    value={formatDate(props.grocery.updated_at)}>
                </MonthlyGroceryAppDisplayField>

            </Paper>

        </Box>
    );
}

export default GroceryDetail;