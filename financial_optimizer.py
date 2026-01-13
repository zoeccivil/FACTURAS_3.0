"""
Motor de Optimización Financiera

Calcula ajustes necesarios para alcanzar ratios financieros objetivo.
Utiliza programación lineal y análisis de escenarios múltiples.
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class AdjustmentCategory(Enum):
    """Categorías de ajustes financieros."""
    INCREASE_INCOME = "Incrementar Ingresos"
    REDUCE_EXPENSES = "Reducir Gastos"
    INCREASE_ASSETS = "Incrementar Activos"
    REDUCE_ASSETS = "Reducir Activos"
    INCREASE_LIABILITIES = "Incrementar Pasivos"
    REDUCE_LIABILITIES = "Reducir Pasivos"
    INCREASE_EQUITY = "Incrementar Capital"


class Priority(Enum):
    """Prioridad de acciones."""
    HIGH = "ALTA"
    MEDIUM = "MEDIA"
    LOW = "BAJA"


class Feasibility(Enum):
    """Factibilidad de implementación."""
    HIGH = "Alta"
    MEDIUM = "Media"
    LOW = "Baja"


@dataclass
class FinancialState:
    """Estado financiero completo."""
    # Balance General
    current_assets: float
    non_current_assets: float
    current_liabilities: float
    non_current_liabilities: float
    equity: float
    
    # Estado de Resultados
    revenue: float
    cogs: float  # Cost of Goods Sold
    operating_expenses: float
    financial_expenses: float
    net_income: float
    ebit: float  # Earnings Before Interest and Taxes
    
    # Detalles (opcionales)
    cash: float = 0.0
    accounts_receivable: float = 0.0
    inventory: float = 0.0
    accounts_payable: float = 0.0
    
    @property
    def total_assets(self) -> float:
        return self.current_assets + self.non_current_assets
    
    @property
    def total_liabilities(self) -> float:
        return self.current_liabilities + self.non_current_liabilities
    
    def calculate_ratios(self) -> Dict[str, float]:
        """Calcula todos los ratios financieros."""
        ratios = {}
        
        # Liquidez
        if self.current_liabilities > 0:
            ratios['current_ratio'] = self.current_assets / self.current_liabilities
            ratios['quick_ratio'] = (self.current_assets - self.inventory) / self.current_liabilities
            ratios['cash_ratio'] = self.cash / self.current_liabilities
        else:
            ratios['current_ratio'] = float('inf')
            ratios['quick_ratio'] = float('inf')
            ratios['cash_ratio'] = float('inf')
        
        # Endeudamiento
        if self.total_assets > 0:
            ratios['debt_ratio'] = self.total_liabilities / self.total_assets
        else:
            ratios['debt_ratio'] = 0.0
        
        if self.equity > 0:
            ratios['debt_to_equity'] = self.total_liabilities / self.equity
        else:
            ratios['debt_to_equity'] = float('inf')
        
        if self.financial_expenses > 0:
            ratios['interest_coverage'] = self.ebit / self.financial_expenses
        else:
            ratios['interest_coverage'] = float('inf')
        
        # Rentabilidad
        if self.total_assets > 0:
            ratios['roa'] = self.net_income / self.total_assets
        else:
            ratios['roa'] = 0.0
        
        if self.equity > 0:
            ratios['roe'] = self.net_income / self.equity
        else:
            ratios['roe'] = 0.0
        
        if self.revenue > 0:
            ratios['net_margin'] = self.net_income / self.revenue
            ratios['operating_margin'] = (self.revenue - self.cogs - self.operating_expenses) / self.revenue
        else:
            ratios['net_margin'] = 0.0
            ratios['operating_margin'] = 0.0
        
        # Eficiencia
        if self.total_assets > 0:
            ratios['asset_turnover'] = self.revenue / self.total_assets
        else:
            ratios['asset_turnover'] = 0.0
        
        if self.revenue > 0 and self.accounts_receivable > 0:
            ratios['days_receivable'] = (self.accounts_receivable / self.revenue) * 365
        else:
            ratios['days_receivable'] = 0.0
        
        if self.cogs > 0 and self.accounts_payable > 0:
            ratios['days_payable'] = (self.accounts_payable / self.cogs) * 365
        else:
            ratios['days_payable'] = 0.0
        
        return ratios


@dataclass
class Adjustment:
    """Ajuste individual propuesto."""
    category: AdjustmentCategory
    description: str
    amount: float  # Positivo = aumentar, Negativo = reducir
    account_affected: str
    priority: Priority
    feasibility: Feasibility
    timeframe_days: int
    impact_on_ratios: Dict[str, float]
    implementation_notes: str = ""


@dataclass
class Scenario:
    """Escenario de optimización completo."""
    name: str
    description: str
    adjustments: List[Adjustment]
    projected_state: FinancialState
    meets_constraints: bool
    constraint_violations: List[str]
    total_impact: Dict[str, float]  # Cambio en cada ratio
    feasibility_score: float  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH


class FinancialOptimizer:
    """
    Motor de optimización financiera.
    
    Genera escenarios para alcanzar ratios objetivo cumpliendo restricciones.
    """
    
    def __init__(self, current_state: FinancialState):
        self.current_state = current_state
        self.current_ratios = current_state.calculate_ratios()
    
    def optimize(
        self,
        target_ratios: Dict[str, float],
        constraints: Dict[str, float],
        preferences: Optional[Dict[str, str]] = None
    ) -> List[Scenario]:
        """
        Genera escenarios de optimización.
        
        Args:
            target_ratios: {'roa': 0.12, 'roe': 0.15, ...}
            constraints: {'min_current_ratio': 1.5, 'max_debt_ratio': 0.6, ...}
            preferences: {'prefer': 'increase_income', 'avoid': 'reduce_assets'}
        
        Returns:
            Lista de escenarios ordenados por factibilidad.
        """
        scenarios = []
        
        # Escenario 1: Incrementar Rentabilidad (Conservador)
        scenario1 = self._generate_profitability_scenario(target_ratios, constraints)
        if scenario1:
            scenarios.append(scenario1)
        
        # Escenario 2: Reducir Activos (Agresivo)
        scenario2 = self._generate_asset_reduction_scenario(target_ratios, constraints)
        if scenario2:
            scenarios.append(scenario2)
        
        # Escenario 3: Balanceado (Recomendado)
        scenario3 = self._generate_balanced_scenario(target_ratios, constraints)
        if scenario3:
            scenarios.append(scenario3)
        
        # Escenario 4: Reestructuración de Pasivos
        scenario4 = self._generate_liability_restructure_scenario(target_ratios, constraints)
        if scenario4:
            scenarios.append(scenario4)
        
        # Escenario 5: Aumento de Capital
        scenario5 = self._generate_equity_increase_scenario(target_ratios, constraints)
        if scenario5:
            scenarios.append(scenario5)
        
        # Ordenar por factibilidad
        scenarios.sort(key=lambda s: s.feasibility_score, reverse=True)
        
        return scenarios
    
    def _generate_profitability_scenario(
        self,
        target_ratios: Dict[str, float],
        constraints: Dict[str, float]
    ) -> Optional[Scenario]:
        """
        Escenario 1: Incrementar utilidad neta sin cambiar estructura de activos/pasivos.
        """
        target_roa = target_ratios.get('roa', self.current_ratios['roa'])
        target_roe = target_ratios.get('roe', self.current_ratios['roe'])
        
        # Calcular utilidad neta necesaria
        required_net_income_roa = target_roa * self.current_state.total_assets
        required_net_income_roe = target_roe * self.current_state.equity
        
        # Usar el mayor de los dos
        required_net_income = max(required_net_income_roa, required_net_income_roe)
        income_gap = required_net_income - self.current_state.net_income
        
        if income_gap <= 0:
            return None  # Ya se cumplen los objetivos
        
        adjustments = []
        
        # Ajuste 1: Incrementar ingresos (60% del gap)
        revenue_increase = income_gap * 0.6 / 0.7  # Asumiendo margen neto 70% después de gastos
        adjustments.append(Adjustment(
            category=AdjustmentCategory.INCREASE_INCOME,
            description=f"Incrementar ingresos mediante nuevos clientes o aumento de precios",
            amount=revenue_increase,
            account_affected="4.1.1.001",
            priority=Priority.HIGH,
            feasibility=Feasibility.MEDIUM,
            timeframe_days=60,
            impact_on_ratios={
                'roa': (required_net_income / self.current_state.total_assets) - self.current_ratios['roa'],
                'roe': (required_net_income / self.current_state.equity) - self.current_ratios['roe']
            },
            implementation_notes="Estrategias: marketing digital, ventas cruzadas, ajuste de precios"
        ))
        
        # Ajuste 2: Reducir gastos operativos (40% del gap)
        expense_reduction = income_gap * 0.4
        adjustments.append(Adjustment(
            category=AdjustmentCategory.REDUCE_EXPENSES,
            description=f"Optimizar gastos operativos y administrativos",
            amount=-expense_reduction,
            account_affected="5.2.1",
            priority=Priority.MEDIUM,
            feasibility=Feasibility.HIGH,
            timeframe_days=30,
            impact_on_ratios={
                'net_margin': expense_reduction / self.current_state.revenue
            },
            implementation_notes="Renegociar contratos, eliminar redundancias, automatizar procesos"
        ))
        
        # Proyectar nuevo estado
        projected = FinancialState(
            current_assets=self.current_state.current_assets,
            non_current_assets=self.current_state.non_current_assets,
            current_liabilities=self.current_state.current_liabilities,
            non_current_liabilities=self.current_state.non_current_liabilities,
            equity=self.current_state.equity,
            revenue=self.current_state.revenue + revenue_increase,
            cogs=self.current_state.cogs,
            operating_expenses=self.current_state.operating_expenses - expense_reduction,
            financial_expenses=self.current_state.financial_expenses,
            net_income=required_net_income,
            ebit=self.current_state.ebit + income_gap,
            cash=self.current_state.cash,
            accounts_receivable=self.current_state.accounts_receivable,
            inventory=self.current_state.inventory,
            accounts_payable=self.current_state.accounts_payable
        )
        
        # Validar restricciones
        projected_ratios = projected.calculate_ratios()
        violations = self._check_constraints(projected_ratios, constraints)
        
        # Calcular impacto total
        total_impact = {}
        for ratio_name in self.current_ratios:
            if ratio_name in projected_ratios:
                total_impact[ratio_name] = projected_ratios[ratio_name] - self.current_ratios[ratio_name]
        
        return Scenario(
            name="Incrementar Rentabilidad",
            description="Enfoque en aumentar utilidad neta mediante incremento de ingresos y reducción de gastos",
            adjustments=adjustments,
            projected_state=projected,
            meets_constraints=len(violations) == 0,
            constraint_violations=violations,
            total_impact=total_impact,
            feasibility_score=75.0,
            risk_level="MEDIUM"
        )
    
    def _generate_asset_reduction_scenario(
        self,
        target_ratios: Dict[str, float],
        constraints: Dict[str, float]
    ) -> Optional[Scenario]:
        """
        Escenario 2: Reducir activos totales para mejorar ROA.
        """
        target_roa = target_ratios.get('roa', self.current_ratios['roa'])
        
        # Calcular activos totales necesarios
        if target_roa > 0:
            required_assets = self.current_state.net_income / target_roa
        else:
            return None
        
        asset_reduction = self.current_state.total_assets - required_assets
        
        if asset_reduction <= 0:
            return None
        
        adjustments = []
        
        # Distribuir la reducción
        # 50% de cuentas por cobrar
        if self.current_state.accounts_receivable > 0:
            ar_reduction = min(asset_reduction * 0.5, self.current_state.accounts_receivable * 0.4)
            adjustments.append(Adjustment(
                category=AdjustmentCategory.REDUCE_ASSETS,
                description="Cobrar cartera vencida y mejorar políticas de crédito",
                amount=-ar_reduction,
                account_affected="1.1.2.001",
                priority=Priority.HIGH,
                feasibility=Feasibility.MEDIUM,
                timeframe_days=45,
                impact_on_ratios={
                    'roa': self.current_state.net_income / (self.current_state.total_assets - ar_reduction) - self.current_ratios['roa']
                },
                implementation_notes="Contactar clientes morosos, ofrecer descuentos por pronto pago"
            ))
        
        # 30% de inventario
        if self.current_state.inventory > 0:
            inv_reduction = min(asset_reduction * 0.3, self.current_state.inventory * 0.3)
            adjustments.append(Adjustment(
                category=AdjustmentCategory.REDUCE_ASSETS,
                description="Liquidar inventario obsoleto o de lenta rotación",
                amount=-inv_reduction,
                account_affected="1.1.3.001",
                priority=Priority.MEDIUM,
                feasibility=Feasibility.MEDIUM,
                timeframe_days=60,
                impact_on_ratios={},
                implementation_notes="Promociones, ventas flash, descuentos por volumen"
            ))
        
        # 20% de activos fijos
        remaining = asset_reduction - sum(abs(a.amount) for a in adjustments)
        if remaining > 0:
            adjustments.append(Adjustment(
                category=AdjustmentCategory.REDUCE_ASSETS,
                description="Vender activos fijos no productivos o subutilizados",
                amount=-remaining,
                account_affected="1.2.1",
                priority=Priority.LOW,
                feasibility=Feasibility.LOW,
                timeframe_days=90,
                impact_on_ratios={},
                implementation_notes="Equipos obsoletos, vehículos en desuso, propiedades no operativas"
            ))
        
        # Proyectar nuevo estado
        total_reduction = sum(abs(a.amount) for a in adjustments)
        ar_reduction_total = sum(abs(a.amount) for a in adjustments if "cobrar" in a.description.lower())
        inv_reduction_total = sum(abs(a.amount) for a in adjustments if "inventario" in a.description.lower())
        fixed_reduction_total = sum(abs(a.amount) for a in adjustments if "activos fijos" in a.description.lower() or "vender" in a.description.lower())
        
        projected = FinancialState(
            current_assets=self.current_state.current_assets - ar_reduction_total - inv_reduction_total,
            non_current_assets=self.current_state.non_current_assets - fixed_reduction_total,
            current_liabilities=self.current_state.current_liabilities,
            non_current_liabilities=self.current_state.non_current_liabilities,
            equity=self.current_state.equity,
            revenue=self.current_state.revenue,
            cogs=self.current_state.cogs,
            operating_expenses=self.current_state.operating_expenses,
            financial_expenses=self.current_state.financial_expenses,
            net_income=self.current_state.net_income,
            ebit=self.current_state.ebit,
            cash=self.current_state.cash + total_reduction,  # El efectivo aumenta por las ventas
            accounts_receivable=self.current_state.accounts_receivable - ar_reduction_total,
            inventory=self.current_state.inventory - inv_reduction_total,
            accounts_payable=self.current_state.accounts_payable
        )
        
        projected_ratios = projected.calculate_ratios()
        violations = self._check_constraints(projected_ratios, constraints)
        
        total_impact = {}
        for ratio_name in self.current_ratios:
            if ratio_name in projected_ratios:
                total_impact[ratio_name] = projected_ratios[ratio_name] - self.current_ratios[ratio_name]
        
        # Penalizar si afecta liquidez
        feasibility = 60.0
        if projected_ratios.get('current_ratio', 0) < constraints.get('min_current_ratio', 1.5):
            feasibility = 35.0
        
        return Scenario(
            name="Reducir Activos",
            description="Optimización agresiva de activos para mejorar eficiencia",
            adjustments=adjustments,
            projected_state=projected,
            meets_constraints=len(violations) == 0,
            constraint_violations=violations,
            total_impact=total_impact,
            feasibility_score=feasibility,
            risk_level="HIGH"
        )
    
    def _generate_balanced_scenario(
        self,
        target_ratios: Dict[str, float],
        constraints: Dict[str, float]
    ) -> Optional[Scenario]:
        """
        Escenario 3: Combinación balanceada de ajustes.
        """
        target_roa = target_ratios.get('roa', self.current_ratios['roa'])
        target_roe = target_ratios.get('roe', self.current_ratios['roe'])
        
        # Calcular gaps
        required_net_income_roa = target_roa * self.current_state.total_assets
        required_net_income_roe = target_roe * self.current_state.equity
        required_net_income = max(required_net_income_roa, required_net_income_roe)
        income_gap = required_net_income - self.current_state.net_income
        
        if income_gap <= 0:
            return None
        
        adjustments = []
        
        # 1. Incrementar utilidad (40% del gap)
        revenue_increase = (income_gap * 0.4) / 0.65  # Margen 65%
        adjustments.append(Adjustment(
            category=AdjustmentCategory.INCREASE_INCOME,
            description="Incrementar ventas mediante expansión de servicios",
            amount=revenue_increase,
            account_affected="4.1.1.001",
            priority=Priority.HIGH,
            feasibility=Feasibility.HIGH,
            timeframe_days=45,
            impact_on_ratios={},
            implementation_notes="Campañas marketing, nuevos productos/servicios"
        ))
        
        # 2. Reducir gastos (20% del gap)
        expense_reduction = income_gap * 0.2
        adjustments.append(Adjustment(
            category=AdjustmentCategory.REDUCE_EXPENSES,
            description="Optimizar estructura de costos operativos",
            amount=-expense_reduction,
            account_affected="5.2.1",
            priority=Priority.MEDIUM,
            feasibility=Feasibility.HIGH,
            timeframe_days=30,
            impact_on_ratios={},
            implementation_notes="Automatización, renegociación proveedores"
        ))
        
        # 3. Reducir activos (25% del gap traducido a activos)
        asset_reduction_value = (income_gap * 0.25) / target_roa if target_roa > 0 else 0
        
        # Cobrar cartera
        if self.current_state.accounts_receivable > 0 and asset_reduction_value > 0:
            ar_reduction = min(asset_reduction_value * 0.6, self.current_state.accounts_receivable * 0.25)
            adjustments.append(Adjustment(
                category=AdjustmentCategory.REDUCE_ASSETS,
                description="Mejorar gestión de cobranza",
                amount=-ar_reduction,
                account_affected="1.1.2.001",
                priority=Priority.HIGH,
                feasibility=Feasibility.MEDIUM,
                timeframe_days=40,
                impact_on_ratios={},
                implementation_notes="Política de crédito más estricta, incentivos por pronto pago"
            ))
        
        # Reducir inventario
        if self.current_state.inventory > 0 and asset_reduction_value > 0:
            inv_reduction = min(asset_reduction_value * 0.4, self.current_state.inventory * 0.20)
            adjustments.append(Adjustment(
                category=AdjustmentCategory.REDUCE_ASSETS,
                description="Optimizar niveles de inventario",
                amount=-inv_reduction,
                account_affected="1.1.3.001",
                priority=Priority.MEDIUM,
                feasibility=Feasibility.HIGH,
                timeframe_days=50,
                impact_on_ratios={},
                implementation_notes="Just-in-time, reducir stock de seguridad"
            ))
        
        # 4. Reducir pasivos corrientes (15% del gap)
        if self.current_state.current_liabilities > 0:
            liability_reduction = min(income_gap * 0.15, self.current_state.current_liabilities * 0.20)
            adjustments.append(Adjustment(
                category=AdjustmentCategory.REDUCE_LIABILITIES,
                description="Pagar deuda de corto plazo con efectivo generado",
                amount=-liability_reduction,
                account_affected="2.1.1.001",
                priority=Priority.MEDIUM,
                feasibility=Feasibility.MEDIUM,
                timeframe_days=60,
                impact_on_ratios={
                    'current_ratio': 0.1  # Mejora estimada
                },
                implementation_notes="Usar flujo de caja mejorado para reducir pasivos"
            ))
        
        # Proyectar nuevo estado
        ar_reduction_total = sum(abs(a.amount) for a in adjustments if a.account_affected == "1.1.2.001")
        inv_reduction_total = sum(abs(a.amount) for a in adjustments if a.account_affected == "1.1.3.001")
        liability_reduction_total = sum(abs(a.amount) for a in adjustments if a.category == AdjustmentCategory.REDUCE_LIABILITIES)
        
        income_from_revenue = revenue_increase * 0.65  # Margen
        income_from_expenses = expense_reduction
        total_income_increase = income_from_revenue + income_from_expenses
        
        projected = FinancialState(
            current_assets=self.current_state.current_assets - ar_reduction_total - inv_reduction_total + total_income_increase,
            non_current_assets=self.current_state.non_current_assets,
            current_liabilities=self.current_state.current_liabilities - liability_reduction_total,
            non_current_liabilities=self.current_state.non_current_liabilities,
            equity=self.current_state.equity + total_income_increase,
            revenue=self.current_state.revenue + revenue_increase,
            cogs=self.current_state.cogs,
            operating_expenses=self.current_state.operating_expenses - expense_reduction,
            financial_expenses=self.current_state.financial_expenses,
            net_income=self.current_state.net_income + total_income_increase,
            ebit=self.current_state.ebit + total_income_increase,
            cash=self.current_state.cash + ar_reduction_total + inv_reduction_total - liability_reduction_total,
            accounts_receivable=self.current_state.accounts_receivable - ar_reduction_total,
            inventory=self.current_state.inventory - inv_reduction_total,
            accounts_payable=self.current_state.accounts_payable
        )
        
        projected_ratios = projected.calculate_ratios()
        violations = self._check_constraints(projected_ratios, constraints)
        
        total_impact = {}
        for ratio_name in self.current_ratios:
            if ratio_name in projected_ratios:
                total_impact[ratio_name] = projected_ratios[ratio_name] - self.current_ratios[ratio_name]
        
        return Scenario(
            name="Balanceado (Recomendado)",
            description="Combinación equilibrada de mejora de utilidad, optimización de activos y reducción de pasivos",
            adjustments=adjustments,
            projected_state=projected,
            meets_constraints=len(violations) == 0,
            constraint_violations=violations,
            total_impact=total_impact,
            feasibility_score=85.0,
            risk_level="LOW"
        )
    
    def _generate_liability_restructure_scenario(
        self,
        target_ratios: Dict[str, float],
        constraints: Dict[str, float]
    ) -> Optional[Scenario]:
        """
        Escenario 4: Reestructuración de pasivos.
        """
        target_debt_ratio = target_ratios.get('debt_ratio', self.current_ratios.get('debt_ratio', 0.5))
        
        if self.current_ratios.get('debt_ratio', 0) <= target_debt_ratio:
            return None  # Ya cumple
        
        # Calcular reducción de pasivos necesaria
        required_liabilities = target_debt_ratio * self.current_state.total_assets
        liability_reduction = self.current_state.total_liabilities - required_liabilities
        
        if liability_reduction <= 0:
            return None
        
        adjustments = []
        
        # Refinanciar deuda de corto a largo plazo
        refinance_amount = min(liability_reduction * 0.6, self.current_state.current_liabilities * 0.5)
        adjustments.append(Adjustment(
            category=AdjustmentCategory.REDUCE_LIABILITIES,
            description="Refinanciar deuda de corto plazo a largo plazo",
            amount=-refinance_amount,
            account_affected="2.1.3.001",
            priority=Priority.HIGH,
            feasibility=Feasibility.MEDIUM,
            timeframe_days=60,
            impact_on_ratios={
                'current_ratio': refinance_amount / self.current_state.current_liabilities if self.current_state.current_liabilities > 0 else 0
            },
            implementation_notes="Negociar con bancos términos más favorables"
        ))
        
        # Pagar deuda con efectivo generado
        pay_down_amount = liability_reduction - refinance_amount
        adjustments.append(Adjustment(
            category=AdjustmentCategory.REDUCE_LIABILITIES,
            description="Pagar deuda utilizando flujo de caja",
            amount=-pay_down_amount,
            account_affected="2.1.1.001",
            priority=Priority.MEDIUM,
            feasibility=Feasibility.MEDIUM,
            timeframe_days=90,
            impact_on_ratios={},
            implementation_notes="Usar excedentes de caja para amortización anticipada"
        ))
        
        projected = FinancialState(
            current_assets=self.current_state.current_assets,
            non_current_assets=self.current_state.non_current_assets,
            current_liabilities=self.current_state.current_liabilities - refinance_amount - (pay_down_amount * 0.7),
            non_current_liabilities=self.current_state.non_current_liabilities + refinance_amount - (pay_down_amount * 0.3),
            equity=self.current_state.equity,
            revenue=self.current_state.revenue,
            cogs=self.current_state.cogs,
            operating_expenses=self.current_state.operating_expenses,
            financial_expenses=self.current_state.financial_expenses * 0.9,  # Reducción por mejor términos
            net_income=self.current_state.net_income,
            ebit=self.current_state.ebit,
            cash=self.current_state.cash - pay_down_amount,
            accounts_receivable=self.current_state.accounts_receivable,
            inventory=self.current_state.inventory,
            accounts_payable=self.current_state.accounts_payable
        )
        
        projected_ratios = projected.calculate_ratios()
        violations = self._check_constraints(projected_ratios, constraints)
        
        total_impact = {}
        for ratio_name in self.current_ratios:
            if ratio_name in projected_ratios:
                total_impact[ratio_name] = projected_ratios[ratio_name] - self.current_ratios[ratio_name]
        
        return Scenario(
            name="Reestructuración de Pasivos",
            description="Optimización de estructura de deuda para mejorar ratios de endeudamiento y liquidez",
            adjustments=adjustments,
            projected_state=projected,
            meets_constraints=len(violations) == 0,
            constraint_violations=violations,
            total_impact=total_impact,
            feasibility_score=65.0,
            risk_level="MEDIUM"
        )
    
    def _generate_equity_increase_scenario(
        self,
        target_ratios: Dict[str, float],
        constraints: Dict[str, float]
    ) -> Optional[Scenario]:
        """
        Escenario 5: Aumento de capital.
        """
        target_roe = target_ratios.get('roe', self.current_ratios.get('roe', 0.15))
        
        # Calcular patrimonio necesario para mantener ROE con utilidad actual
        if target_roe > 0:
            required_equity = self.current_state.net_income / target_roe
        else:
            return None
        
        equity_increase = max(required_equity - self.current_state.equity, 0)
        
        if equity_increase < self.current_state.equity * 0.1:  # Menos del 10%
            return None
        
        adjustments = []
        
        adjustments.append(Adjustment(
            category=AdjustmentCategory.INCREASE_EQUITY,
            description="Aporte de capital adicional por socios",
            amount=equity_increase,
            account_affected="3.1.1.002",
            priority=Priority.LOW,
            feasibility=Feasibility.LOW,
            timeframe_days=120,
            impact_on_ratios={
                'roe': target_roe - self.current_ratios.get('roe', 0),
                'debt_ratio': -0.05  # Mejora estimada
            },
            implementation_notes="Negociar con socios actuales o buscar nuevos inversionistas"
        ))
        
        projected = FinancialState(
            current_assets=self.current_state.current_assets + equity_increase,
            non_current_assets=self.current_state.non_current_assets,
            current_liabilities=self.current_state.current_liabilities,
            non_current_liabilities=self.current_state.non_current_liabilities,
            equity=self.current_state.equity + equity_increase,
            revenue=self.current_state.revenue,
            cogs=self.current_state.cogs,
            operating_expenses=self.current_state.operating_expenses,
            financial_expenses=self.current_state.financial_expenses,
            net_income=self.current_state.net_income,
            ebit=self.current_state.ebit,
            cash=self.current_state.cash + equity_increase,
            accounts_receivable=self.current_state.accounts_receivable,
            inventory=self.current_state.inventory,
            accounts_payable=self.current_state.accounts_payable
        )
        
        projected_ratios = projected.calculate_ratios()
        violations = self._check_constraints(projected_ratios, constraints)
        
        total_impact = {}
        for ratio_name in self.current_ratios:
            if ratio_name in projected_ratios:
                total_impact[ratio_name] = projected_ratios[ratio_name] - self.current_ratios[ratio_name]
        
        return Scenario(
            name="Aumento de Capital",
            description="Inyección de capital para fortalecer patrimonio y mejorar estructura financiera",
            adjustments=adjustments,
            projected_state=projected,
            meets_constraints=len(violations) == 0,
            constraint_violations=violations,
            total_impact=total_impact,
            feasibility_score=40.0,
            risk_level="LOW"
        )
    
    def _check_constraints(
        self,
        ratios: Dict[str, float],
        constraints: Dict[str, float]
    ) -> List[str]:
        """Verifica violaciones de restricciones."""
        violations = []
        
        # Liquidez mínima
        min_current = constraints.get('min_current_ratio', 0)
        if ratios.get('current_ratio', float('inf')) < min_current:
            violations.append(f"Razón corriente ({ratios.get('current_ratio', 0):.2f}) por debajo del mínimo ({min_current})")
        
        # Endeudamiento máximo
        max_debt = constraints.get('max_debt_ratio', 1.0)
        if ratios.get('debt_ratio', 0) > max_debt:
            violations.append(f"Endeudamiento ({ratios.get('debt_ratio', 0):.1%}) excede el máximo ({max_debt:.1%})")
        
        return violations
    
    def what_if_analysis(
        self,
        change_description: str,
        parameter: str,
        change_pct: float
    ) -> Dict[str, float]:
        """
        Análisis de sensibilidad "qué pasa si".
        
        Args:
            change_description: Descripción del cambio
            parameter: 'revenue', 'cogs', 'operating_expenses', etc.
            change_pct: Porcentaje de cambio (ej: 0.15 = +15%)
        
        Returns:
            Nuevos ratios proyectados
        """
        modified_state = FinancialState(
            current_assets=self.current_state.current_assets,
            non_current_assets=self.current_state.non_current_assets,
            current_liabilities=self.current_state.current_liabilities,
            non_current_liabilities=self.current_state.non_current_liabilities,
            equity=self.current_state.equity,
            revenue=self.current_state.revenue,
            cogs=self.current_state.cogs,
            operating_expenses=self.current_state.operating_expenses,
            financial_expenses=self.current_state.financial_expenses,
            net_income=self.current_state.net_income,
            ebit=self.current_state.ebit,
            cash=self.current_state.cash,
            accounts_receivable=self.current_state.accounts_receivable,
            inventory=self.current_state.inventory,
            accounts_payable=self.current_state.accounts_payable
        )
        
        # Aplicar cambio
        if parameter == 'revenue':
            change_amount = modified_state.revenue * change_pct
            modified_state.revenue += change_amount
            # Impacto en utilidad (asumiendo margen constante)
            margin = modified_state.net_income / modified_state.revenue if modified_state.revenue > 0 else 0
            modified_state.net_income += change_amount * margin
            modified_state.ebit += change_amount * margin * 1.2  # Aproximación
        
        elif parameter == 'cogs':
            change_amount = modified_state.cogs * change_pct
            modified_state.cogs += change_amount
            modified_state.net_income -= change_amount
            modified_state.ebit -= change_amount
        
        elif parameter == 'operating_expenses':
            change_amount = modified_state.operating_expenses * change_pct
            modified_state.operating_expenses += change_amount
            modified_state.net_income -= change_amount
            modified_state.ebit -= change_amount
        
        return modified_state.calculate_ratios()
