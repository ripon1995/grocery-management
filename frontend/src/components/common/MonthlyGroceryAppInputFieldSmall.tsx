import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";

interface MonthlyGroceryAppInputFieldSmallProps {
    label: string;
    value: string | number;
    onChange: (value: string) => void; // Handler to pass the value back up
    placeholder?: string;
    type?: string; // e.g., 'text' or 'number'
}

function MonthlyGroceryAppInputFieldSmall({
                                              label,
                                              value,
                                              onChange,
                                              placeholder,
                                              type = "text"
                                          }: MonthlyGroceryAppInputFieldSmallProps) {
    return (
        <Box
            sx={{
                display: 'flex',
                alignItems: 'center',
                mb: 2,
                width: '80%',
            }}
        >
            {/* Label Section - Identical to DisplayField */}
            <Typography
                sx={{
                    fontWeight: 600,
                    color: 'text.secondary',
                    width: '20%',
                    minWidth: '80px',
                    pr: 2,
                }}
            >
                {label}
            </Typography>

            {/* Input Section */}
            <TextField
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                type={type}
                variant="outlined"
                fullWidth
                sx={{
                    '& .MuiOutlinedInput-root': {
                        borderRadius: '4px',
                        backgroundColor: '#ffffff', // White background to signal it's editable
                        '&:hover fieldset': {
                            borderColor: 'primary.main', // Highlight on hover
                        },
                    },
                    '& .MuiOutlinedInput-input': {
                        padding: '10px 14px',
                    }
                }}
            />
        </Box>
    );
}

export default MonthlyGroceryAppInputFieldSmall;