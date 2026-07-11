import {useEffect, useState} from "react";
import {useNavigate} from 'react-router-dom';
import {Typography} from '@mui/material';
import GroceryTable from "../components/grocery_components/GroceryList.tsx";
import GroceryFilterBar from "../components/grocery_components/GroceryFilterBar.tsx";
import Box from "@mui/material/Box";
import {MonthlyGroceryAppAddButton, MonthlyGroceryAppIncludeSelectedButton} from "../components/common/MonthlyGroceryAppButton.tsx";
import PATHS from "../constants/paths.ts";
import useGroceryStore from "../store/useGroceryStore.ts";
import MonthlyGroceryAppLoader from "../components/common/MonthlyGroceryAppLoader.tsx";
import type {IGroceryFilterParams} from "../api/types/requests/grocery/GroceryFilterParams.ts";


function HomePage() {
    const navigate = useNavigate();

    // 1. Hook into the store at the Page level
    const {groceries, fetchGroceries, isLoading, deleteGroceryItem, bulkUpdateShouldIncludeItems} = useGroceryStore();
    const [filters, setFilters] = useState<IGroceryFilterParams>({});
    const [selectedIds, setSelectedIds] = useState<string[]>([]);

    // 2. Trigger the fetch when the page mounts or filters change
    useEffect(() => {
        fetchGroceries(filters).then();
    }, [fetchGroceries, filters]);

    // Selections are tied to the currently visible rows, so drop them when filters change
    useEffect(() => {
        setSelectedIds([]);
    }, [filters]);

    const handleSave = () => {
        navigate(PATHS.ADD_GROCERY);
    };
    const handleOnViewAction = (grocery_id: string) => {
        navigate(PATHS.DETAIL_GROCERY.replace(':id', grocery_id));
    };
    const handleOnEditAction = (grocery_id: string) => {
        navigate(PATHS.EDIT_GROCERY.replace(':id', grocery_id));
    };
    const handleOnDeleteAction = async (grocery_id: string) => {
        await deleteGroceryItem(grocery_id);
    };
    const handleToggleSelect = (grocery_id: string) => {
        setSelectedIds((prev) =>
            prev.includes(grocery_id)
                ? prev.filter((id) => id !== grocery_id)
                : [...prev, grocery_id]
        );
    };
    const handleToggleSelectAll = (checked: boolean) => {
        setSelectedIds(checked ? groceries.map((item) => item.id) : []);
    };
    const handleIncludeSelected = async () => {
        await bulkUpdateShouldIncludeItems(selectedIds, true);
        setSelectedIds([]);
    };


    return (
        <Box>
            {/* Header Row Container */}
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center', // Centers the Typography
                    position: 'relative',    // Allows button to be positioned absolutely
                    mb: 4                    // Spacing below the header
                }}
            >
                {/* 1. The Title (Centered) */}
                <Typography variant="h4" sx={{fontWeight: 'bold'}}>
                    Monthly Grocery List
                </Typography>

                {/* 2. The Button (Pushed to Right) */}
                <Box sx={{position: 'absolute', right: 0}}>
                    <MonthlyGroceryAppAddButton onClick={handleSave}/>
                </Box>
            </Box>
            <GroceryFilterBar onFilterChange={setFilters}/>
            {selectedIds.length > 0 && (
                <Box sx={{display: 'flex', justifyContent: 'flex-end', mb: 2}}>
                    <MonthlyGroceryAppIncludeSelectedButton
                        onClick={handleIncludeSelected}
                        disabled={isLoading}
                        count={selectedIds.length}
                    />
                </Box>
            )}
            {isLoading || !groceries ? (
                <MonthlyGroceryAppLoader message="Fetching list..."/>
            ) : (
                <GroceryTable
                    groceries={groceries}
                    onView={handleOnViewAction}
                    onEdit={handleOnEditAction}
                    onDelete={handleOnDeleteAction}
                    selectedIds={selectedIds}
                    onToggleSelect={handleToggleSelect}
                    onToggleSelectAll={handleToggleSelectAll}>
                </GroceryTable>
            )}
        </Box>
    );
}

export default HomePage;