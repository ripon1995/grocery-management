// overloaded method
function formatDate(dateInput: Date): string;
function formatDate(dateInput: string): string;
function formatDate(dateInput: undefined): 'N/A';

// implementation signature
function formatDate(dateInput: Date | string | undefined): string {
    if (!dateInput) return 'N/A';
    return new Date(dateInput).toLocaleDateString('en-US', {day: 'numeric', month: 'long', year: 'numeric'});
}

export { formatDate };