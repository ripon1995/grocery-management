import {Typography, Paper, Box} from "@mui/material";
import {red} from "@mui/material/colors";
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

interface ErrorStateProps {
    message?: string | null;
    minHeight?: string | number;
    width?: string | number;
}

const MonthlyGroceryAppError = ({
                                    message = "An unexpected error occurred",
                                    minHeight = 400,
                                    width = 900
                                }: ErrorStateProps) => {
    return (
        <Box sx={{
            display: 'flex',
            justifyContent: 'center',
            width: '100%',
            mt: 4
        }}>
            <Paper
                elevation={6}
                sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: minHeight,
                    width: width,
                    maxWidth: '100%',
                    p: 4,
                    borderRadius: 1,
                    gap: 2
                }}
            >
                {/* Adding an icon makes the error state visually clearer */}
                <ErrorOutlineIcon sx={{fontSize: 60, color: red[400]}}/>

                <Typography
                    variant="h4"
                    align="center"
                    sx={{
                        fontWeight: 300,
                        letterSpacing: '0.5px',
                        color: red[800]
                    }}
                >
                    {message || "An unexpected error occurred"}
                </Typography>
            </Paper>
        </Box>
    );
};

export default MonthlyGroceryAppError;