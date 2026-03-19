/**
 * CryptoVue Data Loader
 * Reads JSON scan files and populates the dashboard
 */

// Configuration
const DATA_PATH = '../skills/tradingview-claw-v2/';
const CORE_HOLDINGS = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'BNB', 'LINK'];

// State
let latestData = null;
let historicalData = [];
let allCoins = new Set();

/**
 * Load the most recent scan data
 */
async function loadLatestScan() {
    try {
        // Get list of JSON files
        const response = await fetch(DATA_PATH);
        // For now, we'll use a hardcoded list based on what we saw
        const files = [
            'top_50_analysis_20260319_120036.json',
            'top_50_analysis_20260319_080035.json',
            'top_50_analysis_20260319_040032.json',
            'top_50_analysis_20260319_000030.json',
            'top_50_analysis_20260318_200040.json',
            'top_50_analysis_20260318_160033.json',
            'top_50_analysis_20260318_120035.json',
            'top_50_analysis_20260318_080037.json',
            'top_50_analysis_20260318_040034.json',
            'top_50_analysis_20260318_000040.json',
            'top_50_analysis_20260317_200031.json',
            'top_50_analysis_20260317_160040.json',
            'top_50_analysis_20260317_120030.json',
            'top_50_analysis_20260317_112812.json',
            'top_50_analysis_20260316_120031.json',
            'top_50_analysis_20260316_094553.json',
            'top_50_analysis_20260316_000029.json',
            'top_50_analysis_20260315_200028.json',
            'top_50_analysis_20260315_160033.json',
            'top_50_analysis_20260315_142111.json',
            'top_50_analysis_20260315_120036.json',
            'top_50_analysis_20260315_080026.json',
            'top_50_analysis_20260315_040032.json',
            'top_50_analysis_20260315_000031.json',
            'top_50_analysis_20260314_220521.json',
            'top_50_analysis_20260314_220035.json',
            'top_50_analysis_20260314_215419.json',
            'top_50_analysis_20260314_212806.json'
        ];
        
        // Load latest file
        if (files.length > 0) {
            const latestFile = files[0];
            const data = await fetch(DATA_PATH + latestFile).then(r => r.json());
            latestData = data;
            return data;
        }
    } catch (error) {
        console.error('Error loading latest scan:', error);
        return null;
    }
}

/**
 * Process scan data for display
 */
function processScanData(data) {
    if (!data || !data.results) return [];
    
    return data.results.map(coin => ({
        symbol: coin.symbol.replace('USDT', ''),
        fullSymbol: coin.symbol,
        price: coin.price,
        signal: coin.signal,
        confidence: coin.confidence,
        confidenceLabel: coin.confidence_label,
        strategy: coin.strategy,
        setupType: coin.setup_type,
        csrsiState: coin.csrsi_state,
        csrsiZone: coin.csrsi_zone,
        csrsiRed: coin.csrsi_red,
        rtomBias: coin.rtom_bias,
        rtomRegime: coin.rtom_regime,
        rtomPosition: coin.rtom_position,
        compression: coin.compression,
        liquiditySweep: coin.liquidity_sweep,
        wickRejection: coin.wick_rejection,
        entryZone: coin.entry_zone,
        stopLoss: coin.stop_loss,
        tp1: coin.tp1,
        tp2: coin.tp2,
        dataSource: coin.data_source,
        timestamp: coin.timestamp
    }));
}

/**
 * Get signal counts
 */
function getSignalCounts(processedData) {
    return {
        long: processedData.filter(c => c.signal === 'long').length,
        short: processedData.filter(c => c.signal === 'short').length,
        hold: processedData.filter(c => c.signal === 'hold').length,
        futures: processedData.filter(c => c.strategy === 'FUTURES').length,
        compression: processedData.filter(c => c.compression).length,
        highConfidence: processedData.filter(c => c.confidence >= 65).length
    };
}

/**
 * Get top opportunities
 */
function getTopOpportunities(processedData, limit = 6) {
    return processedData
        .filter(c => c.strategy === 'FUTURES' || c.confidence >= 45)
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, limit);
}

/**
 * Get core holdings data
 */
function getCoreHoldingsData(processedData) {
    return processedData.filter(c => CORE_HOLDINGS.includes(c.symbol));
}

/**
 * Format price
 */
function formatPrice(price) {
    if (price >= 1000) return '$' + price.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
    if (price >= 1) return '$' + price.toFixed(2);
    return '$' + price.toFixed(4);
}

/**
 * Get signal color
 */
function getSignalColor(signal) {
    switch(signal) {
        case 'long': return '#10B981';
        case 'short': return '#EF4444';
        case 'futures': return '#F59E0B';
        default: return '#6B7280';
    }
}

/**
 * Get signal class
 */
function getSignalClass(signal) {
    switch(signal) {
        case 'long': return 'signal-long';
        case 'short': return 'signal-short';
        case 'futures': return 'signal-futures';
        default: return 'signal-hold';
    }
}

/**
 * Get confidence class
 */
function getConfidenceClass(confidence) {
    if (confidence >= 65) return 'confidence-high';
    if (confidence >= 45) return 'confidence-medium';
    return 'confidence-low';
}

// Export for use in dashboard
window.CryptoDataLoader = {
    loadLatestScan,
    processScanData,
    getSignalCounts,
    getTopOpportunities,
    getCoreHoldingsData,
    formatPrice,
    getSignalColor,
    getSignalClass,
    getConfidenceClass,
    CORE_HOLDINGS
};
