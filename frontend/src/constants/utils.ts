export const formatDate = (dateInput: string | Date | undefined) => {
    if (!dateInput) return 'N/A';

    return new Date(dateInput).toLocaleDateString('en-US', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    });
};