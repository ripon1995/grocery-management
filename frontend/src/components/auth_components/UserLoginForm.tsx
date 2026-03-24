import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import MonthlyGroceryAppInputField from "../common/MonthlyGroceryAppInputField.tsx";
import {MonthlyGroceryAppCancelButton, MonthlyGroceryAppLoginButton} from "../common/MonthlyGroceryAppButton.tsx";
import Stack from "@mui/material/Stack";
import type {IUserLoginPayload} from "../../api/types/requests/auth/UserLoginPayload.ts";


interface IUserLoginFormProps {
    formData: IUserLoginPayload;
    onStringChange: (field: keyof IUserLoginPayload) => (value: string) => void;
    handleLoginAction: () => void;
    handleCancelAction: () => void;
}


function UserLoginForm(
    {
        formData,
        onStringChange,
        handleLoginAction,
        handleCancelAction,
    }: IUserLoginFormProps
) {

    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'center', // Centers the Paper horizontally in the screen
                alignItems: 'center',     // Centers the Paper vertically in the screen
                minHeight: '50vh',       // Ensures the box takes full screen heigh
            }}
        >
            <Paper elevation={6} sx={{
                borderRadius: 1,
                display: 'flex',           // Turn Paper into a flex container
                flexDirection: 'column',  // Stack children vertically
                alignItems: 'center',      // Center children horizontally
                width: 900,
                height: 'auto',
                gap: 1,                   // Adds consistent spacing between inputs
                p: 4                       // Add padding so items don't touch edges
            }}>
                <MonthlyGroceryAppInputField
                    label={'Email'}
                    value={formData.email}
                    onChange={onStringChange('email')}>
                </MonthlyGroceryAppInputField>
                <MonthlyGroceryAppInputField
                    label='Password'
                    value={formData.password}
                    onChange={onStringChange('password')}
                />

                <Stack
                    direction="row"
                    spacing={40}
                    sx={{mt: 4, width: '100%', justifyContent: 'center'}}
                >
                    <MonthlyGroceryAppLoginButton onClick={handleLoginAction}></MonthlyGroceryAppLoginButton>
                    <MonthlyGroceryAppCancelButton onClick={handleCancelAction}></MonthlyGroceryAppCancelButton>
                </Stack>
            </Paper>
        </Box>
    );
}


export default UserLoginForm;