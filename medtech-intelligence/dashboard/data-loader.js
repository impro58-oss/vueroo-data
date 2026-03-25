/**
 * NeuroVue Data Loader
 * Reads JSON data files and populates the dashboard
 * DYNAMIC: Fetches from GitHub or local fallback
 */

// Configuration
const DATA_BASE_PATH = '../medtech-intelligence/dashboard/data/';
const GITHUB_RAW_URL = 'https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/data/';

// State
let neuroData = null;
let revenueData = null;
let portfolioData = null;

/**
 * Fetch with local path + GitHub fallback
 */
async function fetchWithFallback(filename) {
    const localPath = DATA_BASE_PATH + filename;
    const githubUrl = GITHUB_RAW_URL + filename;
    
    try {
        // Try local first
        const response = await fetch(localPath);
        if (response.ok) {
            return await response.json();
        }
    } catch (e) {
        console.log('Local fetch failed for', filename, '- trying GitHub');
    }
    
    // Try GitHub raw
    try {
        const response = await fetch(githubUrl);
        if (response.ok) {
            return await response.json();
        }
    } catch (e2) {
        console.error('GitHub fetch failed for', filename);
    }
    
    return null;
}

/**
 * Load all NeuroVue data files
 */
async function loadNeuroVueData() {
    try {
        // Load main epidemiological data
        neuroData = await fetchWithFallback('data.json');
        
        // Load revenue data
        revenueData = await fetchWithFallback('revenue-data.json');
        
        // Load portfolio data
        portfolioData = await fetchWithFallback('product-portfolio-data.json');
        
        console.log('NeuroVue data loaded:', {
            epidemiology: !!neuroData,
            revenue: !!revenueData,
            portfolio: !!portfolioData
        });
        
        return {
            epidemiology: neuroData,
            revenue: revenueData,
            portfolio: portfolioData
        };
        
    } catch (error) {
        console.error('Error loading NeuroVue data:', error);
        return null;
    }
}

/**
 * Process epidemiology data for display
 */
function processEpidemiologyData(data) {
    if (!data || !data.global || !data.regions) return [];
    
    const regions = [];
    
    for (const [key, region] of Object.entries(data.regions)) {
        if (key === 'metadata') continue;
        
        const region2024 = region['2024'] || {};
        
        regions.push({
            key: key,
            name: region.name || key,
            flag: region.flag || '',
            population: region.population || 0,
            annualStrokes: region2024.annualStrokes?.value || 0,
            strokeDeaths: region2024.strokeDeaths?.value || 0,
            prevalence: region2024.prevalence?.value || 0,
            ivTpa: region2024.treatmentAccess?.ivTpa || 0,
            mt: region2024.treatmentAccess?.mt || 0,
            projected2030: region['2030']?.projectedStrokes?.value || 0
        });
    }
    
    return regions.sort((a, b) => b.annualStrokes - a.annualStrokes);
}

/**
 * Get global statistics
 */
function getGlobalStats(data) {
    if (!data || !data.global || !data.global['2024']) return null;
    
    const global2024 = data.global['2024'];
    const global2030 = data.global['2030'];
    
    return {
        annualStrokes: global2024.annualStrokes?.value || 12200000,
        strokeDeaths: global2024.strokeDeaths?.value || 6500000,
        prevalence: global2024.prevalence?.value || 101000000,
        ivTpa: global2024.treatmentAccess?.ivTpa?.global || 15,
        mt: global2024.treatmentAccess?.mechanicalThrombectomy?.global || 12,
        projected2030: global2030?.projectedStrokes?.value || 15100000
    };
}

/**
 * Process revenue data
 */
function processRevenueData(data) {
    if (!data || !data.companies) return [];
    
    return data.companies.map(company => ({
        name: company.name,
        ticker: company.ticker,
        headquarters: company.headquarters,
        marketCap: company.marketCap,
        annualRevenue: company.annualRevenue,
        revenueGrowth: company.revenueGrowth,
        neurovascularRevenue: company.neurovascularRevenue,
        neurovascularGrowth: company.neurovascularGrowth,
        strokeProducts: company.strokeProducts || [],
        aneurysmProducts: company.aneurysmProducts || []
    }));
}

/**
 * Process portfolio data
 */
function processPortfolioData(data) {
    if (!data || !data.categories) return [];
    
    return data.categories.map(category => ({
        name: category.name,
        products: category.products || [],
        totalProducts: (category.products || []).length,
        marketLeaders: category.marketLeaders || []
    }));
}

/**
 * Format large numbers
 */
function formatNumber(num, compact = false) {
    if (num === null || num === undefined) return 'N/A';
    
    if (compact) {
        if (num >= 1000000000) return (num / 1000000000).toFixed(1) + 'B';
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }
    
    return num.toLocaleString('en-US');
}

/**
 * Format currency
 */
function formatCurrency(num, decimals = 1) {
    if (num === null || num === undefined) return 'N/A';
    
    if (num >= 1000000000) return '$' + (num / 1000000000).toFixed(decimals) + 'B';
    if (num >= 1000000) return '$' + (num / 1000000).toFixed(decimals) + 'M';
    if (num >= 1000) return '$' + (num / 1000).toFixed(decimals) + 'K';
    return '$' + num.toFixed(decimals);
}

/**
 * Get severity color
 */
function getSeverityColor(value, thresholds) {
    if (value >= thresholds.high) return '#ef4444'; // Red
    if (value >= thresholds.medium) return '#f59e0b'; // Amber
    return '#10b981'; // Green
}

/**
 * Get severity class
 */
function getSeverityClass(value, thresholds) {
    if (value >= thresholds.high) return 'severity-high';
    if (value >= thresholds.medium) return 'severity-medium';
    return 'severity-low';
}

// Export for use in dashboard
window.NeuroVueDataLoader = {
    loadNeuroVueData,
    processEpidemiologyData,
    getGlobalStats,
    processRevenueData,
    processPortfolioData,
    formatNumber,
    formatCurrency,
    getSeverityColor,
    getSeverityClass
};
