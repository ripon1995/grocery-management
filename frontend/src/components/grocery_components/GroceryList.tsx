import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import {Chip} from "@mui/material";
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import {GroceryStockStatus} from "../../constants/enums.ts";
import '../../styles/GroceryList.css';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpwardRounded';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import MonthlyGroceryAppLoader from "../common/MonthlyGroceryAppLoader.tsx";


const GroceryTableHeader = () => (
    <TableHead className="grocery-header">
        <TableRow sx={{
            backgroundColor: 'purple', '& .MuiTableCell-head': {
                color: 'white',
                fontWeight: 'bold'
            }
        }}>
            <TableCell sx={{fontWeight: 'bold'}}>SL</TableCell>
            <TableCell sx={{fontWeight: 'bold'}}>Name</TableCell>
            <TableCell>Brand</TableCell>
            <TableCell align="center">Type</TableCell>
            <TableCell align="center">Price</TableCell>
            <TableCell align="center">Seller</TableCell>
            <TableCell align="center">Threshold</TableCell>
            <TableCell align="center">Stock</TableCell>
            <TableCell align="center">Include?</TableCell>
            <TableCell align="center">Best Price</TableCell>
            <TableCell align="center">Best Seller</TableCell>
            <TableCell align="center">Status</TableCell>
        </TableRow>
    </TableHead>
);

const GroceryTableRow = ({row, index}: { row: IGroceryListItem; index: number }) => (
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
        <TableCell align="center">${row.current_price.toFixed(2)}</TableCell>
        <TableCell align="center" sx={{textTransform: 'uppercase'}}>{row.current_seller}</TableCell>
        <TableCell align="center">{row.low_stock_threshold}</TableCell>
        <TableCell align="center">{row.quantity_in_stock}</TableCell>
        <TableCell align="center">
            {row.should_include}
            <Chip
                label={row.should_include ? 'YES' : 'NO'}
                color={row.should_include ? 'success' : 'error'}
                variant={"filled"}
                sx={{borderRadius: '2px'}}
            />
        </TableCell>
        <TableCell align="center">${row.best_price.toFixed(2)}</TableCell>
        <TableCell align="center" sx={{textTransform: 'uppercase'}}>{row.best_seller}</TableCell>
        <TableCell align="center">
            <Chip
                icon={
                    row.stock_status === GroceryStockStatus.IN_STOCK
                        ? <ArrowUpwardIcon sx={{fontSize: '15px !important'}}/>
                        : <ArrowDownwardIcon sx={{fontSize: '15px !important'}}/>
                }
                label={row.stock_status === GroceryStockStatus.IN_STOCK ? 'In Stock' : 'Low Stock'}
                color={row.stock_status === GroceryStockStatus.IN_STOCK ? 'success' : 'error'}
                variant="outlined"
            />
        </TableCell>
    </TableRow>
)


interface IGroceryTableProps {
    groceries: IGroceryListItem[];
    isLoading: boolean;
}

function GroceryTable({groceries, isLoading}: IGroceryTableProps) {
    return (
        <Paper elevation={10} sx={{borderRadius: 1, overflow: 'hidden'}}>
            <TableContainer>
                <Table sx={{minWidth: 650}} aria-label="grocery inventory table">
                    <GroceryTableHeader></GroceryTableHeader>
                    <TableBody>
                        {isLoading ? (
                            <TableRow>
                                <TableCell colSpan={12} sx={{p: 0, borderBottom: 'none'}}>
                                    <MonthlyGroceryAppLoader message="Fetching Groceries..." minHeight={500}/>
                                </TableCell>
                            </TableRow>

                        ) : (
                            groceries.map((row, index) => (
                                <GroceryTableRow key={row.id} row={row} index={index}/>
                            ))
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
}

export default GroceryTable;
