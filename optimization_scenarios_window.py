"""
Ventana del Optimizador Financiero.

Muestra ratios actuales, permite configurar objetivos y genera escenarios
de optimización para alcanzar ratios financieros objetivo.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QTabWidget,
    QWidget,
    QTextEdit,
    QLineEdit,
    QCheckBox,
    QGroupBox,
    QScrollArea,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont
import traceback


class OptimizationScenariosWindow(QDialog):
    """
    Ventana principal del Optimizador Financiero.
    
    Muestra:
    - Ratios actuales vs objetivo
    - Escenarios generados
    - Detalles de ajustes recomendados
    - Plan de acción
    """
    
    def __init__(
        self,
        parent,
        controller,
        company_id,
        company_name: str,
        month_str: str,
        year_int: int,
    ):
        super().__init__(parent)
        self.controller = controller
        self.company_id = company_id
        self.company_name = company_name
        self.month_str = month_str
        self.year_int = year_int
        
        self.current_state = None
        self.current_ratios = {}
        self.target_ratios = {}
        self.constraints = {}
        self.scenarios = []
        self.selected_scenario_idx = None

        self.setWindowTitle(f"Optimizador Financiero - {company_name}")
        self.resize(1200, 800)
        self.setModal(True)

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # === HEADER ===
        header_card = QFrame()
        header_card.setObjectName("headerCard")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(4)

        title = QLabel("🎯 Optimizador Financiero")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A;")
        
        period_name = self._get_period_name()
        subtitle = QLabel(f"{self.company_name} – {period_name}")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        root.addWidget(header_card)

        # === TABS ===
        tabs = QTabWidget()
        tabs.setObjectName("modernTabs")

        # Tab 1: Ratios Actuales
        tab_current = self._build_current_ratios_tab()
        tabs.addTab(tab_current, "📊 Situación Actual")

        # Tab 2: Configurar Objetivos
        tab_targets = self._build_targets_tab()
        tabs.addTab(tab_targets, "🎯 Configurar Objetivos")

        # Tab 3: Escenarios
        tab_scenarios = self._build_scenarios_tab()
        tabs.addTab(tab_scenarios, "⚙️ Escenarios de Optimización")

        # Tab 4: Plan de Acción
        tab_action = self._build_action_plan_tab()
        tabs.addTab(tab_action, "📋 Plan de Acción")

        root.addWidget(tabs)

        # === BOTONES GLOBALES ===
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_calculate = QPushButton("🧮 Calcular Escenarios")
        self.btn_calculate.setObjectName("primaryButton")
        self.btn_calculate.setMinimumHeight(40)
        self.btn_calculate.clicked.connect(self._calculate_scenarios)

        self.btn_save = QPushButton("💾 Guardar Configuración")
        self.btn_save.setObjectName("secondaryButton")
        self.btn_save.setMinimumHeight(40)
        self.btn_save.clicked.connect(self._save_configuration)

        btn_close = QPushButton("❌ Cerrar")
        btn_close.setObjectName("cancelButton")
        btn_close.setMinimumHeight(40)
        btn_close.clicked.connect(self.reject)

        btn_row.addStretch()
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_calculate)
        btn_row.addWidget(btn_close)

        root.addLayout(btn_row)

        self._apply_styles()

    def _build_current_ratios_tab(self) -> QWidget:
        """Tab 1: Muestra ratios actuales."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Estado Financiero Actual
        state_card = QFrame()
        state_card.setObjectName("dataCard")
        state_layout = QVBoxLayout(state_card)
        state_layout.setContentsMargins(20, 16, 20, 16)
        state_layout.setSpacing(12)

        state_title = QLabel("📊 Estado Financiero Actual")
        state_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        state_layout.addWidget(state_title)

        # Grid de valores
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(20)

        # Columna 1: Balance
        col1 = QVBoxLayout()
        col1.setSpacing(8)
        
        col1.addWidget(QLabel("BALANCE GENERAL"))
        
        self.lbl_current_assets = QLabel("Activos Corrientes: RD$ 0.00")
        self.lbl_non_current_assets = QLabel("Activos No Corrientes: RD$ 0.00")
        self.lbl_total_assets = QLabel("TOTAL ACTIVOS: RD$ 0.00")
        self.lbl_total_assets.setStyleSheet("font-weight: 700;")
        
        col1.addWidget(self.lbl_current_assets)
        col1.addWidget(self.lbl_non_current_assets)
        col1.addWidget(self.lbl_total_assets)
        col1.addSpacing(10)
        
        self.lbl_current_liab = QLabel("Pasivos Corrientes: RD$ 0.00")
        self.lbl_non_current_liab = QLabel("Pasivos No Corrientes: RD$ 0.00")
        self.lbl_total_liab = QLabel("TOTAL PASIVOS: RD$ 0.00")
        self.lbl_total_liab.setStyleSheet("font-weight: 700;")
        
        col1.addWidget(self.lbl_current_liab)
        col1.addWidget(self.lbl_non_current_liab)
        col1.addWidget(self.lbl_total_liab)
        col1.addSpacing(10)
        
        self.lbl_equity = QLabel("PATRIMONIO: RD$ 0.00")
        self.lbl_equity.setStyleSheet("font-weight: 700;")
        col1.addWidget(self.lbl_equity)

        grid_layout.addLayout(col1)

        # Columna 2: P&L
        col2 = QVBoxLayout()
        col2.setSpacing(8)
        
        col2.addWidget(QLabel("ESTADO DE RESULTADOS"))
        
        self.lbl_revenue = QLabel("Ingresos: RD$ 0.00")
        self.lbl_cogs = QLabel("Costo de Ventas: RD$ 0.00")
        self.lbl_op_exp = QLabel("Gastos Operativos: RD$ 0.00")
        self.lbl_ebit = QLabel("EBIT: RD$ 0.00")
        self.lbl_fin_exp = QLabel("Gastos Financieros: RD$ 0.00")
        self.lbl_net_income = QLabel("UTILIDAD NETA: RD$ 0.00")
        self.lbl_net_income.setStyleSheet("font-weight: 700; font-size: 14px;")
        
        col2.addWidget(self.lbl_revenue)
        col2.addWidget(self.lbl_cogs)
        col2.addWidget(self.lbl_op_exp)
        col2.addWidget(self.lbl_ebit)
        col2.addWidget(self.lbl_fin_exp)
        col2.addSpacing(10)
        col2.addWidget(self.lbl_net_income)

        grid_layout.addLayout(col2)

        state_layout.addLayout(grid_layout)
        layout.addWidget(state_card)

        # Ratios Actuales
        ratios_card = QFrame()
        ratios_card.setObjectName("dataCard")
        ratios_layout = QVBoxLayout(ratios_card)
        ratios_layout.setContentsMargins(20, 16, 20, 16)
        ratios_layout.setSpacing(12)

        ratios_title = QLabel("📈 Ratios Financieros Actuales")
        ratios_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        ratios_layout.addWidget(ratios_title)

        # Tabla de ratios
        self.ratios_table = QTableWidget()
        self.ratios_table.setObjectName("modernTable")
        self.ratios_table.setColumnCount(4)
        self.ratios_table.setHorizontalHeaderLabels(["Categoría", "Ratio", "Valor Actual", "Estado"])
        
        header = self.ratios_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.ratios_table.setAlternatingRowColors(True)
        self.ratios_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ratios_table.verticalHeader().setDefaultSectionSize(35)

        ratios_layout.addWidget(self.ratios_table)
        layout.addWidget(ratios_card)

        layout.addStretch()

        return widget

    def _build_targets_tab(self) -> QWidget:
        """Tab 2: Configurar ratios objetivo."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("modernScroll")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(16)

        # Grupo: Objetivos
        targets_group = QGroupBox("🎯 Ratios Objetivo")
        targets_group.setObjectName("modernGroup")
        targets_layout = QVBoxLayout(targets_group)
        targets_layout.setSpacing(12)

        # ROA
        row_roa = QHBoxLayout()
        row_roa.setSpacing(12)
        row_roa.addWidget(QLabel("ROA (Return on Assets):"))
        self.input_roa = QLineEdit()
        self.input_roa.setObjectName("modernInput")
        self.input_roa.setPlaceholderText("12.0")
        self.input_roa.setMaximumWidth(100)
        row_roa.addWidget(self.input_roa)
        row_roa.addWidget(QLabel("%"))
        row_roa.addWidget(QLabel("(Recomendado: 10-15%)"))
        row_roa.addStretch()
        targets_layout.addLayout(row_roa)

        # ROE
        row_roe = QHBoxLayout()
        row_roe.setSpacing(12)
        row_roe.addWidget(QLabel("ROE (Return on Equity):"))
        self.input_roe = QLineEdit()
        self.input_roe.setObjectName("modernInput")
        self.input_roe.setPlaceholderText("15.0")
        self.input_roe.setMaximumWidth(100)
        row_roe.addWidget(self.input_roe)
        row_roe.addWidget(QLabel("%"))
        row_roe.addWidget(QLabel("(Recomendado: 12-18%)"))
        row_roe.addStretch()
        targets_layout.addLayout(row_roe)

        # Razón Corriente
        row_current = QHBoxLayout()
        row_current.setSpacing(12)
        row_current.addWidget(QLabel("Razón Corriente:"))
        self.input_current_ratio = QLineEdit()
        self.input_current_ratio.setObjectName("modernInput")
        self.input_current_ratio.setPlaceholderText("2.0")
        self.input_current_ratio.setMaximumWidth(100)
        row_current.addWidget(self.input_current_ratio)
        row_current.addWidget(QLabel("(Recomendado: 1.5-2.5)"))
        row_current.addStretch()
        targets_layout.addLayout(row_current)

        # Endeudamiento
        row_debt = QHBoxLayout()
        row_debt.setSpacing(12)
        row_debt.addWidget(QLabel("Endeudamiento Total:"))
        self.input_debt_ratio = QLineEdit()
        self.input_debt_ratio.setObjectName("modernInput")
        self.input_debt_ratio.setPlaceholderText("40.0")
        self.input_debt_ratio.setMaximumWidth(100)
        row_debt.addWidget(self.input_debt_ratio)
        row_debt.addWidget(QLabel("%"))
        row_debt.addWidget(QLabel("(Recomendado: 30-50%)"))
        row_debt.addStretch()
        targets_layout.addLayout(row_debt)

        # Margen Neto
        row_margin = QHBoxLayout()
        row_margin.setSpacing(12)
        row_margin.addWidget(QLabel("Margen Neto:"))
        self.input_net_margin = QLineEdit()
        self.input_net_margin.setObjectName("modernInput")
        self.input_net_margin.setPlaceholderText("10.0")
        self.input_net_margin.setMaximumWidth(100)
        row_margin.addWidget(self.input_net_margin)
        row_margin.addWidget(QLabel("%"))
        row_margin.addWidget(QLabel("(Recomendado: 8-12%)"))
        row_margin.addStretch()
        targets_layout.addLayout(row_margin)

        scroll_layout.addWidget(targets_group)

        # Grupo: Restricciones
        constraints_group = QGroupBox("⚠️ Restricciones")
        constraints_group.setObjectName("modernGroup")
        constraints_layout = QVBoxLayout(constraints_group)
        constraints_layout.setSpacing(12)

        # Liquidez mínima
        row_min_current = QHBoxLayout()
        row_min_current.setSpacing(12)
        self.chk_min_current = QCheckBox("Mantener liquidez mínima:")
        self.chk_min_current.setChecked(True)
        row_min_current.addWidget(self.chk_min_current)
        self.input_min_current = QLineEdit()
        self.input_min_current.setObjectName("modernInput")
        self.input_min_current.setPlaceholderText("1.5")
        self.input_min_current.setMaximumWidth(100)
        row_min_current.addWidget(self.input_min_current)
        row_min_current.addStretch()
        constraints_layout.addLayout(row_min_current)

        # Endeudamiento máximo
        row_max_debt = QHBoxLayout()
        row_max_debt.setSpacing(12)
        self.chk_max_debt = QCheckBox("No exceder endeudamiento:")
        self.chk_max_debt.setChecked(True)
        row_max_debt.addWidget(self.chk_max_debt)
        self.input_max_debt = QLineEdit()
        self.input_max_debt.setObjectName("modernInput")
        self.input_max_debt.setPlaceholderText("60.0")
        self.input_max_debt.setMaximumWidth(100)
        row_max_debt.addWidget(self.input_max_debt)
        row_max_debt.addWidget(QLabel("%"))
        row_max_debt.addStretch()
        constraints_layout.addLayout(row_max_debt)

        # Efectivo mínimo
        row_min_cash = QHBoxLayout()
        row_min_cash.setSpacing(12)
        self.chk_min_cash = QCheckBox("Mantener efectivo mínimo:")
        self.chk_min_cash.setChecked(False)
        row_min_cash.addWidget(self.chk_min_cash)
        self.input_min_cash = QLineEdit()
        self.input_min_cash.setObjectName("modernInput")
        self.input_min_cash.setPlaceholderText("100000")
        self.input_min_cash.setMaximumWidth(150)
        row_min_cash.addWidget(self.input_min_cash)
        row_min_cash.addWidget(QLabel("RD$"))
        row_min_cash.addStretch()
        constraints_layout.addLayout(row_min_cash)

        scroll_layout.addWidget(constraints_group)

        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        return widget

    def _build_scenarios_tab(self) -> QWidget:
        """Tab 3: Escenarios generados."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        info = QLabel("Los escenarios se generarán después de hacer clic en 'Calcular Escenarios'")
        info.setStyleSheet("color: #64748B; font-style: italic;")
        layout.addWidget(info)

        # Lista de escenarios
        self.scenarios_list = QTableWidget()
        self.scenarios_list.setObjectName("modernTable")
        self.scenarios_list.setColumnCount(5)
        self.scenarios_list.setHorizontalHeaderLabels([
            "Escenario", "Factibilidad", "Riesgo", "Cumple Restricciones", "Acciones"
        ])
        
        header = self.scenarios_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.scenarios_list.setColumnWidth(4, 120)
        
        self.scenarios_list.setAlternatingRowColors(True)
        self.scenarios_list.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.scenarios_list.verticalHeader().setDefaultSectionSize(45)

        layout.addWidget(self.scenarios_list)

        # Detalles del escenario seleccionado
        details_card = QFrame()
        details_card.setObjectName("dataCard")
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(20, 16, 20, 16)
        details_layout.setSpacing(12)

        details_title = QLabel("📋 Detalles del Escenario")
        details_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        details_layout.addWidget(details_title)

        self.scenario_details = QTextEdit()
        self.scenario_details.setObjectName("modernTextEdit")
        self.scenario_details.setReadOnly(True)
        self.scenario_details.setMaximumHeight(200)
        self.scenario_details.setPlaceholderText("Selecciona un escenario para ver sus detalles...")

        details_layout.addWidget(self.scenario_details)
        layout.addWidget(details_card)

        return widget

    def _build_action_plan_tab(self) -> QWidget:
        """Tab 4: Plan de acción."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        info = QLabel("El plan de acción se generará al seleccionar un escenario")
        info.setStyleSheet("color: #64748B; font-style: italic;")
        layout.addWidget(info)

        # Tabla de acciones
        self.action_table = QTableWidget()
        self.action_table.setObjectName("modernTable")
        self.action_table.setColumnCount(5)
        self.action_table.setHorizontalHeaderLabels([
            "Prioridad", "Acción", "Monto", "Plazo", "Factibilidad"
        ])
        
        header = self.action_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.action_table.setAlternatingRowColors(True)
        self.action_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.action_table.verticalHeader().setDefaultSectionSize(40)

        layout.addWidget(self.action_table)

        # Resumen del impacto
        impact_card = QFrame()
        impact_card.setObjectName("totalCard")
        impact_layout = QVBoxLayout(impact_card)
        impact_layout.setContentsMargins(20, 16, 20, 16)
        impact_layout.setSpacing(12)

        impact_title = QLabel("📊 Impacto Proyectado")
        impact_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")
        impact_layout.addWidget(impact_title)

        self.impact_summary = QLabel("Selecciona un escenario para ver el impacto proyectado")
        self.impact_summary.setStyleSheet("font-size: 13px; color: #475569;")
        self.impact_summary.setWordWrap(True)
        impact_layout.addWidget(self.impact_summary)

        layout.addWidget(impact_card)

        return widget

    def _apply_styles(self):
        """Aplica estilos modernos."""
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
            }
            
            QFrame#headerCard, QFrame#dataCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
            
            QFrame#totalCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 2px solid #3B82F6;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EFF6FF,
                    stop:1 #FFFFFF
                );
            }
            
            QLineEdit#modernInput {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 12px;
                color: #0F172A;
                font-size: 13px;
            }
            
            QLineEdit#modernInput:focus {
                border-color: #3B82F6;
                border-width: 2px;
            }
            
            QTextEdit#modernTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                color: #0F172A;
                font-size: 13px;
            }
            
            QTableWidget#modernTable {
                background-color: #FFFFFF;
                alternate-background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #E5E7EB;
                color: #0F172A;
            }
            
            QTableWidget#modernTable::item {
                padding: 8px;
            }
            
            QHeaderView::section {
                background-color: #F1F5F9;
                border: none;
                padding: 10px 8px;
                color: #475569;
                font-weight: 700;
                font-size: 12px;
            }
            
            QTabWidget#modernTabs::pane {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background-color: #FFFFFF;
            }
            
            QTabWidget#modernTabs::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin-right: 4px;
                color: #64748B;
                font-weight: 600;
            }
            
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #1E293B;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #F1F5F9;
            }
            
            QGroupBox#modernGroup {
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: 700;
                color: #1E293B;
            }
            
            QGroupBox#modernGroup::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QPushButton#primaryButton {
                background-color: #3B82F6;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 180px;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #2563EB;
            }
            
            QPushButton#secondaryButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 180px;
            }
            
            QPushButton#secondaryButton:hover {
                background-color: #059669;
            }
            
            QPushButton#cancelButton {
                background-color: #F9FAFB;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                font-size: 14px;
                min-width: 120px;
            }
            
            QPushButton#cancelButton:hover {
                background-color: #E5E7EB;
            }
            
            QPushButton#viewButton {
                background-color: #3B82F6;
                color: #FFFFFF;
                padding: 6px 12px;
                border-radius: 6px;
                border: none;
                font-weight: 600;
                font-size: 12px;
            }
            
            QPushButton#viewButton:hover {
                background-color: #2563EB;
            }
            
            QScrollArea#modernScroll {
                border: none;
                background-color: transparent;
            }
        """)

    def _get_period_name(self) -> str:
        """Devuelve el nombre del periodo."""
        months = {
            "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
            "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
            "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
        }
        
        if self.month_str:
            month_name = months.get(self.month_str, self.month_str)
            return f"{month_name} {self.year_int}"
        else:
            return f"Año {self.year_int}"

    def _load_data(self):
        """Carga datos iniciales."""
        try:
            # Cargar estado financiero
            if hasattr(self.controller, "get_financial_state"):
                state_dict = self.controller.get_financial_state(
                    self.company_id,
                    self.month_str,
                    self.year_int
                )
                
                if state_dict:
                    from financial_optimizer import FinancialState
                    self.current_state = FinancialState(**state_dict)
                    self.current_ratios = self.current_state.calculate_ratios()
                    
                    self._update_current_state_display()
                    self._update_ratios_table()
            
            # Cargar objetivos guardados
            if hasattr(self.controller, "get_financial_targets"):
                period = f"{self.year_int}-{self.month_str}" if self.month_str else f"{self.year_int}"
                targets_data = self.controller.get_financial_targets(self.company_id, period)
                
                if targets_data:
                    self.target_ratios = targets_data.get('targets', {})
                    self.constraints = targets_data.get('constraints', {})
                    
                    self._load_targets_into_inputs()

        except Exception as e:
            print(f"[OPTIMIZER] Error loading data: {e}")
            traceback.print_exc()
            QMessageBox.warning(self, "Error", f"Error cargando datos:\n{e}")

    def _update_current_state_display(self):
        """Actualiza los labels del estado financiero actual."""
        if not self.current_state:
            return
        
        # Balance
        self.lbl_current_assets.setText(f"Activos Corrientes: RD$ {self.current_state.current_assets:,.2f}")
        self.lbl_non_current_assets.setText(f"Activos No Corrientes: RD$ {self.current_state.non_current_assets:,.2f}")
        self.lbl_total_assets.setText(f"TOTAL ACTIVOS: RD$ {self.current_state.total_assets:,.2f}")
        
        self.lbl_current_liab.setText(f"Pasivos Corrientes: RD$ {self.current_state.current_liabilities:,.2f}")
        self.lbl_non_current_liab.setText(f"Pasivos No Corrientes: RD$ {self.current_state.non_current_liabilities:,.2f}")
        self.lbl_total_liab.setText(f"TOTAL PASIVOS: RD$ {self.current_state.total_liabilities:,.2f}")
        
        self.lbl_equity.setText(f"PATRIMONIO: RD$ {self.current_state.equity:,.2f}")
        
        # P&L
        self.lbl_revenue.setText(f"Ingresos: RD$ {self.current_state.revenue:,.2f}")
        self.lbl_cogs.setText(f"Costo de Ventas: RD$ {self.current_state.cogs:,.2f}")
        self.lbl_op_exp.setText(f"Gastos Operativos: RD$ {self.current_state.operating_expenses:,.2f}")
        self.lbl_ebit.setText(f"EBIT: RD$ {self.current_state.ebit:,.2f}")
        self.lbl_fin_exp.setText(f"Gastos Financieros: RD$ {self.current_state.financial_expenses:,.2f}")
        self.lbl_net_income.setText(f"UTILIDAD NETA: RD$ {self.current_state.net_income:,.2f}")

    def _update_ratios_table(self):
        """Actualiza la tabla de ratios actuales."""
        self.ratios_table.setRowCount(0)
        
        ratios_data = [
            ("LIQUIDEZ", "Razón Corriente", self.current_ratios.get('current_ratio', 0), 1.5, 2.5),
            ("LIQUIDEZ", "Prueba Ácida", self.current_ratios.get('quick_ratio', 0), 1.0, 1.5),
            ("LIQUIDEZ", "Razón de Efectivo", self.current_ratios.get('cash_ratio', 0), 0.5, 1.0),
            ("ENDEUDAMIENTO", "Endeudamiento Total", self.current_ratios.get('debt_ratio', 0) * 100, 30, 50),
            ("ENDEUDAMIENTO", "Apalancamiento", self.current_ratios.get('debt_to_equity', 0), 0.5, 1.5),
            ("RENTABILIDAD", "ROA", self.current_ratios.get('roa', 0) * 100, 10, 15),
            ("RENTABILIDAD", "ROE", self.current_ratios.get('roe', 0) * 100, 12, 18),
            ("RENTABILIDAD", "Margen Neto", self.current_ratios.get('net_margin', 0) * 100, 8, 12),
            ("EFICIENCIA", "Rotación de Activos", self.current_ratios.get('asset_turnover', 0), 1.0, 2.0),
        ]
        
        for category, name, value, min_val, max_val in ratios_data:
            row = self.ratios_table.rowCount()
            self.ratios_table.insertRow(row)
            
            # Categoría
            self.ratios_table.setItem(row, 0, QTableWidgetItem(category))
            
            # Nombre
            self.ratios_table.setItem(row, 1, QTableWidgetItem(name))
            
            # Valor
            if "%" in name or category == "RENTABILIDAD" or category == "ENDEUDAMIENTO":
                value_str = f"{value:.1f}%"
            else:
                value_str = f"{value:.2f}"
            
            value_item = QTableWidgetItem(value_str)
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.ratios_table.setItem(row, 2, value_item)
            
            # Estado
            if min_val <= value <= max_val:
                status = "✅ Bueno"
                color = QColor("#10B981")
            elif value < min_val:
                status = "⚠️ Bajo"
                color = QColor("#EF4444")
            else:
                status = "⚠️ Alto"
                color = QColor("#F59E0B")
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(color)
            self.ratios_table.setItem(row, 3, status_item)

    def _load_targets_into_inputs(self):
        """Carga objetivos guardados en los inputs."""
        # Targets
        self.input_roa.setText(str(self.target_ratios.get('roa', 0.12) * 100))
        self.input_roe.setText(str(self.target_ratios.get('roe', 0.15) * 100))
        self.input_current_ratio.setText(str(self.target_ratios.get('current_ratio', 2.0)))
        self.input_debt_ratio.setText(str(self.target_ratios.get('debt_ratio', 0.40) * 100))
        self.input_net_margin.setText(str(self.target_ratios.get('net_margin', 0.10) * 100))
        
        # Constraints
        self.input_min_current.setText(str(self.constraints.get('min_current_ratio', 1.5)))
        self.input_max_debt.setText(str(self.constraints.get('max_debt_ratio', 0.60) * 100))
        self.input_min_cash.setText(str(self.constraints.get('min_cash_balance', 100000)))

    def _calculate_scenarios(self):
        """Calcula escenarios de optimización."""
        if not self.current_state:
            QMessageBox.warning(self, "Sin Datos", "No se pudo cargar el estado financiero actual.")
            return
        
        try:
            # Leer objetivos de los inputs
            targets = {
                'roa': float(self.input_roa.text() or 12) / 100,
                'roe': float(self.input_roe.text() or 15) / 100,
                'current_ratio': float(self.input_current_ratio.text() or 2.0),
                'debt_ratio': float(self.input_debt_ratio.text() or 40) / 100,
                'net_margin': float(self.input_net_margin.text() or 10) / 100,
            }
            
            # Leer restricciones
            constraints = {}
            
            if self.chk_min_current.isChecked():
                constraints['min_current_ratio'] = float(self.input_min_current.text() or 1.5)
            
            if self.chk_max_debt.isChecked():
                constraints['max_debt_ratio'] = float(self.input_max_debt.text() or 60) / 100
            
            if self.chk_min_cash.isChecked():
                constraints['min_cash_balance'] = float(self.input_min_cash.text() or 100000)
            
            # Ejecutar optimizador
            from financial_optimizer import FinancialOptimizer
            
            optimizer = FinancialOptimizer(self.current_state)
            self.scenarios = optimizer.optimize(targets, constraints)
            
            if not self.scenarios:
                QMessageBox.information(
                    self,
                    "Sin Escenarios",
                    "No se pudieron generar escenarios. Los objetivos ya se están cumpliendo."
                )
                return
            
            # Mostrar escenarios
            self._display_scenarios()
            
            QMessageBox.information(
                self,
                "Éxito",
                f"Se generaron {len(self.scenarios)} escenarios de optimización.\n"
                "Revisa la pestaña 'Escenarios de Optimización'."
            )

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Valores inválidos en los campos:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error calculando escenarios:\n{e}")
            traceback.print_exc()

    def _display_scenarios(self):
        """Muestra escenarios en la tabla."""
        self.scenarios_list.setRowCount(0)
        
        for idx, scenario in enumerate(self.scenarios):
            row = self.scenarios_list.rowCount()
            self.scenarios_list.insertRow(row)
            
            # Nombre
            name_item = QTableWidgetItem(scenario.name)
            name_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.scenarios_list.setItem(row, 0, name_item)
            
            # Factibilidad
            feasibility_item = QTableWidgetItem(f"{scenario.feasibility_score:.0f}%")
            if scenario.feasibility_score >= 70:
                feasibility_item.setForeground(QColor("#10B981"))
            elif scenario.feasibility_score >= 50:
                feasibility_item.setForeground(QColor("#F59E0B"))
            else:
                feasibility_item.setForeground(QColor("#EF4444"))
            self.scenarios_list.setItem(row, 1, feasibility_item)
            
            # Riesgo
            risk_item = QTableWidgetItem(scenario.risk_level)
            if scenario.risk_level == "LOW":
                risk_item.setForeground(QColor("#10B981"))
            elif scenario.risk_level == "MEDIUM":
                risk_item.setForeground(QColor("#F59E0B"))
            else:
                risk_item.setForeground(QColor("#EF4444"))
            self.scenarios_list.setItem(row, 2, risk_item)
            
            # Cumple restricciones
            meets_item = QTableWidgetItem("✅ Sí" if scenario.meets_constraints else "❌ No")
            meets_item.setForeground(QColor("#10B981") if scenario.meets_constraints else QColor("#EF4444"))
            self.scenarios_list.setItem(row, 3, meets_item)
            
            # Botón Ver Detalles
            btn_view = QPushButton("Ver Detalles")
            btn_view.setObjectName("viewButton")
            btn_view.clicked.connect(lambda checked, i=idx: self._show_scenario_details(i))
            
            self.scenarios_list.setCellWidget(row, 4, btn_view)

    def _show_scenario_details(self, scenario_idx: int):
        """Muestra detalles de un escenario."""
        if scenario_idx >= len(self.scenarios):
            return
        
        self.selected_scenario_idx = scenario_idx
        scenario = self.scenarios[scenario_idx]
        
        # Construir texto de detalles
        details = f"**{scenario.name}**\n\n"
        details += f"{scenario.description}\n\n"
        details += f"**Factibilidad:** {scenario.feasibility_score:.0f}%\n"
        details += f"**Nivel de Riesgo:** {scenario.risk_level}\n"
        details += f"**Cumple Restricciones:** {'Sí ✅' if scenario.meets_constraints else 'No ❌'}\n\n"
        
        if scenario.constraint_violations:
            details += "**⚠️ Violaciones:**\n"
            for violation in scenario.constraint_violations:
                details += f"  • {violation}\n"
            details += "\n"
        
        details += "**📊 Ajustes Propuestos:**\n"
        for adj in scenario.adjustments:
            sign = "+" if adj.amount > 0 else ""
            details += f"\n• {adj.description}\n"
            details += f"  Monto: {sign}RD$ {abs(adj.amount):,.2f}\n"
            details += f"  Prioridad: {adj.priority.value} | Factibilidad: {adj.feasibility.value}\n"
            details += f"  Plazo: {adj.timeframe_days} días\n"
        
        details += "\n**📈 Impacto en Ratios:**\n"
        for ratio_name, impact in scenario.total_impact.items():
            if abs(impact) > 0.001:
                sign = "+" if impact > 0 else ""
                if "ratio" in ratio_name or ratio_name in ["roa", "roe", "net_margin"]:
                    details += f"  • {ratio_name.upper()}: {sign}{impact * 100:.1f}%\n"
                else:
                    details += f"  • {ratio_name.upper()}: {sign}{impact:.2f}\n"
        
        self.scenario_details.setPlainText(details)
        
        # Actualizar plan de acción
        self._update_action_plan(scenario)

    def _update_action_plan(self, scenario):
        """Actualiza el plan de acción."""
        self.action_table.setRowCount(0)
        
        # Ordenar ajustes por prioridad
        from financial_optimizer import Priority
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        sorted_adjustments = sorted(scenario.adjustments, key=lambda a: priority_order[a.priority])
        
        for adj in sorted_adjustments:
            row = self.action_table.rowCount()
            self.action_table.insertRow(row)
            
            # Prioridad
            priority_item = QTableWidgetItem(adj.priority.value)
            if adj.priority == Priority.HIGH:
                priority_item.setForeground(QColor("#EF4444"))
                priority_item.setText("🔴 " + adj.priority.value)
            elif adj.priority == Priority.MEDIUM:
                priority_item.setForeground(QColor("#F59E0B"))
                priority_item.setText("🟡 " + adj.priority.value)
            else:
                priority_item.setForeground(QColor("#10B981"))
                priority_item.setText("🟢 " + adj.priority.value)
            self.action_table.setItem(row, 0, priority_item)
            
            # Acción
            self.action_table.setItem(row, 1, QTableWidgetItem(adj.description))
            
            # Monto
            sign = "+" if adj.amount > 0 else ""
            monto_item = QTableWidgetItem(f"{sign}RD$ {abs(adj.amount):,.0f}")
            monto_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.action_table.setItem(row, 2, monto_item)
            
            # Plazo
            self.action_table.setItem(row, 3, QTableWidgetItem(f"{adj.timeframe_days} días"))
            
            # Factibilidad
            feasibility_item = QTableWidgetItem(adj.feasibility.value)
            if adj.feasibility.value == "Alta":
                feasibility_item.setForeground(QColor("#10B981"))
            elif adj.feasibility.value == "Media":
                feasibility_item.setForeground(QColor("#F59E0B"))
            else:
                feasibility_item.setForeground(QColor("#EF4444"))
            self.action_table.setItem(row, 4, feasibility_item)
        
        # Actualizar resumen de impacto
        self._update_impact_summary(scenario)

    def _update_impact_summary(self, scenario):
        """Actualiza el resumen de impacto."""
        summary = f"**Escenario Seleccionado:** {scenario.name}\n\n"
        
        summary += "**Ratios Proyectados:**\n"
        projected_ratios = scenario.projected_state.calculate_ratios()
        
        key_ratios = [
            ('roa', 'ROA', True),
            ('roe', 'ROE', True),
            ('current_ratio', 'Razón Corriente', False),
            ('debt_ratio', 'Endeudamiento', True),
            ('net_margin', 'Margen Neto', True),
        ]
        
        for ratio_key, ratio_label, is_pct in key_ratios:
            current_val = self.current_ratios.get(ratio_key, 0)
            projected_val = projected_ratios.get(ratio_key, 0)
            change = projected_val - current_val
            
            if is_pct:
                current_str = f"{current_val * 100:.1f}%"
                projected_str = f"{projected_val * 100:.1f}%"
                change_str = f"{change * 100:+.1f}%"
            else:
                current_str = f"{current_val:.2f}"
                projected_str = f"{projected_val:.2f}"
                change_str = f"{change:+.2f}"
            
            summary += f"{ratio_label}: {current_str} → {projected_str} ({change_str})\n"
        
        self.impact_summary.setText(summary)

    def _save_configuration(self):
        """Guarda la configuración de objetivos."""
        try:
            # Leer objetivos
            targets = {
                'roa': float(self.input_roa.text() or 12) / 100,
                'roe': float(self.input_roe.text() or 15) / 100,
                'current_ratio': float(self.input_current_ratio.text() or 2.0),
                'debt_ratio': float(self.input_debt_ratio.text() or 40) / 100,
                'net_margin': float(self.input_net_margin.text() or 10) / 100,
            }
            
            # Leer restricciones
            constraints = {}
            
            if self.chk_min_current.isChecked():
                constraints['min_current_ratio'] = float(self.input_min_current.text() or 1.5)
            
            if self.chk_max_debt.isChecked():
                constraints['max_debt_ratio'] = float(self.input_max_debt.text() or 60) / 100
            
            if self.chk_min_cash.isChecked():
                constraints['min_cash_balance'] = float(self.input_min_cash.text() or 100000)
            
            # Guardar
            period = f"{self.year_int}-{self.month_str}" if self.month_str else f"{self.year_int}"
            
            if hasattr(self.controller, "save_financial_targets"):
                ok, msg = self.controller.save_financial_targets(
                    self.company_id,
                    period,
                    targets,
                    constraints
                )
                
                if ok:
                    QMessageBox.information(self, "Éxito", msg)
                else:
                    QMessageBox.warning(self, "Error", msg)
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Método save_financial_targets no implementado."
                )

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Valores inválidos:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{e}")
