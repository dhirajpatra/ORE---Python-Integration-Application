# ORE (Open Source Risk Engine) Setup and Data Guide

## Overview
ORE is a comprehensive risk analytics platform for pricing and risk managing derivatives. This guide covers installation, data preparation, and usage.

## 1. Installation

### Prerequisites
- C++ compiler (GCC 7+ or MSVC 2017+)
- CMake 3.15+
- Boost libraries (1.72+)
- QuantLib library
- Python 3.8+ (for the wrapper application)

### Building ORE from Source

```bash
# Clone the repository
git clone https://github.com/OpenSourceRisk/Engine.git
cd Engine

# Clone QuantLib (dependency)
git clone https://github.com/lballabio/QuantLib.git

# Build QuantLib first
cd QuantLib
mkdir build && cd build
cmake ..
make -j4
sudo make install

# Return to ORE directory and build
cd ../../
mkdir build && cd build
cmake ..
make -j4

# The ore executable will be in build/App/
```

### Docker Alternative (Easier)

```bash
# Pull the ORE Docker image
docker pull opensourcerisk/ore

# Run ORE in a container
docker run -v /path/to/your/data:/data opensourcerisk/ore ore /data/ore.xml
```

## 2. Python Dependencies

Install required Python packages:

```bash
pip install pandas numpy xml-etree lxml matplotlib
```

## 3. Data Structure

ORE requires several input files organized in a specific structure:

```
project/
├── ore_input/
│   ├── ore.xml                 # Main configuration file
│   ├── portfolio.xml           # Trade portfolio
│   ├── todaysmarket.xml        # Market configuration
│   ├── conventions.xml         # Market conventions
│   ├── curveconfig.xml         # Curve configurations
│   ├── pricingengine.xml       # Pricing engine settings
│   └── market.txt              # Market data (rates, FX, etc.)
└── ore_output/                 # Results will be written here
    ├── npv.csv
    ├── flows.csv
    └── curves.csv
```

## 4. Getting Market Data

### Option 1: Use Sample Data from ORE Examples

ORE provides example datasets in the repository:

```bash
# Examples are in the Engine/Examples directory
cd Engine/Examples/Example_1
# This contains complete sample data
```

### Option 2: Create Your Own Market Data

Create a `market.txt` file with current market rates:

```
# Date format: YYYY-MM-DD
# Quote format: QUOTE_TYPE/INSTRUMENT/CCY/TENOR/TERM value

# Discount curves (OIS rates)
MM/RATE/EUR/0D/1D 0.0350
MM/RATE/EUR/0D/1W 0.0352
MM/RATE/EUR/0D/1M 0.0355
MM/RATE/EUR/0D/3M 0.0360

# Swap rates
IR_SWAP/RATE/EUR/2D/6M/5Y 0.0380
IR_SWAP/RATE/EUR/2D/6M/10Y 0.0400

# FX Spot rates
FX/RATE/EUR/USD 1.1000
FX/RATE/EUR/GBP 0.8500

# FX volatilities
FX_OPTION/RATE_LNVOL/EUR/USD/1Y/ATM 0.08
```

### Option 3: Fetch Live Data (Recommended for Production)

```python
import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_market_data():
    """
    Fetch current market data from various sources
    """
    # Get FX rates
    fx_pairs = ['EURUSD=X', 'EURGBP=X', 'EURJPY=X']
    fx_data = {}
    
    for pair in fx_pairs:
        ticker = yf.Ticker(pair)
        hist = ticker.history(period='1d')
        if not hist.empty:
            fx_data[pair] = hist['Close'].iloc[-1]
    
    # Get interest rate data (using treasury yields as proxy)
    rates = {
        '3M': '^IRX',   # 13 Week Treasury Bill
        '2Y': '^FVX',   # 5 Year Treasury
        '10Y': '^TNX'   # 10 Year Treasury
    }
    
    rate_data = {}
    for tenor, symbol in rates.items():
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d')
        if not hist.empty:
            rate_data[tenor] = hist['Close'].iloc[-1] / 100
    
    return fx_data, rate_data

def create_market_txt(fx_data, rate_data, output_file='market.txt'):
    """
    Create ORE market.txt file from fetched data
    """
    with open(output_file, 'w') as f:
        f.write(f"# Market data as of {datetime.now().strftime('%Y-%m-%d')}\n\n")
        
        # Write rates
        for tenor, rate in rate_data.items():
            f.write(f"MM/RATE/USD/0D/{tenor} {rate:.6f}\n")
        
        # Write FX
        for pair, rate in fx_data.items():
            ccy1 = pair[:3]
            ccy2 = pair[3:6]
            f.write(f"FX/RATE/{ccy1}/{ccy2} {rate:.6f}\n")
```

### Option 4: Bloomberg/Reuters (Enterprise)

If you have access to professional data providers:

```python
# Using Bloomberg API (requires Bloomberg Terminal)
from xbbg import blp

def fetch_bloomberg_data():
    # Fetch swap rates
    swaps = blp.bdh(
        tickers=['EUSA2 Curncy', 'EUSA5 Curncy', 'EUSA10 Curncy'],
        flds=['PX_LAST'],
        start_date='2024-01-01'
    )
    
    # Fetch FX rates
    fx = blp.bdh(
        tickers=['EUR Curncy'],
        flds=['PX_LAST'],
        start_date='2024-01-01'
    )
    
    return swaps, fx
```

## 5. Creating Trade Portfolio

### Simple Trade Examples

#### Interest Rate Swap
```xml
<Trade id="SWAP_001">
  <TradeType>Swap</TradeType>
  <Envelope>
    <Counterparty>BANK_A</Counterparty>
    <NettingSetId>BANK_A_NETTING</NettingSetId>
  </Envelope>
  <SwapData>
    <LegData type="Fixed">
      <Payer>true</Payer>
      <Currency>EUR</Currency>
      <Notionals>
        <Notional>10000000</Notional>
      </Notionals>
      <FixedLegData>
        <Rates>
          <Rate>0.035</Rate>
        </Rates>
      </FixedLegData>
      <ScheduleData>
        <StartDate>2024-01-15</StartDate>
        <EndDate>2029-01-15</EndDate>
        <Tenor>6M</Tenor>
      </ScheduleData>
    </LegData>
    <LegData type="Floating">
      <Payer>false</Payer>
      <Currency>EUR</Currency>
      <Notionals>
        <Notional>10000000</Notional>
      </Notionals>
      <FloatingLegData>
        <Index>EUR-EURIBOR-6M</Index>
      </FloatingLegData>
      <ScheduleData>
        <StartDate>2024-01-15</StartDate>
        <EndDate>2029-01-15</EndDate>
        <Tenor>6M</Tenor>
      </ScheduleData>
    </LegData>
  </SwapData>
</Trade>
```

## 6. Running the Application

```bash
# 1. Prepare your data
python ore_app.py --prepare-data

# 2. Update the ore_executable path in the script
# Edit ore_app.py and set: ore_executable = "/path/to/ore"

# 3. Run ORE
python ore_app.py --run

# 4. Analyze results
python ore_app.py --analyze
```

## 7. Understanding the Output

### NPV Results (npv.csv)
- TradeId: Unique trade identifier
- NPV: Net Present Value in base currency
- BaseCurrency: Currency of NPV
- NettingSet: Netting set identifier

### Cashflow Results (flows.csv)
- TradeId: Trade identifier
- LegNo: Leg number (0, 1, etc.)
- PayDate: Payment date
- Amount: Cashflow amount
- Currency: Cashflow currency
- FlowType: Type (Interest, Notional, etc.)

## 8. Advanced Usage

### Sensitivity Analysis
Add to ore.xml:
```xml
<Analytic type="sensitivity">
  <Parameter name="active">Y</Parameter>
  <Parameter name="parSensitivity">Y</Parameter>
  <Parameter name="outputSensitivity">Y</Parameter>
</Analytic>
```

### CVA (Credit Valuation Adjustment)
```xml
<Analytic type="xva">
  <Parameter name="active">Y</Parameter>
  <Parameter name="cva">Y</Parameter>
  <Parameter name="baseCurrency">EUR</Parameter>
</Analytic>
```

### Stress Testing
Create scenarios in `scenarios.xml`:
```xml
<Scenarios>
  <Scenario name="Rates_Up_100bp">
    <ShiftType>absolute</ShiftType>
    <ShiftSize>0.01</ShiftSize>
    <RiskFactors>IR/EUR/*</RiskFactors>
  </Scenario>
</Scenarios>
```

## 9. Troubleshooting

**Common Issues:**

1. **ORE executable not found**: Make sure the path is correct and the file is executable
   ```bash
   chmod +x /path/to/ore
   ```

2. **Missing market data**: Ensure all required quotes are in market.txt

3. **XML validation errors**: Validate your XML files against ORE schemas

4. **Memory issues**: For large portfolios, increase memory allocation

## 10. Resources

- **Documentation**: https://opensourcerisk.org/docs/
- **User Guide**: Check Engine/Docs/UserGuide/
- **Examples**: Engine/Examples/
- **Forum**: https://opensourcerisk.org/forum/
- **GitHub Issues**: https://github.com/OpenSourceRisk/Engine/issues

## Next Steps

1. Start with Example_1 from the ORE repository
2. Modify the portfolio with your own trades
3. Update market data with current rates
4. Run valuations and analyze results
5. Expand to more complex analytics (CVA, sensitivities, etc.)
