import TextField from '@mui/material/TextField';


interface ITextInputProps {
    label: string;
    value: string;
    onChange: (val: string) => void;
}

function MonthlyGroceryAppInputField({label, value, onChange}: ITextInputProps) {
    return (
        <TextField
            fullWidth
            label={label}
            variant="outlined"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            sx={{
                mb: 2,
                '& .MuiOutlinedInput-root': {
                    borderRadius: '4px',
                }
            }}
        />
    );
}

export default MonthlyGroceryAppInputField;