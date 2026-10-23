import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import {Alert, AlertTitle, Button, LinearProgress, Link, Stack, Typography} from "@mui/material";
import type {IGroceryListItem} from "../../types/IGroceryList.ts";
import type {
    IGroceryExploreResult,
    IMarketExploreError,
    IMarketExploreProgress,
    IMarketExploreResult,
    IShopOffer
} from "../../types/IMarketExplore.ts";
import MonthlyGroceryAppLoader from "../common/MonthlyGroceryAppLoader.tsx";

interface IMarketExploreDialogProps {
    open: boolean;
    isLoading: boolean;
    result: IMarketExploreResult | null;
    progress: IMarketExploreProgress | null;
    error: IMarketExploreError | null;
    groceries: IGroceryListItem[];
    onClose: () => void;
}

// Offer urls come from Gemini, so only link to real web pages
const isSafeUrl = (url: string | null): url is string => url != null && /^https?:\/\//i.test(url);

const groceryName = (groceries: IGroceryListItem[], grocery_id: string): string =>
    groceries.find((item) => item.id === grocery_id)?.name ?? grocery_id;

const progressMessage = (progress: IMarketExploreProgress | null): string =>
    progress == null ? 'Queuing explore...' : `Searching shops... ${progress.done} of ${progress.total}`;

const OfferLabel = ({offer}: { offer: IShopOffer }) => (
    <Typography variant="body2">
        <strong style={{textTransform: 'uppercase'}}>{offer.seller}</strong>
        {` ${offer.price.toFixed(0)} BDT — `}
        {isSafeUrl(offer.url) ? (
            <Link href={offer.url} target="_blank" rel="noopener noreferrer">{offer.product_name}</Link>
        ) : offer.product_name}
    </Typography>
);

const Savings = ({currentPrice, cheapest}: { currentPrice: number; cheapest: IShopOffer | null }) => {
    if (cheapest == null) return <>—</>;
    const savings = currentPrice - cheapest.price;
    if (savings > 0) return <Typography color="success.main" fontWeight="bold">Save {savings} BDT</Typography>;
    if (savings < 0) return <Typography color="text.secondary">{-savings} BDT more</Typography>;
    return <Typography color="text.secondary">Same price</Typography>;
};

const ExploreResultRow = ({row, grocery}: { row: IGroceryExploreResult; grocery: IGroceryListItem | undefined }) => {
    const offers = [...row.offers].sort((a, b) => a.price - b.price);
    return (
        <TableRow>
            <TableCell sx={{fontWeight: 500}}>{grocery?.name ?? row.grocery_id}</TableCell>
            <TableCell align="center">
                {grocery ? (
                    <>
                        {grocery.current_price.toFixed(0)} BDT
                        <Typography variant="caption" display="block" sx={{textTransform: 'uppercase'}}>
                            {grocery.current_seller}
                        </Typography>
                    </>
                ) : '—'}
            </TableCell>
            <TableCell>
                {offers.length === 0 ? (
                    <Typography variant="body2" color="text.secondary">No offers found</Typography>
                ) : (
                    <Stack spacing={0.5}>
                        {offers.map((offer) => <OfferLabel key={offer.seller} offer={offer}/>)}
                    </Stack>
                )}
            </TableCell>
            <TableCell align="center">
                {grocery ? <Savings currentPrice={grocery.current_price} cheapest={row.cheapest}/> : '—'}
            </TableCell>
        </TableRow>
    );
};

function MarketExploreDialog({open, isLoading, result, progress, error, groceries, onClose}: IMarketExploreDialogProps) {
    const hasResults = result != null && result.results.length > 0;

    // Closing while it polls is fine: the job keeps running in the worker
    return (
        <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
            <DialogTitle sx={{fontWeight: 'bold'}}>Explore Market Prices</DialogTitle>
            <DialogContent>
                {isLoading && !hasResults ? (
                    <MonthlyGroceryAppLoader message={progressMessage(progress)} minHeight={250} width="100%"/>
                ) : (
                    <Stack spacing={2}>
                        {isLoading && progress != null && (
                            <Stack spacing={1}>
                                <Typography variant="body2" color="text.secondary">{progressMessage(progress)}</Typography>
                                <LinearProgress
                                    variant="determinate"
                                    value={progress.total > 0 ? (progress.done / progress.total) * 100 : 0}
                                />
                            </Stack>
                        )}
                        {error != null && (
                            <Alert severity="error">
                                <AlertTitle>{error.message}</AlertTitle>
                                <Typography variant="body2" sx={{wordBreak: 'break-word'}}>{error.detail}</Typography>
                            </Alert>
                        )}
                        {result != null && result.not_found_ids.length > 0 && (
                            <Alert severity="warning">
                                {`Not found: ${result.not_found_ids.map((id) => groceryName(groceries, id)).join(', ')}. They may have been deleted.`}
                            </Alert>
                        )}
                        {hasResults && (
                            <Table size="small">
                                <TableHead>
                                    <TableRow sx={{'& .MuiTableCell-head': {fontWeight: 'bold'}}}>
                                        <TableCell>Name</TableCell>
                                        <TableCell align="center">Current</TableCell>
                                        <TableCell>Shop offers</TableCell>
                                        <TableCell align="center">Cheapest vs current</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {result.results.map((row) => (
                                        <ExploreResultRow
                                            key={row.grocery_id}
                                            row={row}
                                            grocery={groceries.find((item) => item.id === row.grocery_id)}
                                        />
                                    ))}
                                </TableBody>
                            </Table>
                        )}
                        {hasResults && (
                            <Typography variant="caption" color="text.secondary">
                                Prices are found by AI web search and may be out of date. Check the shop before buying.
                            </Typography>
                        )}
                    </Stack>
                )}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} sx={{color: 'purple', fontWeight: 'bold'}}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}

export default MarketExploreDialog;
