import {Avatar, Tooltip, IconButton} from "@mui/material"; // Add these imports
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import {Divider} from "@mui/material";
import ShoppingCartSharpIcon from '@mui/icons-material/ShoppingCartSharp';
import Stack from "@mui/material/Stack";
import {MonthlyGroceryAppLoginButton} from "./MonthlyGroceryAppButton.tsx";
import PATHS from "../../constants/paths.ts";
import {useNavigate} from "react-router-dom";
import useAuthStore from "../../store/useAuthStore.ts"; // Import your store
import log from "loglevel";

function MonthlyGroceryAppBar() {

    const navigate = useNavigate();

    // 1. Grab the token from your Zustand store
    const {token} = useAuthStore();

    const handleLoginButtonOnClick = () => {
        navigate(PATHS.LOGIN);
    };

    const handleProfileClick = () => {
        log.debug('Profile icon clicked');
    }


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

                {/* Right Side: Login Button */}
                {/* Right Side: Conditional Rendering */}
                <Box sx={{display: 'flex', alignItems: 'center'}}>
                    {token ? (
                        /* Show Avatar if token exists */
                        <Tooltip title={token.user_email}>
                            <IconButton onClick={handleProfileClick} sx={{p: 0}}>
                                <Avatar sx={{color: 'mediumpurple', fontWeight: 'bold'}}>
                                    {token.user_email.charAt(0).toUpperCase()}
                                </Avatar>
                            </IconButton>
                        </Tooltip>
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
