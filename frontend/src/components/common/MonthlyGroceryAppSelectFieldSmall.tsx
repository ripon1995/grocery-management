import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, {type SelectChangeEvent} from '@mui/material/Select';

interface ISelectProps {
    label: string;
    value: string;
    onChange: (val: string) => void;
    options: string[];
}

function MonthlyGroceryAppSelectField({label, value, onChange, options}: ISelectProps) {

    const handleChange = (event: SelectChangeEvent) => {
        onChange(event.target.value as string);
    };

    return (
        <Box
            sx={{
                display: 'flex',
                alignItems: 'center', // Aligns label with the Select box
                mb: 2,
                width: '80%',
            }}
        >
            {/* Label Section - Matching DisplayField and InputField */}
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

            {/* Select Section */}
            <FormControl fullWidth>
                <Select
                    value={value}
                    onChange={handleChange}
                    displayEmpty
                    sx={{
                        textAlign: 'left',
                        backgroundColor: '#ffffff',
                        '& .MuiOutlinedInput-notchedOutline': {
                            borderRadius: '4px',
                            borderColor: 'rgba(0, 0, 0, 0.2)',
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                            borderColor: 'primary.main',
                        },
                        '& .MuiSelect-select': {
                            padding: '10px 14px', // Matches the slim height of your other fields
                        }
                    }}
                >
                    {options.map((opt) => (
                        <MenuItem key={opt} value={opt}>
                            {opt.toUpperCase()}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
        </Box>
    );
}

export default MonthlyGroceryAppSelectField;