import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import {Chip, IconButton, Tooltip} from "@mui/material";
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import {GroceryStockStatus} from "../../constants/enums.ts";
import '../../styles/GroceryList.css';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpwardRounded';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import Stack from "@mui/material/Stack";


interface IGroceryTableProps {
    groceries: IGroceryListItem[];
    onView: (grocery_id: string) => void;
    onEdit: (grocery_id: string) => void;
    onDelete: (grocery_id: string) => void;
}


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
            <TableCell align="center">Actions</TableCell>
        </TableRow>
    </TableHead>
);


const GroceryTableRow = ({row, index, onView, onEdit, onDelete}: {
    row: IGroceryListItem;
    index: number,
    onView: (grocery_id: string) => void;
    onEdit: (grocery_id: string) => void;
    onDelete: (grocery_id: string) => void;
}) => (
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
        <TableCell align="center">{row.current_price.toFixed(0)} BDT</TableCell>
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
        <TableCell align="center">{row.best_price.toFixed(0)} BDT</TableCell>
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
        <TableCell align="center">
            <Stack direction="row" spacing={1} justifyContent="center">
                <Tooltip title="View">
                    <IconButton onClick={() => onView(row.id)} color="primary" size="small">
                        <VisibilityIcon fontSize="small"/>
                    </IconButton>
                </Tooltip>
                <Tooltip title="Edit">
                    <IconButton onClick={() => onEdit(row.id)} color="info" size="small">
                        <EditIcon fontSize="small"/>
                    </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                    <IconButton onClick={() => onDelete(row.id)} color="error" size="small">
                        <DeleteIcon fontSize="small"/>
                    </IconButton>
                </Tooltip>
            </Stack>
        </TableCell>
    </TableRow>
)


function GroceryTable({groceries, onView, onEdit, onDelete}: IGroceryTableProps) {
    return (
        <Paper elevation={10} sx={{borderRadius: 1, overflow: 'hidden'}}>
            <TableContainer>
                <Table sx={{minWidth: 650}} aria-label="grocery inventory table">
                    <GroceryTableHeader></GroceryTableHeader>
                    <TableBody>
                        {(
                            groceries.map((row, index) => (
                                <GroceryTableRow
                                    key={row.id}
                                    row={row}
                                    index={index}
                                    onView={onView}
                                    onEdit={onEdit}
                                    onDelete={onDelete}
                                />
                            ))
                        )}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
}

export default GroceryTable;
