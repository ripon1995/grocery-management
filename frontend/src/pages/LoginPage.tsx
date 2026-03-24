import {useNavigate} from 'react-router-dom';
import {useEffect, useState} from "react";
import {Container, Typography} from '@mui/material';
import PATHS from "../constants/paths.ts";
import UserLoginForm from "../components/auth_components/UserLoginForm.tsx";
import type {IUserLoginPayload} from "../api/types/requests/auth/UserLoginPayload.ts";
import useAuthStore from "../store/useAuthStore.ts";
import MonthlyGroceryAppError from "../components/common/MonthlyGroceryAppError.tsx";

const INITIAL_LOGIN_STATE: IUserLoginPayload = {
    email: '',
    password: '',
};


function UserLoginPage() {

    const navigate = useNavigate();
    const {login, error, resetError} = useAuthStore();

    useEffect(() => {
        resetError();
    }, [resetError]);

    // Initial state for all fields
    const [formData, setFormData] = useState<IUserLoginPayload>(INITIAL_LOGIN_STATE);

    // Handle string inputs (name, brand)
    const handleStringChange = (field: keyof IUserLoginPayload) => (value: string) => {
        setFormData(prev => ({...prev, [field]: value}));
    };

    const handleLogin = async () => {
        await login(formData)
    };

    const handleCancelAction = async () => {
        navigateToBack();
    };

    const navigateToBack = () => {
        navigate(PATHS.HOME);
    };

    // 1. If there's an error and no grocery data, show Error
    if (error) {
        return (
            <Container>
                <Typography variant="h4" sx={{mb: 2}}>Monthly Grocery Detail</Typography>
                <MonthlyGroceryAppError message={error}/>
            </Container>
        );
    }


    return (
        <Container>
            <Typography variant="h4">Welcome Back!</Typography>
            <UserLoginForm
                formData={formData}
                onStringChange={handleStringChange}
                handleLoginAction={handleLogin}
                handleCancelAction={handleCancelAction}>
            </UserLoginForm>
        </Container>
    );
}

export default UserLoginPage;