import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import {Divider} from "@mui/material";
import ShoppingCartSharpIcon from '@mui/icons-material/ShoppingCartSharp';
import Stack from "@mui/material/Stack";
import {MonthlyGroceryAppLoginButton} from "./MonthlyGroceryAppButton.tsx";
import PATHS from "../../constants/paths.ts";
import {useNavigate} from "react-router-dom";
import useAuthStore from "../../store/useAuthStore.ts"; // Import your store

function MonthlyGroceryAppBar() {

    const navigate = useNavigate();

    // 1. Grab the token from your Zustand store
    const {token} = useAuthStore();

    const handleLoginButtonOnClick = () => {
        navigate(PATHS.LOGIN);
    };

    return (
        <Box sx={{width: '100%', mt: 2, mb: 4}}>
            <Stack
                direction="row"
                justifyContent="space-between"
                alignItems="center"
                sx={{width: '100%', padding: 2}}
            >
                {/* Left Side: Logo and Title */}
                <Box sx={{display: 'flex', alignItems: 'center'}}>
                    <ShoppingCartSharpIcon fontSize={"large"} sx={{color: 'mediumpurple'}}/>
                    <Typography variant="h4" sx={{fontWeight: 'bold', letterSpacing: 1, fontFamily: 'ui-rounded'}}>
                        Monthly Grocery Manager
                    </Typography>
                </Box>

                {/* Right Side: Conditional Rendering */}
                <Box sx={{display: 'flex', alignItems: 'center'}}>
                    {token ? (
                        /* Show greeting if token exists */
                        <Typography sx={{fontWeight: 'bold', color: 'mediumpurple'}}>
                            Hi, {token.username}
                        </Typography>
                    ) : (
                        /* Show Login Button if token is null */
                        <MonthlyGroceryAppLoginButton onClick={handleLoginButtonOnClick}/>
                    )}
                </Box>
            </Stack>

            <Divider sx={{width: '100%', borderBottomWidth: 2, borderColor: 'blueviolet'}}/>
        </Box>
    );
}

export default MonthlyGroceryAppBar;
