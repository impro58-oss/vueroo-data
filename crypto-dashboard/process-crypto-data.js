/**
 * CryptoVue Data Processor
 * Processes all JSON scan files and generates consolidated data
 * 
 * Usage: node process-crypto-data.js
 */

const fs = require('fs');
const path = require('path');

const SCAN_DIR = '../skills/tradingview-claw-v2/';
const OUTPUT_FILE = './crypto-data.json';

// Get all JSON files
function getScanFiles() {
    const files = fs.readdirSync(SCAN_DIR)
        .filter(f => f.startsWith('top_50_analysis_') && f.endsWith('.json'))
        .sort()
        .reverse(); // Most recent first
    
    return files;
}

// Process a single scan file
function processScanFile(filename) {
    const filepath = path.join(SCAN_DIR, filename);
    const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
    
    const timestamp = data.analysis_time;
    const processed = data.results.map(coin => ({
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
    
    return {
        filename: filename,
        timestamp: timestamp,
        results: processed,
        counts: {
            long: processed.filter(c => c.signal === 'long').length,
            short: processed.filter(c => c.signal === 'short').length,
            hold: processed.filter(c => c.signal === 'hold').length,
            futures: processed.filter(c => c.strategy === 'FUTURES').length,
            compression: processed.filter(c => c.compression).length
        }
    };
}

// Build historical data for each coin
function buildCoinHistory(allScans) {
    const history = {};
    
    allScans.forEach(scan => {
        scan.results.forEach(coin => {
            if (!history[coin.symbol]) {
                history[coin.symbol] = [];
            }
            history[coin.symbol].push({
                timestamp: scan.timestamp,
                price: coin.price,
                signal: coin.signal,
                confidence: coin.confidence,
                strategy: coin.strategy,
                csrsiRed: coin.csrsiRed,
                rtomBias: coin.rtomBias
            });
        });
    });
    
    return history;
}

// Generate trend analysis
function generateTrends(history) {
    const trends = {};
    
    Object.keys(history).forEach(symbol => {
        const data = history[symbol];
        if (data.length < 2) return;
        
        const latest = data[0];
        const previous = data[1];
        const older = data[data.length - 1];
        
        // Signal change detection
        const signalChanged = latest.signal !== previous.signal;
        
        // Confidence trend
        const confidenceChange = latest.confidence - older.confidence;
        
        // Price change
        const priceChange = ((latest.price - older.price) / older.price) * 100;
        
        trends[symbol] = {
            signalChanged: signalChanged,
            previousSignal: previous.signal,
            confidenceChange: confidenceChange,
            priceChange: priceChange,
            dataPoints: data.length
        };
    });
    
    return trends;
}

// Main processing
function main() {
    console.log('🔍 CryptoVue Data Processor');
    console.log('============================');
    
    try {
        // Get all scan files
        const files = getScanFiles();
        console.log(`📁 Found ${files.length} scan files`);
        
        // Process all scans
        const allScans = files.map(f => {
            console.log(`  Processing: ${f}`);
            return processScanFile(f);
        });
        
        // Build history
        const history = buildCoinHistory(allScans);
        console.log(`📊 Built history for ${Object.keys(history).length} coins`);
        
        // Generate trends
        const trends = generateTrends(history);
        console.log(`📈 Generated trends for ${Object.keys(trends).length} coins`);
        
        // Create output data
        const output = {
            generatedAt: new Date().toISOString(),
            totalScans: files.length,
            dateRange: {
                earliest: allScans[allScans.length - 1].timestamp,
                latest: allScans[0].timestamp
            },
            latestScan: allScans[0],
            allScans: allScans.map(s => ({
                filename: s.filename,
                timestamp: s.timestamp,
                counts: s.counts
            })),
            history: history,
            trends: trends
        };
        
        // Write output
        fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
        console.log(`\n✅ Data written to ${OUTPUT_FILE}`);
        
        // Print summary
        const latest = allScans[0];
        console.log('\n📊 Latest Scan Summary:');
        console.log(`  Timestamp: ${latest.timestamp}`);
        console.log(`  Total Coins: ${latest.results.length}`);
        console.log(`  Long Signals: ${latest.counts.long}`);
        console.log(`  Short Signals: ${latest.counts.short}`);
        console.log(`  Futures Ready: ${latest.counts.futures}`);
        console.log(`  Compression: ${latest.counts.compression}`);
        
        // Top opportunities
        const opportunities = latest.results
            .filter(c => c.strategy === 'FUTURES' || c.confidence >= 45)
            .sort((a, b) => b.confidence - a.confidence)
            .slice(0, 5);
        
        console.log('\n🎯 Top 5 Opportunities:');
        opportunities.forEach((c, i) => {
            console.log(`  ${i+1}. ${c.symbol} - ${c.signal.toUpperCase()} (${c.confidence}%) - ${c.strategy}`);
        });
        
        // Signal changes
        const changes = Object.entries(trends)
            .filter(([_, t]) => t.signalChanged)
            .slice(0, 5);
        
        if (changes.length > 0) {
            console.log('\n🔄 Recent Signal Changes:');
            changes.forEach(([sym, t]) => {
                console.log(`  ${sym}: ${t.previousSignal} → ${latest.results.find(c => c.symbol === sym)?.signal}`);
            });
        }
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        process.exit(1);
    }
}

main();
