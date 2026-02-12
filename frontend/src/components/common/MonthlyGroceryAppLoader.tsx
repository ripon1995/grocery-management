import {Box, CircularProgress, Typography, Paper} from "@mui/material";

interface LoadingStateProps {
    message?: string;
    minHeight?: string | number;
    width?: string | number;
}

const MonthlyGroceryAppLoader = ({
                                     message = "Fetching Groceries...",
                                     minHeight = 400,
                                     width = 900
                                 }: LoadingStateProps) => {
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
                    gap: 3,
                }}
            >
                <Box sx={{position: 'relative', display: 'inline-flex'}}>
                    {/* Background track for the spinner */}
                    <CircularProgress
                        variant="determinate"
                        sx={{color: (theme) => theme.palette.grey[200]}}
                        size={60}
                        thickness={4}
                        value={100}
                    />
                    {/* Active spinning part */}
                    <CircularProgress
                        variant="indeterminate"
                        disableShrink
                        sx={{
                            color: 'purple', // Matches your header theme
                            animationDuration: '550ms',
                            position: 'absolute',
                            left: 0,
                        }}
                        size={60}
                        thickness={4}
                    />
                </Box>
                <Typography
                    variant="h4"
                    sx={{
                        fontWeight: 300,
                        letterSpacing: '0.5px',
                        color: 'text.secondary'
                    }}
                >
                    {message}
                </Typography>
            </Paper>
        </Box>
    );
};

export default MonthlyGroceryAppLoader;