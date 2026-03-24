import {useNavigate} from 'react-router-dom';
import {useState} from "react";
import {Container, Typography} from '@mui/material';
import PATHS from "../constants/paths.ts";
import UserLoginForm from "../components/auth_components/UserLoginForm.tsx";
import type {IUserLoginPayload} from "../api/types/requests/auth/UserLoginPayload.ts";
import useAuthStore from "../store/useAuthStore.ts";

const INITIAL_LOGIN_STATE: IUserLoginPayload = {
    email: '',
    password: '',
};


function UserLoginPage() {

    const navigate = useNavigate();
    const {login} = useAuthStore();

    // Initial state for all fields
    const [formData, setFormData] = useState<IUserLoginPayload>(INITIAL_LOGIN_STATE);

    // Handle string inputs (name, brand)
    const handleStringChange = (field: keyof IUserLoginPayload) => (value: string) => {
        setFormData(prev => ({...prev, [field]: value}));
    };

    const handleLogin = async () => {
        await login(formData)
        navigateToBack();
    };

    // TODO -> Add later
    const handleRegistration = async () => {
        // await addGroceries(formData)
        navigateToBack();
    };

    const navigateToBack = () => {
        navigate(PATHS.HOME);
    };


    return (
        <Container>
            <Typography variant="h4">Welcome Back!</Typography>
            <UserLoginForm
                formData={formData}
                onStringChange={handleStringChange}
                handleLoginAction={handleLogin}
                handleRegisterAction={handleRegistration}>
            </UserLoginForm>
        </Container>
    );
}

export default UserLoginPage;