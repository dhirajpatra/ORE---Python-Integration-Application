"""
ORE (Open Source Risk Engine) Python Application
This application demonstrates how to set up and run ORE calculations
"""

import os
import subprocess
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
import json
from datetime import datetime

class ORERunner:
    """
    Wrapper class for running ORE (Open Source Risk Engine) calculations
    """
    
    def __init__(self, ore_executable_path, input_dir, output_dir):
        """
        Initialize ORE Runner
        
        Args:
            ore_executable_path: Path to the ORE executable
            input_dir: Directory containing input files
            output_dir: Directory for output files
        """
        self.ore_exe = ore_executable_path
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_ore_xml_config(self, config_file="ore.xml"):
        """
        Create the main ORE configuration XML file
        """
        config = f"""<?xml version="1.0"?>
<ORE>
  <Setup>
    <Parameter name="asofDate">{datetime.now().strftime('%Y-%m-%d')}</Parameter>
    <Parameter name="inputPath">{self.input_dir}</Parameter>
    <Parameter name="outputPath">{self.output_dir}</Parameter>
  </Setup>
  
  <Markets>
    <Parameter name="lgmcalibration">collateral_eur</Parameter>
    <Parameter name="fxcalibration">xois_eur</Parameter>
    <Parameter name="pricing">pricing</Parameter>
    <Parameter name="simulation">simulation</Parameter>
  </Markets>
  
  <Analytics>
    <Analytic type="npv">
      <Parameter name="active">Y</Parameter>
      <Parameter name="baseCurrency">EUR</Parameter>
    </Analytic>
    
    <Analytic type="cashflow">
      <Parameter name="active">Y</Parameter>
    </Analytic>
    
    <Analytic type="curves">
      <Parameter name="active">Y</Parameter>
      <Parameter name="configuration">default</Parameter>
      <Parameter name="grid">240,1M</Parameter>
    </Analytic>
  </Analytics>
</ORE>
"""
        
        config_path = self.input_dir / config_file
        with open(config_path, 'w') as f:
            f.write(config)
        
        return config_path
    
    def create_portfolio_xml(self, trades):
        """
        Create portfolio XML file with trades
        
        Args:
            trades: List of trade dictionaries
        """
        portfolio = ET.Element('Portfolio')
        
        for trade in trades:
            trade_elem = ET.SubElement(portfolio, 'Trade', id=trade['id'])
            
            trade_type = ET.SubElement(trade_elem, 'TradeType')
            trade_type.text = trade['type']
            
            envelope = ET.SubElement(trade_elem, 'Envelope')
            counterparty = ET.SubElement(envelope, 'Counterparty')
            counterparty.text = trade.get('counterparty', 'CPTY_A')
            
            # Add trade-specific data
            if trade['type'] == 'Swap':
                self._add_swap_data(trade_elem, trade)
            elif trade['type'] == 'FxForward':
                self._add_fx_forward_data(trade_elem, trade)
        
        tree = ET.ElementTree(portfolio)
        portfolio_path = self.input_dir / 'portfolio.xml'
        tree.write(portfolio_path, encoding='utf-8', xml_declaration=True)
        
        return portfolio_path
    
    def _add_swap_data(self, trade_elem, trade):
        """Add Interest Rate Swap data to trade element"""
        swap_data = ET.SubElement(trade_elem, 'SwapData')
        
        # Add legs
        for leg in trade.get('legs', []):
            leg_elem = ET.SubElement(swap_data, 'LegData', type=leg['type'])
            
            payer = ET.SubElement(leg_elem, 'Payer')
            payer.text = str(leg['payer'])
            
            currency = ET.SubElement(leg_elem, 'Currency')
            currency.text = leg['currency']
            
            notionals = ET.SubElement(leg_elem, 'Notionals')
            notional = ET.SubElement(notionals, 'Notional')
            notional.text = str(leg['notional'])
            
            schedule = ET.SubElement(leg_elem, 'ScheduleData')
            start_date = ET.SubElement(schedule, 'StartDate')
            start_date.text = leg['start_date']
            end_date = ET.SubElement(schedule, 'EndDate')
            end_date.text = leg['end_date']
            
    def _add_fx_forward_data(self, trade_elem, trade):
        """Add FX Forward data to trade element"""
        fx_data = ET.SubElement(trade_elem, 'FxForwardData')
        
        maturity = ET.SubElement(fx_data, 'ValueDate')
        maturity.text = trade['maturity_date']
        
        bought_currency = ET.SubElement(fx_data, 'BoughtCurrency')
        bought_currency.text = trade['bought_currency']
        
        bought_amount = ET.SubElement(fx_data, 'BoughtAmount')
        bought_amount.text = str(trade['bought_amount'])
        
        sold_currency = ET.SubElement(fx_data, 'SoldCurrency')
        sold_currency.text = trade['sold_currency']
        
        sold_amount = ET.SubElement(fx_data, 'SoldAmount')
        sold_amount.text = str(trade['sold_amount'])
    
    def create_market_data(self):
        """
        Create sample market data configuration
        """
        # This is a simplified example - real market data would be more complex
        market_data = """<?xml version="1.0"?>
<TodaysMarket>
  <Configuration>
    <DiscountingCurves>
      <DiscountingCurve>
        <CurveId>EUR-EONIA</CurveId>
        <Currency>EUR</Currency>
        <YieldCurve>EUR-EONIA</YieldCurve>
      </DiscountingCurve>
    </DiscountingCurves>
    
    <YieldCurves>
      <YieldCurve>
        <CurveId>EUR-EONIA</CurveId>
        <Currency>EUR</Currency>
        <Segments>
          <Simple>
            <Type>Deposit</Type>
            <Quotes>
              <Quote>MM/RATE/EUR/0D/1D</Quote>
            </Quotes>
            <Conventions>EUR-EONIA-CONVENTIONS</Conventions>
          </Simple>
        </Segments>
      </YieldCurve>
    </YieldCurves>
  </Configuration>
</TodaysMarket>
"""
        market_path = self.input_dir / 'todaysmarket.xml'
        with open(market_path, 'w') as f:
            f.write(market_data)
        
        return market_path
    
    def run_ore(self, config_file="ore.xml"):
        """
        Execute ORE with the given configuration
        """
        config_path = self.input_dir / config_file
        
        if not os.path.exists(self.ore_exe):
            raise FileNotFoundError(f"ORE executable not found at {self.ore_exe}")
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
        
        # Run ORE
        cmd = [self.ore_exe, str(config_path)]
        
        print(f"Running ORE: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"ORE Error: {result.stderr}")
            raise RuntimeError(f"ORE execution failed with return code {result.returncode}")
        
        print("ORE execution completed successfully")
        return result
    
    def read_npv_results(self):
        """
        Read NPV results from output
        """
        npv_file = self.output_dir / "npv.csv"
        
        if not npv_file.exists():
            print("NPV file not found")
            return None
        
        df = pd.read_csv(npv_file)
        return df
    
    def read_cashflow_results(self):
        """
        Read cashflow results from output
        """
        cf_file = self.output_dir / "flows.csv"
        
        if not cf_file.exists():
            print("Cashflow file not found")
            return None
        
        df = pd.read_csv(cf_file)
        return df


def main():
    """
    Main function demonstrating ORE usage
    """
    
    # Configuration
    ore_executable = "/path/to/ore"  # Update this path
    input_directory = "./ore_input"
    output_directory = "./ore_output"
    
    # Initialize ORE Runner
    ore_runner = ORERunner(ore_executable, input_directory, output_directory)
    
    # Create sample portfolio
    sample_trades = [
        {
            'id': 'SWAP_001',
            'type': 'Swap',
            'counterparty': 'BANK_A',
            'legs': [
                {
                    'type': 'Fixed',
                    'payer': 'true',
                    'currency': 'EUR',
                    'notional': 10000000,
                    'start_date': '2024-01-15',
                    'end_date': '2029-01-15'
                },
                {
                    'type': 'Floating',
                    'payer': 'false',
                    'currency': 'EUR',
                    'notional': 10000000,
                    'start_date': '2024-01-15',
                    'end_date': '2029-01-15'
                }
            ]
        },
        {
            'id': 'FX_001',
            'type': 'FxForward',
            'counterparty': 'BANK_B',
            'maturity_date': '2025-06-15',
            'bought_currency': 'USD',
            'bought_amount': 1000000,
            'sold_currency': 'EUR',
            'sold_amount': 900000
        }
    ]
    
    # Create input files
    print("Creating configuration files...")
    ore_runner.create_ore_xml_config()
    ore_runner.create_portfolio_xml(sample_trades)
    ore_runner.create_market_data()
    
    # Run ORE (commented out - uncomment when you have ORE installed)
    # print("Running ORE...")
    # ore_runner.run_ore()
    
    # Read results (uncomment after running ORE)
    # print("Reading results...")
    # npv_results = ore_runner.read_npv_results()
    # if npv_results is not None:
    #     print("\nNPV Results:")
    #     print(npv_results)
    
    # cf_results = ore_runner.read_cashflow_results()
    # if cf_results is not None:
    #     print("\nCashflow Results:")
    #     print(cf_results)
    
    print("\nSetup complete! Input files created in:", input_directory)


if __name__ == "__main__":
    main()
