"""
Data Generator for PackagingCo BI Portfolio

This module provides utilities to generate realistic mock data for development and testing.
It can create both transaction-level and aggregated data to simulate real-world scenarios.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional, Tuple, Union
import os


class MockDataGenerator:
    """Generate realistic mock data for PackagingCo BI portfolio."""
    
    def __init__(self, seed: int = 42):
        """Initialize the data generator with a random seed."""
        np.random.seed(seed)
        random.seed(seed)
        
        # Define product configurations with more realistic details
        self.products = {
            'Plastic Containers': {
                'base_cost': 3.0,
                'base_price': 5.0,
                'emissions_factor': 0.8,  # kg CO2 per unit
                'energy_factor': 2.5,     # kWh per unit
                'water_factor': 1.2,      # liters per unit
                'waste_factor': 0.1,      # kg waste per unit
                'recycled_material_potential': 0.6,  # max % recycled
                'virgin_material_potential': 0.4,    # min % virgin
                'sku_prefix': 'PLASTIC',
                'weight_kg': 0.5,
                'volume_liters': 1.0,
                'shelf_life_days': 365,
                'regulatory_compliance': ['FDA', 'EU_Food_Safe'],
                'sustainability_rating': 3  # 1-5 scale
            },
            'Paper Packaging': {
                'base_cost': 2.5,
                'base_price': 4.5,
                'emissions_factor': 0.5,
                'energy_factor': 1.8,
                'water_factor': 0.8,
                'waste_factor': 0.05,
                'recycled_material_potential': 0.8,
                'virgin_material_potential': 0.2,
                'sku_prefix': 'PAPER',
                'weight_kg': 0.3,
                'volume_liters': 0.8,
                'shelf_life_days': 180,
                'regulatory_compliance': ['FDA', 'FSC_Certified'],
                'sustainability_rating': 4
            },
            'Glass Bottles': {
                'base_cost': 4.0,
                'base_price': 8.0,
                'emissions_factor': 1.2,
                'energy_factor': 4.0,
                'water_factor': 2.0,
                'waste_factor': 0.15,
                'recycled_material_potential': 0.3,
                'virgin_material_potential': 0.7,
                'sku_prefix': 'GLASS',
                'weight_kg': 1.2,
                'volume_liters': 1.5,
                'shelf_life_days': 730,
                'regulatory_compliance': ['FDA', 'EU_Food_Safe', 'Recyclable'],
                'sustainability_rating': 5
            },
            'Aluminum Cans': {
                'base_cost': 3.5,
                'base_price': 6.5,
                'emissions_factor': 1.0,
                'energy_factor': 3.2,
                'water_factor': 1.5,
                'waste_factor': 0.08,
                'recycled_material_potential': 0.7,
                'virgin_material_potential': 0.3,
                'sku_prefix': 'ALUM',
                'weight_kg': 0.4,
                'volume_liters': 0.5,
                'shelf_life_days': 1095,
                'regulatory_compliance': ['FDA', 'Recyclable'],
                'sustainability_rating': 4
            },
            'Biodegradable Packaging': {
                'base_cost': 4.5,
                'base_price': 7.5,
                'emissions_factor': 0.3,
                'energy_factor': 1.5,
                'water_factor': 0.6,
                'waste_factor': 0.02,
                'recycled_material_potential': 0.9,
                'virgin_material_potential': 0.1,
                'sku_prefix': 'BIO',
                'weight_kg': 0.2,
                'volume_liters': 0.6,
                'shelf_life_days': 90,
                'regulatory_compliance': ['FDA', 'Biodegradable', 'Compostable'],
                'sustainability_rating': 5
            }
        }
        
        # Define facility configurations with more detail
        self.facilities = {
            'Plant A - North America': {
                'efficiency_factor': 1.0,
                'location': 'North America',
                'capacity': 50000,
                'sustainability_initiative': True,
                'certifications': ['ISO_14001', 'LEED_Gold'],
                'energy_source': 'Mixed (60% Renewable)',
                'water_recycling_rate': 0.85,
                'waste_recycling_rate': 0.92,
                'employee_count': 150,
                'production_hours_per_day': 16,
                'maintenance_schedule': 'Preventive',
                'technology_level': 'Advanced'
            },
            'Plant B - Europe': {
                'efficiency_factor': 0.95,
                'location': 'Europe',
                'capacity': 45000,
                'sustainability_initiative': False,
                'certifications': ['ISO_14001'],
                'energy_source': 'Grid (30% Renewable)',
                'water_recycling_rate': 0.70,
                'waste_recycling_rate': 0.78,
                'employee_count': 120,
                'production_hours_per_day': 14,
                'maintenance_schedule': 'Reactive',
                'technology_level': 'Standard'
            },
            'Plant C - Asia Pacific': {
                'efficiency_factor': 0.90,
                'location': 'Asia Pacific',
                'capacity': 60000,
                'sustainability_initiative': True,
                'certifications': ['ISO_14001', 'ISO_50001'],
                'energy_source': 'Solar + Grid',
                'water_recycling_rate': 0.95,
                'waste_recycling_rate': 0.88,
                'employee_count': 200,
                'production_hours_per_day': 20,
                'maintenance_schedule': 'Predictive',
                'technology_level': 'Cutting-edge'
            }
        }
        
        # Define customer segments with more detail
        self.customer_segments = {
            'Retail': {
                'price_sensitivity': 0.8,
                'volume_factor': 0.7,
                'sustainability_preference': 0.6,
                'payment_terms': 'Net 30',
                'order_frequency': 'Weekly',
                'average_order_size': 1000,
                'loyalty_level': 'Medium',
                'growth_rate': 0.05
            },
            'Wholesale': {
                'price_sensitivity': 0.6,
                'volume_factor': 1.3,
                'sustainability_preference': 0.4,
                'payment_terms': 'Net 60',
                'order_frequency': 'Monthly',
                'average_order_size': 5000,
                'loyalty_level': 'High',
                'growth_rate': 0.08
            },
            'Food & Beverage': {
                'price_sensitivity': 0.7,
                'volume_factor': 1.1,
                'sustainability_preference': 0.8,
                'payment_terms': 'Net 45',
                'order_frequency': 'Bi-weekly',
                'average_order_size': 3000,
                'loyalty_level': 'High',
                'growth_rate': 0.12
            },
            'Pharmaceutical': {
                'price_sensitivity': 0.4,
                'volume_factor': 0.8,
                'sustainability_preference': 0.5,
                'payment_terms': 'Net 90',
                'order_frequency': 'Monthly',
                'average_order_size': 2000,
                'loyalty_level': 'Very High',
                'growth_rate': 0.15
            },
            'E-commerce': {
                'price_sensitivity': 0.9,
                'volume_factor': 1.5,
                'sustainability_preference': 0.7,
                'payment_terms': 'Net 15',
                'order_frequency': 'Daily',
                'average_order_size': 500,
                'loyalty_level': 'Low',
                'growth_rate': 0.20
            }
        }
        
        # Define regions with market characteristics
        self.regions = {
            'North America': {
                'market_growth': 0.02,
                'price_premium': 1.0,
                'sustainability_demand': 0.7,
                'regulatory_environment': 'Moderate',
                'competition_level': 'High',
                'logistics_cost_factor': 1.0,
                'currency': 'USD',
                'timezone': 'EST'
            },
            'Europe': {
                'market_growth': 0.015,
                'price_premium': 1.1,
                'sustainability_demand': 0.8,
                'regulatory_environment': 'Strict',
                'competition_level': 'Medium',
                'logistics_cost_factor': 1.2,
                'currency': 'EUR',
                'timezone': 'CET'
            },
            'Asia Pacific': {
                'market_growth': 0.08,
                'price_premium': 0.9,
                'sustainability_demand': 0.5,
                'regulatory_environment': 'Variable',
                'competition_level': 'Very High',
                'logistics_cost_factor': 0.8,
                'currency': 'USD',
                'timezone': 'SGT'
            },
            'Latin America': {
                'market_growth': 0.06,
                'price_premium': 0.85,
                'sustainability_demand': 0.4,
                'regulatory_environment': 'Developing',
                'competition_level': 'Medium',
                'logistics_cost_factor': 1.1,
                'currency': 'USD',
                'timezone': 'BRT'
            }
        }
        
        # Define suppliers for supply chain simulation
        self.suppliers = {
            'Green Materials Co': {
                'reliability': 0.95,
                'cost_factor': 1.1,
                'sustainability_rating': 5,
                'delivery_time_days': 7,
                'quality_rating': 0.98,
                'certifications': ['FSC', 'ISO_14001']
            },
            'Standard Supply Inc': {
                'reliability': 0.88,
                'cost_factor': 1.0,
                'sustainability_rating': 3,
                'delivery_time_days': 5,
                'quality_rating': 0.95,
                'certifications': ['ISO_9001']
            },
            'EcoTech Solutions': {
                'reliability': 0.92,
                'cost_factor': 1.2,
                'sustainability_rating': 5,
                'delivery_time_days': 10,
                'quality_rating': 0.99,
                'certifications': ['FSC', 'ISO_14001', 'Cradle_to_Cradle']
            }
        }

    def generate_transaction_level_sales(self, 
                                       start_date: str = '2023-01-01',
                                       end_date: str = '2023-12-31',
                                       daily_transactions: int = 200) -> pd.DataFrame:
        """
        Generate transaction-level sales data (like real ERP data).
        
        Args:
            start_date: Start date for data generation
            end_date: End date for data generation
            daily_transactions: Number of transactions per day
            
        Returns:
            DataFrame with transaction-level sales data
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        date_range = pd.date_range(start, end, freq='D')
        
        transactions = []
        
        for date in date_range:
            for _ in range(daily_transactions):
                # Random product selection
                product = random.choice(list(self.products.keys()))
                product_config = self.products[product]
                
                # Random region and customer segment
                region = random.choice(list(self.regions.keys()))
                customer_segment = random.choice(list(self.customer_segments.keys()))
                
                # Generate realistic quantities with segment-based variation
                segment_config = self.customer_segments[customer_segment]
                base_quantity = segment_config['average_order_size']
                quantity = int(np.random.normal(base_quantity, base_quantity * 0.3))
                quantity = max(1, quantity)  # Ensure positive
                
                # Calculate costs and prices with realistic variation
                base_cost = float(product_config['base_cost'])
                base_price = float(product_config['base_price'])
                
                # Add regional price premium and seasonal variation
                regional_premium = float(self.regions[region]['price_premium'])
                seasonal_factor = 1 + 0.15 * np.sin(2 * np.pi * date.dayofyear / 365)
                
                # Add market growth over time
                days_from_start = (date - start).days
                growth_factor = 1 + (days_from_start / 365) * float(self.regions[region]['market_growth'])
                
                final_price = base_price * regional_premium * seasonal_factor * growth_factor
                final_price *= random.uniform(0.95, 1.05)  # Small random variation
                
                # Calculate costs with supplier variation
                supplier = random.choice(list(self.suppliers.keys()))
                supplier_config = self.suppliers[supplier]
                final_cost = base_cost * float(supplier_config['cost_factor']) * random.uniform(0.9, 1.1)
                
                # Calculate revenue and costs
                revenue = quantity * final_price
                cost_of_goods = quantity * final_cost
                operating_cost = cost_of_goods * random.uniform(0.25, 0.45)  # 25-45% of COGS
                profit_margin = revenue - cost_of_goods - operating_cost
                
                # Add realistic transaction details
                transaction_id = f"TXN_{date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}"
                customer_id = f"CUST_{random.randint(1000, 9999)}"
                order_id = f"ORD_{date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}"
                sku = f"{product_config['sku_prefix']}_{random.randint(100, 999)}"
                
                # Add delivery and payment information
                delivery_date = date + timedelta(days=random.randint(1, 14))
                payment_terms = str(segment_config['payment_terms'])
                payment_status = random.choice(['Paid', 'Pending', 'Overdue'])
                
                transactions.append({
                    'transaction_id': transaction_id,
                    'date': date,
                    'customer_id': customer_id,
                    'order_id': order_id,
                    'product_line': product,
                    'sku': sku,
                    'region': region,
                    'customer_segment': customer_segment,
                    'supplier': supplier,
                    'units_sold': quantity,
                    'unit_price': round(final_price, 2),
                    'unit_cost': round(final_cost, 2),
                    'revenue': round(revenue, 2),
                    'cost_of_goods': round(cost_of_goods, 2),
                    'operating_cost': round(operating_cost, 2),
                    'profit_margin': round(profit_margin, 2),
                    'delivery_date': delivery_date,
                    'payment_terms': payment_terms,
                    'payment_status': payment_status,
                    'currency': str(self.regions[region]['currency']),
                    'weight_kg': quantity * float(product_config['weight_kg']),
                    'volume_liters': quantity * float(product_config['volume_liters'])
                })
        
        return pd.DataFrame(transactions)

    def generate_transaction_level_esg(self,
                                     start_date: str = '2023-01-01',
                                     end_date: str = '2023-12-31',
                                     daily_batches: int = 100) -> pd.DataFrame:
        """
        Generate transaction-level ESG data (like real production data).
        
        Args:
            start_date: Start date for data generation
            end_date: End date for data generation
            daily_batches: Number of production batches per day
            
        Returns:
            DataFrame with transaction-level ESG data
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        date_range = pd.date_range(start, end, freq='D')
        
        production_records = []
        
        for date in date_range:
            for _ in range(daily_batches):
                # Random product and facility selection
                product = random.choice(list(self.products.keys()))
                facility = random.choice(list(self.facilities.keys()))
                
                product_config = self.products[product]
                facility_config = self.facilities[facility]
                
                # Generate batch size with facility capacity constraints
                max_batch_size = int(facility_config['capacity']) // 30  # Daily capacity
                batch_size = random.randint(100, max_batch_size)
                
                # Calculate ESG metrics based on product and facility
                efficiency_factor = float(facility_config['efficiency_factor'])
                
                # Base emissions and resource usage
                emissions = batch_size * float(product_config['emissions_factor']) * efficiency_factor
                energy = batch_size * float(product_config['energy_factor']) * efficiency_factor
                water = batch_size * float(product_config['water_factor']) * efficiency_factor
                waste = batch_size * float(product_config['waste_factor']) * efficiency_factor
                
                # Material composition with sustainability improvements over time
                days_from_start = (date - start).days
                sustainability_progress = min(0.4, days_from_start / 365 * 0.4)  # 40% improvement over year
                
                # Facility-specific sustainability initiatives
                if bool(facility_config['sustainability_initiative']):
                    sustainability_progress += 0.2
                
                recycled_pct = (float(product_config['recycled_material_potential']) * 
                              (0.6 + sustainability_progress) * random.uniform(0.8, 1.2))
                recycled_pct = min(100, max(0, recycled_pct))
                virgin_pct = 100 - recycled_pct
                
                # Recycling rate based on facility capabilities
                base_recycling_rate = float(facility_config['waste_recycling_rate']) * 100
                recycling_rate = base_recycling_rate * random.uniform(0.9, 1.1)
                recycling_rate = min(100, max(0, recycling_rate))
                
                # Add realistic production details
                batch_id = f"BATCH_{date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}"
                operator_id = f"OP_{random.randint(1000, 9999)}"
                equipment_id = f"EQ_{random.randint(1000, 9999)}"
                
                # Production hours and efficiency
                production_hours = random.uniform(8, float(facility_config['production_hours_per_day']))
                efficiency_rating = random.uniform(0.85, 1.0)
                
                # Quality metrics
                defect_rate = random.uniform(0.01, 0.05)  # 1-5% defect rate
                quality_score = 1 - defect_rate
                
                # Energy source and efficiency
                energy_source = str(facility_config['energy_source'])
                renewable_energy_pct = random.uniform(0.3, 0.8) if 'Renewable' in energy_source else random.uniform(0.1, 0.3)
                
                # Water recycling
                water_recycled = water * float(facility_config['water_recycling_rate']) * random.uniform(0.8, 1.0)
                water_fresh = water - water_recycled
                
                # Add some daily variation and anomalies
                daily_factor = random.uniform(0.7, 1.3)
                emissions *= daily_factor
                energy *= daily_factor
                water *= daily_factor
                waste *= daily_factor
                
                production_records.append({
                    'batch_id': batch_id,
                    'date': date,
                    'product_line': product,
                    'facility': facility,
                    'batch_size': batch_size,
                    'emissions_kg_co2': round(emissions, 2),
                    'energy_consumption_kwh': round(energy, 2),
                    'water_usage_liters': round(water, 2),
                    'water_recycled_liters': round(water_recycled, 2),
                    'water_fresh_liters': round(water_fresh, 2),
                    'recycled_material_pct': round(recycled_pct, 2),
                    'virgin_material_pct': round(virgin_pct, 2),
                    'waste_generated_kg': round(waste, 2),
                    'recycling_rate_pct': round(recycling_rate, 2),
                    'production_hours': round(production_hours, 2),
                    'efficiency_rating': round(efficiency_rating, 3),
                    'quality_score': round(quality_score, 3),
                    'defect_rate_pct': round(defect_rate * 100, 2),
                    'renewable_energy_pct': round(renewable_energy_pct * 100, 2),
                    'operator_id': operator_id,
                    'equipment_id': equipment_id,
                    'energy_source': energy_source,
                    'maintenance_status': random.choice(['Normal', 'Scheduled', 'Emergency']),
                    'temperature_celsius': random.uniform(18, 25),
                    'humidity_pct': random.uniform(40, 60)
                })
        
        return pd.DataFrame(production_records)

    def generate_supply_chain_data(self,
                                 start_date: str = '2023-01-01',
                                 end_date: str = '2023-12-31') -> pd.DataFrame:
        """
        Generate supply chain data for future module.
        
        Args:
            start_date: Start date for data generation
            end_date: End date for data generation
            
        Returns:
            DataFrame with supply chain data
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        date_range = pd.date_range(start, end, freq='D')
        
        supply_chain_records = []
        
        for date in date_range:
            # Generate procurement orders
            for supplier in self.suppliers.keys():
                supplier_config = self.suppliers[supplier]
                
                # Random order frequency
                if random.random() < 0.3:  # 30% chance of order per day
                    order_quantity = random.randint(1000, 10000)
                    order_value = order_quantity * random.uniform(2.0, 5.0)
                    
                    # Delivery performance
                    expected_delivery = date + timedelta(days=int(supplier_config['delivery_time_days']))
                    actual_delivery = expected_delivery + timedelta(days=random.randint(-2, 5))
                    
                    # Quality issues
                    quality_issues = random.random() < (1 - float(supplier_config['quality_rating']))
                    defect_quantity = order_quantity * random.uniform(0.01, 0.05) if quality_issues else 0
                    
                    supply_chain_records.append({
                        'date': date,
                        'supplier': supplier,
                        'order_id': f"PO_{date.strftime('%Y%m%d')}_{random.randint(1000, 9999)}",
                        'order_quantity': order_quantity,
                        'order_value': round(order_value, 2),
                        'expected_delivery': expected_delivery,
                        'actual_delivery': actual_delivery,
                        'on_time_delivery': actual_delivery <= expected_delivery,
                        'quality_issues': quality_issues,
                        'defect_quantity': defect_quantity,
                        'supplier_reliability': float(supplier_config['reliability']),
                        'sustainability_rating': float(supplier_config['sustainability_rating'])
                    })
        
        return pd.DataFrame(supply_chain_records)

    def aggregate_to_monthly(self, transaction_df: pd.DataFrame, 
                           group_columns: List[str]) -> pd.DataFrame:
        """
        Aggregate transaction-level data to monthly level.
        
        Args:
            transaction_df: Transaction-level DataFrame
            group_columns: Columns to group by for aggregation
            
        Returns:
            DataFrame with monthly aggregated data
        """
        # Ensure date column is datetime
        transaction_df['date'] = pd.to_datetime(transaction_df['date'])
        
        # Group by month and specified columns
        transaction_df['month'] = transaction_df['date'].dt.to_period('M')
        group_cols = ['month'] + group_columns

        # Aggregate numeric columns
        agg_dict = {
            'units_sold': 'sum',
            'revenue': 'sum',
            'cost_of_goods': 'sum',
            'operating_cost': 'sum',
            'profit_margin': 'sum',
            'weight_kg': 'sum',
            'volume_liters': 'sum'
        }

        # Only include columns that exist in the DataFrame
        existing_agg_cols = {k: v for k, v in agg_dict.items() if k in transaction_df.columns}
        monthly_data = transaction_df.groupby(group_cols)[list(existing_agg_cols.keys())].agg(existing_agg_cols).reset_index()

        # Convert period back to datetime
        monthly_data['month'] = monthly_data['month'].dt.to_timestamp()
        
        return monthly_data

    def aggregate_esg_to_monthly(self, esg_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate ESG transaction data to monthly level.
        
        Args:
            esg_df: Transaction-level ESG DataFrame
            
        Returns:
            DataFrame with monthly aggregated ESG data
        """
        # Ensure date column is datetime
        esg_df['date'] = pd.to_datetime(esg_df['date'])
        
        # Group by month, product line, and facility
        esg_df['month'] = esg_df['date'].dt.to_period('M')

        # Aggregate ESG metrics
        agg_dict = {
            'batch_size': 'sum',
            'emissions_kg_co2': 'sum',
            'energy_consumption_kwh': 'sum',
            'water_usage_liters': 'sum',
            'water_recycled_liters': 'sum',
            'water_fresh_liters': 'sum',
            'waste_generated_kg': 'sum',
            'production_hours': 'sum',
            'recycled_material_pct': 'mean',
            'virgin_material_pct': 'mean',
            'recycling_rate_pct': 'mean',
            'efficiency_rating': 'mean',
            'quality_score': 'mean',
            'defect_rate_pct': 'mean',
            'renewable_energy_pct': 'mean'
        }

        # Only include columns that exist in the DataFrame
        existing_agg_cols = {k: v for k, v in agg_dict.items() if k in esg_df.columns}
        monthly_esg = esg_df.groupby(['month', 'product_line', 'facility'])[list(existing_agg_cols.keys())].agg(existing_agg_cols).reset_index()

        # Convert period back to datetime
        monthly_esg['month'] = monthly_esg['month'].dt.to_timestamp()
        
        return monthly_esg

    def generate_and_save_mock_data(self, 
                                  output_dir: str = 'data/raw',
                                  generate_transaction_level: bool = False) -> Dict[str, str]:
        """
        Generate comprehensive mock data and save to files.
        
        Args:
            output_dir: Directory to save generated data
            generate_transaction_level: Whether to generate transaction-level data
            
        Returns:
            Dictionary with paths to generated files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = {}
        
        if generate_transaction_level:
            # Generate transaction-level data
            print("Generating transaction-level sales data...")
            sales_transactions = self.generate_transaction_level_sales()
            sales_transactions_path = os.path.join(output_dir, 'sales_transactions.csv')
            sales_transactions.to_csv(sales_transactions_path, index=False)
            generated_files['sales_transactions'] = sales_transactions_path
            
            print("Generating transaction-level ESG data...")
            esg_transactions = self.generate_transaction_level_esg()
            esg_transactions_path = os.path.join(output_dir, 'esg_transactions.csv')
            esg_transactions.to_csv(esg_transactions_path, index=False)
            generated_files['esg_transactions'] = esg_transactions_path
            
            print("Generating supply chain data...")
            supply_chain_data = self.generate_supply_chain_data()
            supply_chain_path = os.path.join(output_dir, 'supply_chain_data.csv')
            supply_chain_data.to_csv(supply_chain_path, index=False)
            generated_files['supply_chain_data'] = supply_chain_path
            
            # Aggregate to monthly for dbt seeds
            print("Aggregating sales data to monthly...")
            monthly_sales = self.aggregate_to_monthly(
                sales_transactions, 
                ['product_line', 'region', 'customer_segment']
            )
            monthly_sales_path = os.path.join(output_dir, 'sample_sales_data.csv')
            monthly_sales.to_csv(monthly_sales_path, index=False)
            generated_files['monthly_sales'] = monthly_sales_path
            
            print("Aggregating ESG data to monthly...")
            monthly_esg = self.aggregate_esg_to_monthly(esg_transactions)
            monthly_esg_path = os.path.join(output_dir, 'sample_esg_data.csv')
            monthly_esg.to_csv(monthly_esg_path, index=False)
            generated_files['monthly_esg'] = monthly_esg_path
            
        else:
            # Generate only monthly aggregated data (current approach)
            print("Generating monthly aggregated sales data...")
            sales_transactions = self.generate_transaction_level_sales()
            monthly_sales = self.aggregate_to_monthly(
                sales_transactions, 
                ['product_line', 'region', 'customer_segment']
            )
            monthly_sales_path = os.path.join(output_dir, 'sample_sales_data.csv')
            monthly_sales.to_csv(monthly_sales_path, index=False)
            generated_files['monthly_sales'] = monthly_sales_path
            
            print("Generating monthly aggregated ESG data...")
            esg_transactions = self.generate_transaction_level_esg()
            monthly_esg = self.aggregate_esg_to_monthly(esg_transactions)
            monthly_esg_path = os.path.join(output_dir, 'sample_esg_data.csv')
            monthly_esg.to_csv(monthly_esg_path, index=False)
            generated_files['monthly_esg'] = monthly_esg_path
        
        print(f"Generated {len(generated_files)} data files in {output_dir}")
        return generated_files


def generate_mock_data(output_dir: str = 'data/raw', 
                      transaction_level: bool = False,
                      seed: int = 42) -> Dict[str, str]:
    """
    Convenience function to generate mock data.
    
    Args:
        output_dir: Directory to save generated data
        transaction_level: Whether to generate transaction-level data
        seed: Random seed for reproducibility
        
    Returns:
        Dictionary with paths to generated files
    """
    generator = MockDataGenerator(seed=seed)
    return generator.generate_and_save_mock_data(output_dir, transaction_level)


if __name__ == "__main__":
    # Example usage
    print("Generating mock data...")
    files = generate_mock_data(transaction_level=True)
    
    for file_type, file_path in files.items():
        print(f"{file_type}: {file_path}") 