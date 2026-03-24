import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import {Divider} from "@mui/material";
import ShoppingCartSharpIcon from '@mui/icons-material/ShoppingCartSharp';
import Stack from "@mui/material/Stack";
import {MonthlyGroceryAppLoginButton} from "./MonthlyGroceryAppButton.tsx";
import PATHS from "../../constants/paths.ts";
import {useNavigate} from "react-router-dom";


function MonthlyGroceryAppBar() {

    const navigate = useNavigate();

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

                {/* Right Side: Login Button */}
                <Box sx={{display: 'flex', alignItems: 'center'}}>
                    <MonthlyGroceryAppLoginButton onClick={handleLoginButtonOnClick}/>
                </Box>
            </Stack>

            <Divider sx={{width: '100%', borderBottomWidth: 2, borderColor: 'blueviolet'}}/>
        </Box>
    );
}

export default MonthlyGroceryAppBar;
