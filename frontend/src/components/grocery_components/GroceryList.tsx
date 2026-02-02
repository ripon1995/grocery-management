import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import {BestSeller, GroceryStockStatus, GroceryType} from "../../utils/enums.ts";
import {Chip} from "@mui/material";
import '../../styles/GroceryList.css';


const createGroceryListItem = (
    name: string,
    brand: string,
    type: GroceryType,
    price: number,
    required: number,
    stock: number,
    bestSeller: BestSeller
): IGroceryListItem => {
    return {
        id: Math.random().toString(36).substring(2, 12), // Random 10-char ID
        name,
        brand,
        type,
        current_price: price,
        quantity_required: required,
        low_stock_threshold: 5,
        quantity_in_stock: stock,
        best_price: price * 0.9, // Assuming best price is 10% lower
        best_seller: bestSeller,
        stock_status: stock <= 5 ? GroceryStockStatus.BELOW_STOCK : GroceryStockStatus.IN_STOCK,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
    };
};


const groceryRows: IGroceryListItem[] = [

    createGroceryListItem('Basmati Rice', 'Fortune', GroceryType.SACK, 1200, 2, 1, BestSeller.SHWAPNO),
    createGroceryListItem('Full Cream Milk', 'Arla', GroceryType.CAN, 95, 12, 24, BestSeller.MEENA),
    createGroceryListItem('Whole Wheat Flour', 'Aashirvaad', GroceryType.SACK, 550, 1, 0, BestSeller.LOCAL),
    createGroceryListItem('Greek Yogurt', 'Danone', GroceryType.PIECE, 120, 5, 8, BestSeller.MEENA),
    createGroceryListItem('Canned Tuna', 'John West', GroceryType.CAN, 210, 10, 15, BestSeller.SHWAPNO),
    createGroceryListItem('Potatoes', 'Local Farm', GroceryType.WEIGHT, 40, 5, 12, BestSeller.LOCAL),
    createGroceryListItem('Sugar', 'Fresh', GroceryType.WEIGHT, 110, 2, 4, BestSeller.COMILLA),
    createGroceryListItem('Lentils (Dal)', 'Teer', GroceryType.SACK, 140, 3, 10, BestSeller.SHWAPNO),
    createGroceryListItem('Eggs (Dozen)', 'Farm Egg', GroceryType.PIECE, 150, 4, 2, BestSeller.LOCAL),
    createGroceryListItem('Cooking Oil', 'Rupchanda', GroceryType.CAN, 185, 5, 20, BestSeller.MEENA),
];

function GroceryTable() {
    return (
        <Paper elevation={10} sx={{borderRadius: 1, overflow: 'hidden'}}>
            <TableContainer>
                <Table sx={{minWidth: 650}} aria-label="grocery inventory table">
                    <TableHead className="grocery-header">
                        <TableRow sx={{
                            backgroundColor: 'purple', '& .MuiTableCell-head': {
                                color: 'white',
                                fontWeight: 'bold'
                            }
                        }}>
                            <TableCell sx={{fontWeight: 'bold'}}>SL</TableCell>
                            <TableCell sx={{fontWeight: 'bold'}}>Item Name</TableCell>
                            <TableCell>Brand</TableCell>
                            <TableCell align="center">Type</TableCell>
                            <TableCell align="right">In Stock</TableCell>
                            <TableCell align="right">Required</TableCell>
                            <TableCell align="right">Current Price</TableCell>
                            <TableCell align="right">Best Price</TableCell>
                            <TableCell align="right">Best Seller</TableCell>
                            <TableCell align="right">Updated</TableCell>
                            <TableCell align="center">Status</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {groceryRows.map((row, index) => (
                            <TableRow
                                key={row.id}
                                className="grocery-row"
                                sx={{'&:last-child td, &:last-child th': {border: 0}}}
                            >
                                <TableCell component="th" scope="row" sx={{fontWeight: 500}}>
                                    {index + 1}
                                </TableCell>
                                <TableCell component="th" scope="row" sx={{fontWeight: 500}}>
                                    {row.name}
                                </TableCell>
                                <TableCell>{row.brand}</TableCell>
                                <TableCell align="center" sx={{textTransform: 'capitalize'}}>
                                    {row.type}
                                </TableCell>
                                <TableCell align="right">{row.quantity_in_stock}</TableCell>
                                <TableCell align="right">{row.quantity_required}</TableCell>
                                <TableCell align="right">${row.current_price.toFixed(2)}</TableCell>
                                <TableCell align="right">${row.best_price.toFixed(2)}</TableCell>
                                <TableCell align="right">{row.best_seller}</TableCell>
                                <TableCell align="right">{row.updated_at}</TableCell>
                                <TableCell align="center">
                                    <Chip
                                        label={row.stock_status === GroceryStockStatus.IN_STOCK ? 'In Stock' : 'Low Stock'}
                                        color={row.stock_status === GroceryStockStatus.IN_STOCK ? 'success' : 'error'}
                                        size="small"
                                        variant="outlined"
                                    />
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
}

export default GroceryTable;
