import {useEffect, useState} from "react";
import {useParams, useNavigate} from "react-router-dom";
import {Container, Typography} from '@mui/material';
import useGroceryStore from "../store/useGroceryStore.ts";
import MonthlyGroceryAppError from "../components/common/MonthlyGroceryAppError.tsx";
import MonthlyGroceryAppLoader from "../components/common/MonthlyGroceryAppLoader.tsx";
import GroceryUpdate from "../components/grocery_components/GroceryUpdateForm.tsx";
import type {IPayloadGroceryItemUpdate} from "../api/types/requests/UpdateGroceryItem.ts";
import PATHS from "../constants/paths.ts";

function UpdateGroceryPage() {
    const {getGroceryDetail, updateGroceryDetail, grocery, isLoading, error} = useGroceryStore();
    const {id} = useParams<{ id: string }>();
    const navigate = useNavigate();

    // 1. Initialize as null.
    const [formData, setFormData] = useState<IPayloadGroceryItemUpdate | null>(null);

    // 2. Fetch data from API on mount
    useEffect(() => {
        if (id) {
            getGroceryDetail(id).then();
        }
    }, [id, getGroceryDetail]);

    // 3. IMPORTANT: Sync the store data to local form state once it arrives
    useEffect(() => {
        if (grocery) {
            setFormData(grocery);
        }
    }, [grocery]);

    const navigateToBack = () => {
        navigate(PATHS.HOME);
    };

    const handleSave = async () => {
        if (id && formData) {
            console.log(formData)
            await updateGroceryDetail(id, formData);
        }
        navigateToBack();
    };

    // Curried handlers with Null-Checks to satisfy TypeScript
    const handleStringChange = (field: keyof IPayloadGroceryItemUpdate) => (value: string) => {
        setFormData(prev => {
            if (!prev) return null;
            return {...prev, [field]: value};
        });
    };

    const handleNumberChange = (field: keyof IPayloadGroceryItemUpdate) => (value: string) => {
        setFormData(prev => {
            if (!prev) return null;
            // Use 'as any' to bypass strict dynamic key check if necessary
            return {...prev, [field]: (Number(value) || 0)};
        });
    };

    // Logic: If there is an error, show it
    if (error) {
        return (
            <Container sx={{py: 4}}>
                <Typography variant="h4" sx={{mb: 2}}>Monthly Grocery Update Page</Typography>
                <MonthlyGroceryAppError message={error}/>
            </Container>
        );
    }

    // Logic: If loading OR state hasn't been synced yet, show loader
    if (isLoading || !formData) {
        return (
            <Container sx={{py: 4}}>
                <Typography variant="h4" sx={{mb: 2}}>Monthly Grocery Update Page</Typography>
                <MonthlyGroceryAppLoader message="Fetching Details..."/>
            </Container>
        );
    }

    return (
        <Container sx={{py: 4}}>
            <Typography variant="h4" sx={{mb: 4, fontWeight: 'bold', textAlign: 'center'}}>
                Update Grocery Item
            </Typography>

            <GroceryUpdate
                formData={formData}
                onStringChange={handleStringChange}
                onNumberChange={handleNumberChange}
                handleSaveAction={handleSave}
                handleCancelAction={navigateToBack}
            />
        </Container>
    );
}

export default UpdateGroceryPage;