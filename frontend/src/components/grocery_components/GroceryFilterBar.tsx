import {useEffect, useState} from "react";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select, {type SelectChangeEvent} from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Button from "@mui/material/Button";
import {GroceryType, Seller, GroceryCategory} from "../../constants/enums.ts";
import type {IGroceryFilterParams} from "../../api/types/requests/grocery/GroceryFilterParams.ts";

const ALL = '';

interface IGroceryFilterBarProps {
    onFilterChange: (filters: IGroceryFilterParams) => void;
}

function GroceryFilterBar({onFilterChange}: IGroceryFilterBarProps) {
    const [search, setSearch] = useState('');
    const [type, setType] = useState<string>(ALL);
    const [currentSeller, setCurrentSeller] = useState<string>(ALL);
    const [bestSeller, setBestSeller] = useState<string>(ALL);
    const [category, setCategory] = useState<string>(ALL);
    const [shouldInclude, setShouldInclude] = useState<string>(ALL);

    // Debounce free-text search so it doesn't fire a request on every keystroke
    useEffect(() => {
        const handler = setTimeout(() => {
            emitFilters();
        }, 400);
        return () => clearTimeout(handler);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [search]);

    // Dropdown filters apply immediately
    useEffect(() => {
        emitFilters();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [type, currentSeller, bestSeller, category, shouldInclude]);

    const emitFilters = () => {
        const filters: IGroceryFilterParams = {};
        if (search.trim()) filters.search = search.trim();
        if (type) filters.type = type as GroceryType;
        if (currentSeller) filters.current_seller = currentSeller as Seller;
        if (bestSeller) filters.best_seller = bestSeller as Seller;
        if (category) filters.category = category as GroceryCategory;
        if (shouldInclude) filters.should_include = shouldInclude === 'yes';
        onFilterChange(filters);
    };

    const handleClear = () => {
        setSearch('');
        setType(ALL);
        setCurrentSeller(ALL);
        setBestSeller(ALL);
        setCategory(ALL);
        setShouldInclude(ALL);
    };

    return (
        <Box
            sx={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 2,
                alignItems: 'center',
                mb: 3,
            }}
        >
            <TextField
                label="Search"
                size="small"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                sx={{minWidth: 220}}
            />
            <FormControl size="small" sx={{minWidth: 140}}>
                <InputLabel id="filter-type-label">Type</InputLabel>
                <Select
                    labelId="filter-type-label"
                    label="Type"
                    value={type}
                    onChange={(e: SelectChangeEvent) => setType(e.target.value)}
                >
                    <MenuItem value={ALL}>All</MenuItem>
                    {Object.values(GroceryType).map((opt) => (
                        <MenuItem key={opt} value={opt}>{opt.toUpperCase()}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControl size="small" sx={{minWidth: 140}}>
                <InputLabel id="filter-category-label">Category</InputLabel>
                <Select
                    labelId="filter-category-label"
                    label="Category"
                    value={category}
                    onChange={(e: SelectChangeEvent) => setCategory(e.target.value)}
                >
                    <MenuItem value={ALL}>All</MenuItem>
                    {Object.values(GroceryCategory).map((opt) => (
                        <MenuItem key={opt} value={opt}>{opt.toUpperCase()}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControl size="small" sx={{minWidth: 160}}>
                <InputLabel id="filter-current-seller-label">Current Seller</InputLabel>
                <Select
                    labelId="filter-current-seller-label"
                    label="Current Seller"
                    value={currentSeller}
                    onChange={(e: SelectChangeEvent) => setCurrentSeller(e.target.value)}
                >
                    <MenuItem value={ALL}>All</MenuItem>
                    {Object.values(Seller).map((opt) => (
                        <MenuItem key={opt} value={opt}>{opt.toUpperCase()}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControl size="small" sx={{minWidth: 150}}>
                <InputLabel id="filter-best-seller-label">Best Seller</InputLabel>
                <Select
                    labelId="filter-best-seller-label"
                    label="Best Seller"
                    value={bestSeller}
                    onChange={(e: SelectChangeEvent) => setBestSeller(e.target.value)}
                >
                    <MenuItem value={ALL}>All</MenuItem>
                    {Object.values(Seller).map((opt) => (
                        <MenuItem key={opt} value={opt}>{opt.toUpperCase()}</MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControl size="small" sx={{minWidth: 120}}>
                <InputLabel id="filter-should-include-label">Include?</InputLabel>
                <Select
                    labelId="filter-should-include-label"
                    label="Include?"
                    value={shouldInclude}
                    onChange={(e: SelectChangeEvent) => setShouldInclude(e.target.value)}
                >
                    <MenuItem value={ALL}>All</MenuItem>
                    <MenuItem value="yes">YES</MenuItem>
                    <MenuItem value="no">NO</MenuItem>
                </Select>
            </FormControl>
            <Button variant="outlined" onClick={handleClear}>Clear Filters</Button>
        </Box>
    );
}

export default GroceryFilterBar;
