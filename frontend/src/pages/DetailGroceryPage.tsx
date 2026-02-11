import {Container, Typography} from '@mui/material';
import {useParams} from "react-router-dom";
import GroceryDetail from "../components/grocery_components/GroceryDetail.tsx";
import {GroceryStockStatus, GroceryType, Seller} from "../constants/enums.ts";


const DUMMY_GROCERY = {
    id: "groc-001",
    name: "Organic Whole Milk",
    brand: "DairyPure",
    type: GroceryType.CAN,
    current_price: 4.99,
    current_seller: Seller.MEENA,
    low_stock_threshold: 2,
    quantity_in_stock: 5,
    should_include: true,
    best_price: 4.50,
    best_seller: Seller.SHWAPNO,
    stock_status: GroceryStockStatus.IN_STOCK,
    created_at: new Date("2023-10-01T08:00:00Z"),
    updated_at: new Date("2024-02-10T14:30:00Z"),
};


function GroceryDetailPage() {
    const {id} = useParams<{ id: string }>();
    return (
        <Container>
            <Typography variant="h4" sx={{fontWeight: 'regular'}}>
                Monthly Grocery Detail
            </Typography>
            <GroceryDetail grocery={DUMMY_GROCERY}></GroceryDetail>
        </Container>

    );
}

export default GroceryDetailPage;