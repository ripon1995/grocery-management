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
import {Checkbox, Chip, IconButton, Tooltip} from "@mui/material";
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
    selectedIds: string[];
    onToggleSelect: (grocery_id: string) => void;
    onToggleSelectAll: (checked: boolean) => void;
}


const GroceryTableHeader = ({allSelected, someSelected, onToggleSelectAll}: {
    allSelected: boolean;
    someSelected: boolean;
    onToggleSelectAll: (checked: boolean) => void;
}) => (
    <TableHead className="grocery-header">
        <TableRow sx={{
            backgroundColor: 'purple', '& .MuiTableCell-head': {
                color: 'white',
                fontWeight: 'bold'
            }
        }}>
            <TableCell padding="checkbox">
                <Checkbox
                    sx={{color: 'white'}}
                    checked={allSelected}
                    indeterminate={someSelected && !allSelected}
                    onChange={(e) => onToggleSelectAll(e.target.checked)}
                />
            </TableCell>
            <TableCell sx={{fontWeight: 'bold'}}>SL</TableCell>
            <TableCell sx={{fontWeight: 'bold'}}>Name</TableCell>
            <TableCell>Brand</TableCell>
            <TableCell align="center">Type</TableCell>
            <TableCell align="center">Price</TableCell>
            <TableCell align="center">Seller</TableCell>
            <TableCell align="center">Category</TableCell>
            <TableCell align="center">Stock</TableCell>
            <TableCell align="center">Include?</TableCell>
            <TableCell align="center">Best Price</TableCell>
            <TableCell align="center">Best Seller</TableCell>
            <TableCell align="center">Status</TableCell>
            <TableCell align="center">Actions</TableCell>
        </TableRow>
    </TableHead>
);


const GroceryTableRow = ({row, index, onView, onEdit, onDelete, selected, onToggleSelect}: {
    row: IGroceryListItem;
    index: number,
    onView: (grocery_id: string) => void;
    onEdit: (grocery_id: string) => void;
    onDelete: (grocery_id: string) => void;
    selected: boolean;
    onToggleSelect: (grocery_id: string) => void;
}) => (
    <TableRow
        key={row.id}
        className="grocery-row"
        selected={selected}
        sx={{'&:last-child td, &:last-child th': {border: 0}}}
    >
        <TableCell padding="checkbox">
            <Checkbox
                checked={selected}
                onChange={() => onToggleSelect(row.id)}
            />
        </TableCell>
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
        <TableCell align="center" sx={{textTransform: 'capitalize'}}>{row.category}</TableCell>
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


function GroceryTable({groceries, onView, onEdit, onDelete, selectedIds, onToggleSelect, onToggleSelectAll}: IGroceryTableProps) {
    const allSelected = groceries.length > 0 && groceries.every((row) => selectedIds.includes(row.id));
    const someSelected = groceries.some((row) => selectedIds.includes(row.id));

    return (
        <Paper elevation={10} sx={{borderRadius: 1, overflow: 'hidden'}}>
            <TableContainer>
                <Table sx={{minWidth: 650}} aria-label="grocery inventory table">
                    <GroceryTableHeader
                        allSelected={allSelected}
                        someSelected={someSelected}
                        onToggleSelectAll={onToggleSelectAll}
                    />
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
                                    selected={selectedIds.includes(row.id)}
                                    onToggleSelect={onToggleSelect}
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
