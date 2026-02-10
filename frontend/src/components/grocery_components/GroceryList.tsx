import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import {Chip} from "@mui/material";
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import {GroceryStockStatus} from "../../utils/enums.ts";
import '../../styles/GroceryList.css';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpwardRounded';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import {useEffect} from "react";
import useGroceryStore from "../../store/useGroceryStore.ts";


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
            <TableCell align="right">Seller</TableCell>
            <TableCell align="right">Threshold</TableCell>
            <TableCell align="right">Stock</TableCell>
            <TableCell align="right">Include?</TableCell>
            <TableCell align="right">Best Price</TableCell>
            <TableCell align="right">Best Seller</TableCell>
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
        <TableCell align="right">${row.current_price.toFixed(2)}</TableCell>
        <TableCell align="right">{row.current_seller}</TableCell>
        <TableCell align="right">{row.low_stock_threshold}</TableCell>
        <TableCell align="right">{row.quantity_in_stock}</TableCell>
        <TableCell align="right">{row.should_include}</TableCell>
        <TableCell align="right">${row.best_price.toFixed(2)}</TableCell>
        <TableCell align="right">{row.best_seller}</TableCell>
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

function GroceryTable() {

    const {groceries, fetchGroceries} = useGroceryStore();
    useEffect(() => {
        fetchGroceries().then();
    }, [fetchGroceries]);


    return (
        <Paper elevation={10} sx={{borderRadius: 1, overflow: 'hidden'}}>
            <TableContainer>
                <Table sx={{minWidth: 650}} aria-label="grocery inventory table">
                    <GroceryTableHeader></GroceryTableHeader>
                    <TableBody>
                        {groceries.map((row, index) => (
                            <GroceryTableRow row={row} index={index}></GroceryTableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
}

export default GroceryTable;
