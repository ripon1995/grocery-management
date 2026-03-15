import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import {Divider} from "@mui/material";
import ShoppingCartSharpIcon from '@mui/icons-material/ShoppingCartSharp';

function MonthlyGroceryAppBar() {
    return (
        <Box sx={{width: '100%', mt: 2, mb: 4}}>
            <Box sx={{display: 'flex', alignItems: 'center'}}>
                <ShoppingCartSharpIcon fontSize={"large"}></ShoppingCartSharpIcon>
                <Typography variant="h4" sx={{fontWeight: 'bold', letterSpacing: 1, fontFamily: 'ui-rounded'}}>
                    Monthly Grocery Manager
                </Typography>
            </Box>

            <Divider sx={{width: '100%', borderBottomWidth: 2, borderColor: 'blueviolet'}}/>
        </Box>
    );
}

export default MonthlyGroceryAppBar;
