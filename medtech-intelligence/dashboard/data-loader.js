/**
 * NeuroVue Data Loader
 * Dynamic JSON loading with GitHub fallback
 * Version: 2.0 - Dynamic Data Discovery
 */

// Configuration
const DATA_PATH = './data/';
const GITHUB_RAW_URL = 'https://raw.githubusercontent.com/impro58-oss/rooquest1/master/medtech-intelligence/dashboard/data/';

// State
let appData = {
    epidemiology: null,
    portfolio: null,
    revenue: null
};

/**
 * Fetch with local path + GitHub fallback
 */
async function fetchWithFallback(filename) {
    const localUrl = DATA_PATH + filename;
    const githubUrl = GITHUB_RAW_URL + filename;
    
    try {
        // Try local first
        const response = await fetch(localUrl);
        if (response.ok) {
            console.log(`Loaded ${filename} from local path`);
            return await response.json();
        }
    } catch (e) {
        console.log(`Local fetch failed for ${filename}, trying GitHub...`);
    }
    
    // Try GitHub raw
    try {
        const response = await fetch(githubUrl);
        if (response.ok) {
            console.log(`Loaded ${filename} from GitHub`);
            return await response.json();
        }
    } catch (e) {
        console.error(`Failed to load ${filename} from both local and GitHub`);
        throw new Error(`Could not load ${filename}`);
    }
    
    return null;
}

/**
 * Load all NeuroVue data
 */
async function loadNeuroVueData() {
    try {
        const [epidemiology, portfolio, revenue] = await Promise.all([
            fetchWithFallback('data.json').catch(e => {
                console.warn('Epidemiology data not available:', e);
                return null;
            }),
            fetchWithFallback('product-portfolio-data.json').catch(e => {
                console.warn('Portfolio data not available:', e);
                return null;
            }),
            fetchWithFallback('revenue-data.json').catch(e => {
                console.warn('Revenue data not available:', e);
                return generateFallbackRevenue();
            })
        ]);
        
        appData = {
            epidemiology: epidemiology,
            portfolio: portfolio,
            revenue: revenue
        };
        
        console.log('NeuroVue data loaded successfully');
        return appData;
        
    } catch (error) {
        console.error('Error loading NeuroVue data:', error);
        return null;
    }
}

/**
 * Generate fallback revenue data if JSON not available
 */
function generateFallbackRevenue() {
    return {
        companies: [
            { name: 'Stryker', ticker: 'SYK', headquarters: 'USA', marketCap: 85000000000, annualRevenue: 20500000000, revenueGrowth: 8.5, neurovascularRevenue: 1450000000, neurovascularGrowth: 9.1 },
            { name: 'Medtronic', ticker: 'MDT', headquarters: 'Ireland', marketCap: 120000000000, annualRevenue: 32300000000, revenueGrowth: 3.2, neurovascularRevenue: 1380000000, neurovascularGrowth: 8.8 },
            { name: 'Johnson & Johnson', ticker: 'JNJ', headquarters: 'USA', marketCap: 380000000000, annualRevenue: 95000000000, revenueGrowth: 6.8, neurovascularRevenue: 680000000, neurovascularGrowth: 9.2 },
            { name: 'Microvention/Terumo', ticker: 'TER', headquarters: 'Japan', marketCap: 45000000000, annualRevenue: 6200000000, revenueGrowth: 12.1, neurovascularRevenue: 520000000, neurovascularGrowth: 10.0 },
            { name: 'Penumbra', ticker: 'PEN', headquarters: 'USA', marketCap: 5200000000, annualRevenue: 1180000000, revenueGrowth: 24.8, neurovascularRevenue: 380000000, neurovascularGrowth: 11.2 },
            { name: 'Balt', ticker: 'Private', headquarters: 'France', marketCap: null, annualRevenue: 180000000, revenueGrowth: 15.3, neurovascularRevenue: 180000000, neurovascularGrowth: 9.5 },
            { name: 'Wallaby Phenox', ticker: 'Private', headquarters: 'Germany', marketCap: null, annualRevenue: 95000000, revenueGrowth: 35.2, neurovascularRevenue: 95000000, neurovascularGrowth: 12.7 }
        ]
    };
}

/**
 * Process epidemiology data from new structure
 */
function processEpidemiologyData(epidemiologyData) {
    if (!epidemiologyData || !epidemiologyData.regions) {
        return generateFallbackEpidemiology();
    }
    
    const regions = epidemiologyData.regions;
    const result = [];
    
    Object.keys(regions).forEach(key => {
        const region = regions[key];
        if (!region || !region['2024']) return;
        
        const data2024 = region['2024'];
        const data2030 = region['2030'];
        
        result.push({
            name: region.name,
            flag: region.flag,
            population: region.population || 0,
            annualStrokes: data2024.annualStrokes ? data2024.annualStrokes.value : 0,
            strokeDeaths: data2024.strokeDeaths ? data2024.strokeDeaths.value : 0,
            prevalence: data2024.prevalence ? data2024.prevalence.value : 0,
            ivTpa: data2024.treatmentAccess ? data2024.treatmentAccess.ivTpa : 0,
            mt: data2024.treatmentAccess ? data2024.treatmentAccess.mt : 0,
            projected2030: data2030 && data2030.projectedStrokes ? data2030.projectedStrokes.value : 0
        });
    });
    
    return result.sort((a, b) => b.annualStrokes - a.annualStrokes);
}

/**
 * Generate fallback epidemiology data
 */
function generateFallbackEpidemiology() {
    return [
        { name: 'China', flag: '🇨🇳', population: 1412000000, annualStrokes: 3300000, strokeDeaths: 1500000, prevalence: 17800000, ivTpa: 25, mt: 8, projected2030: 4200000 },
        { name: 'European Union', flag: '🇪🇺', population: 447000000, annualStrokes: 1100000, strokeDeaths: 450000, prevalence: 9000000, ivTpa: 35, mt: 18, projected2030: 1350000 },
        { name: 'United States', flag: '🇺🇸', population: 335000000, annualStrokes: 795000, strokeDeaths: 160000, prevalence: 4500000, ivTpa: 40, mt: 25, projected2030: 920000 },
        { name: 'Japan', flag: '🇯🇵', population: 125000000, annualStrokes: 280000, strokeDeaths: 110000, prevalence: 2200000, ivTpa: 45, mt: 20, projected2030: 310000 },
        { name: 'Germany', flag: '🇩🇪', population: 84000000, annualStrokes: 195000, strokeDeaths: 65000, prevalence: 1200000, ivTpa: 50, mt: 30, projected2030: 230000 }
    ];
}

/**
 * Get global statistics from the epidemiology data
 */
function getGlobalStats(epidemiologyData) {
    if (!epidemiologyData || !epidemiologyData.global || !epidemiologyData.global['2024']) {
        return {
            annualStrokes: 12200000,
            strokeDeaths: 6500000,
            prevalence: 101000000,
            mt: 12,
            projected2030: 15100000
        };
    }
    
    const global = epidemiologyData.global['2024'];
    const global2030 = epidemiologyData.global['2030'];
    
    return {
        annualStrokes: global.annualStrokes ? global.annualStrokes.value : 12200000,
        strokeDeaths: global.strokeDeaths ? global.strokeDeaths.value : 6500000,
        prevalence: global.prevalence ? global.prevalence.value : 101000000,
        mt: global.treatmentAccess && global.treatmentAccess.mechanicalThrombectomy ? 
            global.treatmentAccess.mechanicalThrombectomy.global : 12,
        projected2030: global2030 && global2030.projectedStrokes ? 
            global2030.projectedStrokes.value : 15100000
    };
}

/**
 * Process revenue data
 */
function processRevenueData(revenueData) {
    if (!revenueData || !revenueData.companies) {
        return generateFallbackRevenue().companies;
    }
    
    return revenueData.companies.map(company => ({
        name: company.name,
        ticker: company.ticker || 'N/A',
        headquarters: company.headquarters || 'Unknown',
        marketCap: company.market_cap || company.marketCap || 0,
        annualRevenue: company.annual_revenue || company.annualRevenue || 0,
        revenueGrowth: company.revenue_growth || company.revenueGrowth || 0,
        neurovascularRevenue: company.neurovascular_revenue || company.neurovascularRevenue || 0,
        neurovascularGrowth: company.neurovascular_growth || company.neurovascularGrowth || 0
    })).sort((a, b) => b.neurovascularRevenue - a.neurovascularRevenue);
}

/**
 * Process portfolio data
 */
function processPortfolioData(portfolioData) {
    if (!portfolioData) {
        return generateFallbackPortfolio();
    }
    
    // Try different possible structures
    let tableData = null;
    
    if (portfolioData.portfolio_analysis && portfolioData.portfolio_analysis['Tabelle1 (2)']) {
        // New structure with portfolio_analysis
        tableData = portfolioData.portfolio_analysis['Tabelle1 (2)'];
    } else if (portfolioData['Tabelle1 (2)']) {
        // Direct structure
        tableData = portfolioData['Tabelle1 (2)'];
    } else if (portfolioData.product_categories) {
        // Expected structure
        return portfolioData.product_categories.map(cat => ({
            name: cat.category,
            totalProducts: cat.products ? cat.products.length : 0,
            products: cat.products || [],
            marketLeaders: cat.market_leaders || []
        }));
    }
    
    if (!tableData) {
        return generateFallbackPortfolio();
    }
    
    // Process spreadsheet-exported data
    const categories = [];
    const categoryMap = new Map();
    
    tableData.forEach((row, idx) => {
        if (!row['NV Market coverage'] && !row['Product Group']) return;
        
        const categoryName = row['NV Market coverage'] || row['Product Group'];
        
        // Count products from company columns
        const companyColumns = ['Medtronic', 'Stryker', 'Microvention/\nTerumo', 'Cerenovus', 'Balt', 'Penumbra', 'Acandis', 'other'];
        let products = [];
        let marketLeaders = [];
        
        companyColumns.forEach(col => {
            const productsInCell = row[col];
            if (productsInCell && typeof productsInCell === 'string' && productsInCell.trim() !== '-' && productsInCell.trim() !== '') {
                const productNames = productsInCell.split(/\n|,/).map(p => p.trim()).filter(p => p && p !== '-');
                products = products.concat(productNames.map(p => ({ name: p })));
                if (col === 'Medtronic' || col === 'Stryker' || col === 'Cerenovus') {
                    marketLeaders.push(col.replace('/\n', '/').trim());
                }
            }
        });
        
        if (!categoryMap.has(categoryName)) {
            categoryMap.set(categoryName, {
                name: categoryName,
                totalProducts: 0,
                products: [],
                marketLeaders: new Set()
            });
        }
        
        const cat = categoryMap.get(categoryName);
        cat.products = cat.products.concat(products);
        cat.totalProducts += products.length;
        marketLeaders.forEach(l => cat.marketLeaders.add(l));
    });
    
    return Array.from(categoryMap.values()).map(cat => ({
        name: cat.name,
        totalProducts: cat.totalProducts,
        products: cat.products.slice(0, 8), // Limit display
        marketLeaders: Array.from(cat.marketLeaders).slice(0, 5)
    })).slice(0, 8); // Limit to 8 categories
}

/**
 * Generate fallback portfolio data
 */
function generateFallbackPortfolio() {
    return [
        {
            name: 'Coils & Embolization',
            totalProducts: 45,
            products: [
                { name: 'Platinum Coils', company: 'Stryker' },
                { name: 'Concerto', company: 'Medtronic' },
                { name: 'Target', company: 'Stryker' },
                { name: 'HydroCoil', company: 'Microvention' },
                { name: 'Orbit', company: 'Medtronic' }
            ],
            marketLeaders: ['Stryker', 'Medtronic', 'Microvention']
        },
        {
            name: 'Stent Retrievers',
            totalProducts: 8,
            products: [
                { name: 'Trevo', company: 'Stryker' },
                { name: 'Solitaire', company: 'Medtronic' },
                { name: 'EmboTrap', company: 'Johnson & Johnson' },
                { name: 'pRESET', company: 'Phenox' },
                { name: 'AXS Catalyst', company: 'Penumbra' }
            ],
            marketLeaders: ['Stryker', 'Medtronic', 'Johnson & Johnson']
        },
        {
            name: 'Aspiration Catheters',
            totalProducts: 12,
            products: [
                { name: 'Penumbra System', company: 'Penumbra' },
                { name: 'Sophia', company: 'Microvention' },
                { name: 'Trevo Aspiration', company: 'Stryker' },
                { name: 'AXS Vecta', company: 'Penumbra' },
                { name: 'Export', company: 'Medtronic' }
            ],
            marketLeaders: ['Penumbra', 'Microvention', 'Stryker']
        },
        {
            name: 'Flow Diverters',
            totalProducts: 6,
            products: [
                { name: 'Pipeline Flex', company: 'Medtronic' },
                { name: 'FRED', company: 'Microvention' },
                { name: 'Surpass Streamline', company: 'Stryker' },
                { name: 'p64', company: 'Phenox' },
                { name: 'Tubridge', company: 'MicroPort' }
            ],
            marketLeaders: ['Medtronic', 'Microvention', 'Stryker']
        },
        {
            name: 'Balloon Guide Catheters',
            totalProducts: 5,
            products: [
                { name: 'FlowGate', company: 'Stryker' },
                { name: 'Merci', company: 'Medtronic' },
                { name: 'Select', company: 'Penumbra' },
                { name: 'Cello', company: 'Johnson & Johnson' },
                { name: 'Ballast', company: 'Microvention' }
            ],
            marketLeaders: ['Stryker', 'Medtronic', 'Penumbra']
        },
        {
            name: 'Intrasaccular Devices',
            totalProducts: 4,
            products: [
                { name: 'WEB', company: 'Microvention' },
                { name: 'Contour', company: 'Stryker' },
                { name: 'PulseRider', company: 'Phenox' },
                { name: 'Medina', company: 'Medtronic' }
            ],
            marketLeaders: ['Microvention', 'Stryker']
        }
    ];
}

/**
 * Format large numbers with M/B suffix
 */
function formatNumber(num, compact = false) {
    if (num === null || num === undefined) return '--';
    if (num === 0) return '0';
    
    if (compact) {
        if (num >= 1000000000) {
            return (num / 1000000000).toFixed(1) + 'B';
        }
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
    }
    
    return num.toLocaleString();
}

/**
 * Format currency values
 */
function formatCurrency(num) {
    if (num === null || num === undefined || num === 0) return '--';
    
    if (num >= 1000000000) {
        return '$' + (num / 1000000000).toFixed(1) + 'B';
    }
    if (num >= 1000000) {
        return '$' + (num / 1000000).toFixed(0) + 'M';
    }
    if (num >= 1000) {
        return '$' + (num / 1000).toFixed(1) + 'K';
    }
    
    return '$' + num.toLocaleString();
}

/**
 * Format percentage
 */
function formatPercent(num) {
    if (num === null || num === undefined) return '--';
    return num.toFixed(1) + '%';
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
    formatPercent,
    appData
};
