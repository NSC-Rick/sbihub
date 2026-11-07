"""
Deal Optimization Engine (WPP-FME-026)

Evaluates multiple capital structure scenarios using grid search
to find optimal deal structures based on specified objectives and constraints.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from sbi_hub.modules.financial_modeler.engine.model import build_model


class DealOptimizer:
    """
    Optimizes deal structure by testing multiple capital structure scenarios.
    
    Uses grid search to evaluate combinations of:
    - Buyer equity
    - Seller note
    - Working capital
    
    Bank loan is derived from purchase price minus other sources.
    """
    
    def __init__(
        self,
        base_model_inputs: Dict,
        purchase_price: float,
        objective: str = "minimize_buyer_equity",
        minimum_dscr: float = 1.25,
        minimum_cash_balance: float = 5000.0,
        maximum_loan_amount: Optional[float] = None,
        max_iterations: int = 5000
    ):
        """
        Initialize the deal optimizer.
        
        Args:
            base_model_inputs: Base model configuration (revenue, expenses, etc.)
            purchase_price: Target purchase price
            objective: Optimization objective (minimize_buyer_equity, maximize_purchase_price, 
                      maximize_dscr, maximize_owner_income)
            minimum_dscr: Minimum acceptable DSCR constraint
            minimum_cash_balance: Minimum acceptable cash balance constraint
            maximum_loan_amount: Maximum acceptable bank loan (optional)
            max_iterations: Maximum scenarios to test (safety limit)
        """
        self.base_model_inputs = base_model_inputs.copy()
        self.purchase_price = purchase_price
        self.objective = objective
        self.minimum_dscr = minimum_dscr
        self.minimum_cash_balance = minimum_cash_balance
        self.maximum_loan_amount = maximum_loan_amount
        self.max_iterations = max_iterations
        
        # Results storage
        self.valid_scenarios = []
        self.total_scenarios_tested = 0
        self.scenarios_skipped = 0
        
    def define_search_ranges(
        self,
        buyer_equity_range: Optional[Tuple[float, float, float]] = None,
        seller_note_range: Optional[Tuple[float, float, float]] = None,
        working_capital_range: Optional[Tuple[float, float, float]] = None
    ):
        """
        Define search ranges for optimization variables.
        
        Args:
            buyer_equity_range: (min, max, step) for buyer equity
            seller_note_range: (min, max, step) for seller note
            working_capital_range: (min, max, step) for working capital
        """
        # Default ranges
        self.buyer_equity_range = buyer_equity_range or (0, 150000, 5000)
        self.seller_note_range = seller_note_range or (0, 200000, 5000)
        self.working_capital_range = working_capital_range or (5000, 50000, 5000)
        
    def generate_scenarios(self) -> List[Dict]:
        """
        Generate all possible scenarios using grid search.
        
        Returns:
            List of scenario dictionaries with capital structure parameters
        """
        scenarios = []
        
        # Generate buyer equity values
        buyer_equity_min, buyer_equity_max, buyer_equity_step = self.buyer_equity_range
        buyer_equity_values = []
        current = buyer_equity_min
        while current <= buyer_equity_max:
            buyer_equity_values.append(current)
            current += buyer_equity_step
        
        # Generate seller note values
        seller_note_min, seller_note_max, seller_note_step = self.seller_note_range
        seller_note_values = []
        current = seller_note_min
        while current <= seller_note_max:
            seller_note_values.append(current)
            current += seller_note_step
        
        # Generate working capital values
        wc_min, wc_max, wc_step = self.working_capital_range
        working_capital_values = []
        current = wc_min
        while current <= wc_max:
            working_capital_values.append(current)
            current += wc_step
        
        # Grid search
        for buyer_equity in buyer_equity_values:
            for seller_note in seller_note_values:
                for working_capital in working_capital_values:
                    # Calculate bank loan (derived)
                    # bank_loan = purchase_price - buyer_equity - seller_note - grants - donations - community_equity
                    capital_stack = self.base_model_inputs.get('capital_stack', {})
                    sources = capital_stack.get('sources', {})
                    
                    grants = sources.get('grants', 0)
                    donations = sources.get('donations', 0)
                    community_equity = sources.get('community_equity', 0)
                    
                    bank_loan = (
                        self.purchase_price 
                        - buyer_equity 
                        - seller_note 
                        - grants 
                        - donations 
                        - community_equity
                    )
                    
                    # Skip if bank loan is negative
                    if bank_loan < 0:
                        continue
                    
                    # Skip if bank loan exceeds maximum (if specified)
                    if self.maximum_loan_amount is not None and bank_loan > self.maximum_loan_amount:
                        continue
                    
                    scenarios.append({
                        'buyer_equity': buyer_equity,
                        'seller_note': seller_note,
                        'working_capital': working_capital,
                        'bank_loan': bank_loan
                    })
                    
                    # Safety limit
                    if len(scenarios) >= self.max_iterations:
                        return scenarios
        
        return scenarios
    
    def evaluate_scenario(self, scenario: Dict) -> Optional[Dict]:
        """
        Evaluate a single scenario by running the financial model.
        
        Args:
            scenario: Capital structure parameters
            
        Returns:
            Result dictionary if valid, None if constraints not met
        """
        # Build model inputs with this scenario's capital structure
        model_inputs = self.base_model_inputs.copy()
        
        # Update capital stack
        capital_stack = model_inputs.get('capital_stack', {})
        if not capital_stack.get('enabled', False):
            capital_stack['enabled'] = True
        
        sources = capital_stack.get('sources', {})
        sources['buyer_equity'] = scenario['buyer_equity']
        sources['bank_loan'] = scenario['bank_loan']
        sources['seller_note'] = scenario['seller_note']
        
        uses = capital_stack.get('uses', {})
        uses['working_capital'] = scenario['working_capital']
        
        capital_stack['sources'] = sources
        capital_stack['uses'] = uses
        model_inputs['capital_stack'] = capital_stack
        
        try:
            # Run the model
            outputs = build_model(model_inputs)
            
            # Extract key metrics
            kpis = outputs.get('kpis', {})
            cash_flow = outputs.get('cash_flow', None)
            
            # Get DSCR (average or minimum)
            dscr = kpis.get('avg_dscr', 0)
            
            # Get minimum cash balance
            if cash_flow is not None:
                min_cash = cash_flow['ending_cash'].min()
            else:
                min_cash = 0
            
            # Get owner income (total distributions or net income)
            income_statement = outputs.get('income_statement', None)
            if income_statement is not None:
                owner_income = income_statement['net_income'].sum()
            else:
                owner_income = 0
            
            # Check constraints
            if dscr < self.minimum_dscr:
                return None
            
            if min_cash < self.minimum_cash_balance:
                return None
            
            # Valid scenario - store results
            result = {
                'buyer_equity': scenario['buyer_equity'],
                'bank_loan': scenario['bank_loan'],
                'seller_note': scenario['seller_note'],
                'working_capital': scenario['working_capital'],
                'dscr': dscr,
                'min_cash': min_cash,
                'purchase_price': self.purchase_price,
                'owner_income': owner_income
            }
            
            return result
            
        except Exception as e:
            # Model failed - skip this scenario
            return None
    
    def optimize(self) -> Dict:
        """
        Run the optimization process.
        
        Returns:
            Dictionary with optimization results including best scenario and all valid scenarios
        """
        # Define search ranges
        self.define_search_ranges()
        
        # Generate all scenarios
        scenarios = self.generate_scenarios()
        
        # Evaluate each scenario
        for scenario in scenarios:
            self.total_scenarios_tested += 1
            
            result = self.evaluate_scenario(scenario)
            
            if result is not None:
                self.valid_scenarios.append(result)
            else:
                self.scenarios_skipped += 1
        
        # Select best scenario based on objective
        best_scenario = self.select_best_scenario()
        
        # Sort valid scenarios by objective for top 10 display
        sorted_scenarios = self.sort_scenarios_by_objective()
        
        return {
            'best_scenario': best_scenario,
            'valid_scenarios': self.valid_scenarios,
            'sorted_scenarios': sorted_scenarios[:10],  # Top 10
            'total_scenarios_tested': self.total_scenarios_tested,
            'valid_scenarios_count': len(self.valid_scenarios),
            'scenarios_skipped': self.scenarios_skipped,
            'objective': self.objective,
            'constraints': {
                'minimum_dscr': self.minimum_dscr,
                'minimum_cash_balance': self.minimum_cash_balance,
                'maximum_loan_amount': self.maximum_loan_amount
            }
        }
    
    def select_best_scenario(self) -> Optional[Dict]:
        """
        Select the best scenario based on the optimization objective.
        
        Returns:
            Best scenario dictionary or None if no valid scenarios
        """
        if not self.valid_scenarios:
            return None
        
        if self.objective == "minimize_buyer_equity":
            return min(self.valid_scenarios, key=lambda x: x['buyer_equity'])
        
        elif self.objective == "maximize_purchase_price":
            return max(self.valid_scenarios, key=lambda x: x['purchase_price'])
        
        elif self.objective == "maximize_dscr":
            return max(self.valid_scenarios, key=lambda x: x['dscr'])
        
        elif self.objective == "maximize_owner_income":
            return max(self.valid_scenarios, key=lambda x: x['owner_income'])
        
        else:
            # Default to minimize buyer equity
            return min(self.valid_scenarios, key=lambda x: x['buyer_equity'])
    
    def sort_scenarios_by_objective(self) -> List[Dict]:
        """
        Sort all valid scenarios by the optimization objective.
        
        Returns:
            Sorted list of scenarios
        """
        if not self.valid_scenarios:
            return []
        
        if self.objective == "minimize_buyer_equity":
            return sorted(self.valid_scenarios, key=lambda x: x['buyer_equity'])
        
        elif self.objective == "maximize_purchase_price":
            return sorted(self.valid_scenarios, key=lambda x: x['purchase_price'], reverse=True)
        
        elif self.objective == "maximize_dscr":
            return sorted(self.valid_scenarios, key=lambda x: x['dscr'], reverse=True)
        
        elif self.objective == "maximize_owner_income":
            return sorted(self.valid_scenarios, key=lambda x: x['owner_income'], reverse=True)
        
        else:
            # Default to minimize buyer equity
            return sorted(self.valid_scenarios, key=lambda x: x['buyer_equity'])


def run_deal_optimization(
    base_model_inputs: Dict,
    purchase_price: float,
    objective: str = "minimize_buyer_equity",
    minimum_dscr: float = 1.25,
    minimum_cash_balance: float = 5000.0,
    maximum_loan_amount: Optional[float] = None,
    buyer_equity_range: Optional[Tuple[float, float, float]] = None,
    seller_note_range: Optional[Tuple[float, float, float]] = None,
    working_capital_range: Optional[Tuple[float, float, float]] = None,
    max_iterations: int = 5000
) -> Dict:
    """
    Convenience function to run deal optimization.
    
    Args:
        base_model_inputs: Base model configuration
        purchase_price: Target purchase price
        objective: Optimization objective
        minimum_dscr: Minimum DSCR constraint
        minimum_cash_balance: Minimum cash balance constraint
        maximum_loan_amount: Maximum loan amount constraint (optional)
        buyer_equity_range: (min, max, step) for buyer equity
        seller_note_range: (min, max, step) for seller note
        working_capital_range: (min, max, step) for working capital
        max_iterations: Maximum scenarios to test
        
    Returns:
        Optimization results dictionary
    """
    optimizer = DealOptimizer(
        base_model_inputs=base_model_inputs,
        purchase_price=purchase_price,
        objective=objective,
        minimum_dscr=minimum_dscr,
        minimum_cash_balance=minimum_cash_balance,
        maximum_loan_amount=maximum_loan_amount,
        max_iterations=max_iterations
    )
    
    # Set custom ranges if provided
    if buyer_equity_range or seller_note_range or working_capital_range:
        optimizer.define_search_ranges(
            buyer_equity_range=buyer_equity_range,
            seller_note_range=seller_note_range,
            working_capital_range=working_capital_range
        )
    
    return optimizer.optimize()
