from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QComboBox,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTextEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import calendar


class AnnualExpensesManager(QDialog):
    """
    Gestor de Gastos Adicionales ACUMULATIVOS por Año.  
    
    - Muestra conceptos anuales
    - Permite editar valor acumulado por mes
    - Navegación entre meses
    - Vista de histórico mensual
    - Integración con catálogo maestro
    """

    MONTHS_MAP = {
        "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
        "Mayo": "05", "Junio": "06", "Julio":  "07", "Agosto": "08",
        "Septiembre": "09", "Octubre":  "10", "Noviembre":  "11", "Diciembre": "12",
    }

    def __init__(
        self,
        parent,
        controller,
        company_id,
        company_name:  str,
        month_str: str,
        year_int: int,
    ):
        super().__init__(parent)
        self.controller = controller
        self.company_id = company_id
        self.company_name = company_name
        self.current_month_str = month_str
        self.current_year_int = year_int
        
        self.editing_concept_id = None
        self.editing_concept_name = None

        self.setWindowTitle(f"Gastos Adicionales Anuales - {company_name} - {year_int}")
        self.resize(1000, 680)
        self.setModal(True)

        self._build_ui()
        self._load_concepts()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # === HEADER CON NAVEGACIÓN ===
        header_card = QFrame()
        header_card.setObjectName("headerCard")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(20, 16, 20, 16)
        header_layout.setSpacing(8)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        title = QLabel(f"📊 Gastos Adicionales Acumulativos")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #0F172A;")
        title_row.addWidget(title)
        title_row.addStretch()

        # Navegación de mes
        nav_container = QHBoxLayout()
        nav_container.setSpacing(8)

        self.btn_prev_month = QPushButton("◀ Anterior")
        self.btn_prev_month.setObjectName("navButton")
        self.btn_prev_month.clicked.connect(self._prev_month)

        self.month_label = QLabel()
        self.month_label.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #1E293B; "
            "padding: 6px 20px; background-color: #EFF6FF; border-radius: 6px;"
        )
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_label.setMinimumWidth(180)

        self.btn_next_month = QPushButton("Siguiente ▶")
        self.btn_next_month.setObjectName("navButton")
        self.btn_next_month.clicked.connect(self._next_month)

        nav_container.addWidget(self.btn_prev_month)
        nav_container.addWidget(self.month_label)
        nav_container.addWidget(self.btn_next_month)

        title_row.addLayout(nav_container)

        header_layout.addLayout(title_row)

        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet("font-size: 12px; color: #64748B;")
        header_layout.addWidget(self.subtitle_label)

        root.addWidget(header_card)

        # === FORMULARIO PARA EDITAR/AGREGAR ===
        form_card = QFrame()
        form_card.setObjectName("formCard")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(20, 16, 20, 16)
        form_layout.setSpacing(12)

        form_title = QLabel("Editar Concepto Anual")
        form_title.setStyleSheet("font-weight: 700; color: #1E293B; font-size: 14px;")
        form_layout.addWidget(form_title)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        lbl_concepto = QLabel("Concepto:")
        lbl_concepto.setStyleSheet("color: #475569; font-weight: 600;")
        row1.addWidget(lbl_concepto)

        self.edit_concepto = QLineEdit()
        self.edit_concepto.setPlaceholderText("Ej: Depreciación Equipos, Nómina Administrativa...")
        self.edit_concepto.setObjectName("modernInput")
        row1.addWidget(self.edit_concepto, 2)

        lbl_categoria = QLabel("Categoría:")
        lbl_categoria.setStyleSheet("color: #475569; font-weight: 600;")
        row1.addWidget(lbl_categoria)

        self.combo_categoria = QComboBox()
        self.combo_categoria.setObjectName("modernCombo")
        self.combo_categoria.addItems([
            "Nómina", "Servicios", "Alquiler", "Mantenimiento",
            "Publicidad", "Transporte", "Depreciación", "Otros"
        ])
        self.combo_categoria.setEditable(True)
        self.combo_categoria.setMinimumWidth(160)
        row1.addWidget(self.combo_categoria)

        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        lbl_valor = QLabel(f"Valor Acumulado (hasta {self._get_month_name()}):")
        lbl_valor.setStyleSheet("color: #475569; font-weight: 600;")
        self.lbl_valor_mes = lbl_valor
        row2.addWidget(lbl_valor)

        self.edit_valor = QLineEdit()
        self.edit_valor.setPlaceholderText("0.00")
        self.edit_valor.setObjectName("modernInput")
        self.edit_valor.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.edit_valor.setMaximumWidth(200)
        row2.addWidget(self.edit_valor)

        row2.addWidget(QLabel("RD$"))
        row2.addStretch()

        form_layout.addLayout(row2)

        row3 = QVBoxLayout()
        row3.setSpacing(4)

        lbl_nota = QLabel("Nota del mes (opcional):")
        lbl_nota.setStyleSheet("color: #475569; font-weight:  600;")
        row3.addWidget(lbl_nota)

        self.edit_nota = QTextEdit()
        self.edit_nota.setObjectName("modernTextEdit")
        self.edit_nota.setPlaceholderText("Descripción del cambio este mes...")
        self.edit_nota.setMaximumHeight(60)
        row3.addWidget(self.edit_nota)

        form_layout.addLayout(row3)

        # === BOTONES DE ACCIÓN (Corregidos) ===
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_guardar = QPushButton("💾 Guardar Valor")
        self.btn_guardar.setObjectName("primaryButton")
        self.btn_guardar.clicked.connect(self._save_value)

        self.btn_nuevo = QPushButton("➕ Nuevo Concepto")
        self.btn_nuevo.setObjectName("secondaryButton")
        self.btn_nuevo.clicked.connect(self._new_concept)

        self.btn_catalog = QPushButton("📚 Catálogo")
        self.btn_catalog.setObjectName("catalogButton")
        self.btn_catalog.setToolTip("Gestionar catálogo maestro de conceptos")
        self.btn_catalog.clicked.connect(self._open_concept_catalog)

        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.setObjectName("cancelButton")
        self.btn_cancelar.clicked.connect(self._cancel_edit)
        self.btn_cancelar.setVisible(False)

        btn_row.addWidget(self.btn_guardar)
        btn_row.addWidget(self.btn_nuevo)
        btn_row.addWidget(self.btn_catalog)
        btn_row.addWidget(self.btn_cancelar)
        btn_row.addStretch()

        form_layout.addLayout(btn_row)
        root.addWidget(form_card)

        # === TABLA DE CONCEPTOS ===
        table_label = QLabel("📋 Conceptos del Año:")
        table_label.setStyleSheet("font-weight: 700; color: #1E293B; font-size:  14px;")
        root.addWidget(table_label)

        self.table = QTableWidget()
        self.table.setObjectName("modernTable")
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Concepto", "Categoría", f"Valor {self._get_month_name()}", "Acumulado Año", "Acciones"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 140)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(40)

        root.addWidget(self.table)

        # === TOTAL ===
        total_card = QFrame()
        total_card.setObjectName("totalCard")
        total_layout = QHBoxLayout(total_card)
        total_layout.setContentsMargins(20, 16, 20, 16)
        total_layout.setSpacing(12)

        total_lbl = QLabel(f"TOTAL ACUMULADO ({self._get_month_name().upper()}):")
        total_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #1E293B;")

        self.label_total = QLabel("RD$ 0.00")
        self.label_total.setStyleSheet(
            "font-size: 20px; font-weight: 800; color: #DC2626;"
        )

        total_layout.addStretch()
        total_layout.addWidget(total_lbl)
        total_layout.addWidget(self.label_total)

        root.addWidget(total_card)

        self._apply_styles()
        self._update_labels()

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #F8F9FA;
            }

            QFrame#headerCard, QFrame#formCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }

            QFrame#totalCard {
                background-color:  #FFFFFF;
                border-radius: 12px;
                border: 2px solid #DC2626;
                background:  qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FEF2F2,
                    stop:1 #FFFFFF
                );
            }

            /* INPUTS Y COMBOS */
            QLineEdit#modernInput, QTextEdit#modernTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 12px;
                color: #0F172A;
                font-size: 13px;
            }

            QLineEdit#modernInput:focus, QTextEdit#modernTextEdit:focus {
                border-color: #3B82F6;
                border-width: 2px;
            }

            QComboBox#modernCombo {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px 12px;
                color: #0F172A;
                font-size: 13px;
                font-weight: 500;
            }

            QComboBox#modernCombo:hover { border-color: #3B82F6; }
            QComboBox#modernCombo::drop-down { border: none; width: 30px; }

            QComboBox#modernCombo::down-arrow {
                image:  none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #64748B;
                margin-right: 8px;
            }

            QComboBox#modernCombo QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                selection-background-color: #EFF6FF;
                selection-color: #1E293B;
                color: #0F172A;
            }

            /* === BOTONES PRINCIPALES (HOMOLOGADOS) === */
            /* Definimos la estructura base para que todos sean iguales */
            QPushButton#primaryButton, QPushButton#secondaryButton, QPushButton#catalogButton {
                padding: 0px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                border: none;
                min-width: 150px; /* Ancho mínimo */
                height: 40px;     /* Alto fijo */
                color: #FFFFFF;
            }

            QPushButton#primaryButton { background-color: #15803D; }
            QPushButton#primaryButton:hover { background-color: #166534; }

            QPushButton#secondaryButton { background-color: #3B82F6; }
            QPushButton#secondaryButton:hover { background-color: #2563EB; }

            QPushButton#catalogButton { background-color: #8B5CF6; }
            QPushButton#catalogButton:hover { background-color: #7C3AED; }

            /* Botón Cancelar */
            QPushButton#cancelButton {
                background-color: #DC2626;
                color: #FFFFFF;
                padding: 0px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                border: none;
                min-width: 100px;
                height: 40px;
            }
            QPushButton#cancelButton:hover { background-color: #B91C1C; }

            /* Botones de Navegación */
            QPushButton#navButton {
                background-color:  #F9FAFB;
                color: #374151;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 600;
                font-size: 13px;
                height: 32px;
            }

            QPushButton#navButton:hover { background-color: #E5E7EB; }

            /* Botones de Tabla */
            QPushButton#actionButton, QPushButton#deleteButton, QPushButton#historyButton {
                color: #FFFFFF;
                border-radius:  6px;
                border: none;
                font-weight: 600;
                font-size: 18px;
                width: 36px;
                height: 32px;
            }

            QPushButton#actionButton { background-color:  #3B82F6; }
            QPushButton#actionButton:hover { background-color:  #2563EB; }

            QPushButton#deleteButton { background-color:  #EF4444; }
            QPushButton#deleteButton:hover { background-color:  #DC2626; }

            QPushButton#historyButton { background-color: #8B5CF6; }
            QPushButton#historyButton:hover { background-color:  #7C3AED; }

            /* TABLA */
            QTableWidget#modernTable {
                background-color: #FFFFFF;
                alternate-background-color: #F9FAFB;
                border:  1px solid #E5E7EB;
                border-radius: 8px;
                gridline-color: #E5E7EB;
                color: #0F172A;
            }

            QTableWidget#modernTable::item { padding: 8px; }

            QHeaderView::section {
                background-color: #F1F5F9;
                border: none;
                padding: 10px 8px;
                color: #475569;
                font-weight:  700;
                font-size: 12px;
                text-transform: uppercase;
            }
        """)

    def _get_month_name(self):
        """Devuelve el nombre del mes actual."""
        for name, code in self.MONTHS_MAP.items():
            if code == self.current_month_str:
                return name
        return "Mes"

    def _update_labels(self):
        """Actualiza labels dinámicos según el mes actual."""
        month_name = self._get_month_name()
        
        self.month_label.setText(f"{month_name} {self.current_year_int}")
        self.subtitle_label.setText(
            f"{self.company_name} – Viendo valores acumulados hasta {month_name}"
        )
        self.lbl_valor_mes.setText(f"Valor Acumulado (hasta {month_name}):")
        
        # Actualizar header de tabla
        if self.table.columnCount() >= 3:
            self.table.setHorizontalHeaderLabels([
                "Concepto", 
                "Categoría", 
                f"Valor {month_name}", 
                "Acumulado Año", 
                "Acciones"
            ])

    def _prev_month(self):
        """Navega al mes anterior."""
        month_int = int(self.current_month_str)
        
        if month_int == 1:
            # Ir a diciembre del año anterior
            self.current_year_int -= 1
            self.current_month_str = "12"
        else:
            self.current_month_str = f"{month_int - 1:02d}"
        
        self._update_labels()
        self._load_concepts()

    def _next_month(self):
        """Navega al mes siguiente."""
        month_int = int(self.current_month_str)
        
        if month_int == 12:
            # Ir a enero del año siguiente
            self.current_year_int += 1
            self.current_month_str = "01"
        else:
            self.current_month_str = f"{month_int + 1:02d}"
        
        self._update_labels()
        self._load_concepts()

    def _load_concepts(self):
        """Carga los conceptos anuales."""
        concepts = []
        try:
            if hasattr(self.controller, "get_annual_expense_concepts"):
                concepts = self.controller.get_annual_expense_concepts(
                    self.company_id,
                    self.current_year_int
                ) or []
        except Exception as e:
            print(f"[ANNUAL_MANAGER] Error:  {e}")
            QMessageBox.warning(self, "Error", f"Error cargando conceptos:\n{e}")

        self.table.setRowCount(0)
        total_month = 0.0

        for concept_data in concepts:
            row = self.table.rowCount()
            self.table.insertRow(row)

            concept_name = concept_data.get("concept", "")
            category = concept_data.get("category", "")
            monthly_values = concept_data.get("monthly_values", {})

            # Valor del mes actual
            value_month = float(monthly_values.get(self.current_month_str, 0.0) or 0.0)
            
            # Si no existe, buscar último valor anterior
            if value_month == 0.0:
                month_int = int(self.current_month_str)
                for m in range(month_int - 1, 0, -1):
                    m_str = f"{m:02d}"
                    if m_str in monthly_values:
                        value_month = float(monthly_values[m_str] or 0.0)
                        break

            # Acumulado año = valor de diciembre o último mes disponible
            value_year = value_month  # Por defecto
            for m in range(12, int(self.current_month_str), -1):
                m_str = f"{m:02d}"
                if m_str in monthly_values:
                    value_year = float(monthly_values[m_str] or 0.0)
                    break

            total_month += value_month

            # Nombre
            self.table.setItem(row, 0, QTableWidgetItem(concept_name))

            # Categoría
            self.table.setItem(row, 1, QTableWidgetItem(category))

            # Valor mes
            item_month = QTableWidgetItem(f"RD$ {value_month: ,.2f}")
            item_month.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, item_month)

            # Acumulado año
            item_year = QTableWidgetItem(f"RD$ {value_year:,.2f}")
            item_year.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_year.setForeground(QColor("#15803D"))
            item_year.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.table.setItem(row, 3, item_year)

            # Acciones
            actions_widget = QFrame()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(8, 4, 8, 4)
            actions_layout.setSpacing(6)

            btn_edit = QPushButton("✏️")
            btn_edit.setObjectName("actionButton")
            btn_edit.setToolTip("Editar valor del mes")
            btn_edit.clicked.connect(
                lambda checked, c=concept_data: self._edit_concept(c)
            )

            btn_history = QPushButton("📊")
            btn_history.setObjectName("historyButton")
            btn_history.setToolTip("Ver histórico mensual")
            btn_history.clicked.connect(
                lambda checked, c=concept_data: self._show_history(c)
            )

            btn_delete = QPushButton("🗑️")
            btn_delete.setObjectName("deleteButton")
            btn_delete.setToolTip("Eliminar concepto completo")
            btn_delete.clicked.connect(
                lambda checked, c=concept_data: self._delete_concept(c)
            )

            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_history)
            actions_layout.addWidget(btn_delete)
            actions_layout.addStretch()

            self.table.setCellWidget(row, 4, actions_widget)

        self.label_total.setText(f"RD$ {total_month:,.2f}")

    def _new_concept(self):
        """Limpia el formulario para crear un nuevo concepto."""
        self.editing_concept_id = None
        self.editing_concept_name = None
        self.edit_concepto.clear()
        self.edit_concepto.setEnabled(True)
        self.edit_valor.clear()
        self.edit_nota.clear()
        self.combo_categoria.setCurrentIndex(0)
        self.btn_guardar.setText("💾 Crear Concepto")
        self.btn_cancelar.setVisible(False)
        self.edit_concepto.setFocus()

    def _edit_concept(self, concept_data):
        """Carga un concepto para editar su valor del mes actual."""
        self.editing_concept_id = concept_data.get("id")
        self.editing_concept_name = concept_data.get("concept")
        
        self.edit_concepto.setText(self.editing_concept_name)
        self.edit_concepto.setEnabled(False)  # No se puede cambiar el nombre
        
        self.combo_categoria.setCurrentText(concept_data.get("category", ""))
        
        monthly_values = concept_data.get("monthly_values", {})
        value_month = float(monthly_values.get(self.current_month_str, 0.0) or 0.0)
        
        # Si no hay valor, buscar el anterior
        if value_month == 0.0:
            month_int = int(self.current_month_str)
            for m in range(month_int - 1, 0, -1):
                m_str = f"{m:02d}"
                if m_str in monthly_values:  
                    value_month = float(monthly_values[m_str] or 0.0)
                    break
        
        self.edit_valor.setText(f"{value_month:.2f}")
        
        monthly_notes = concept_data.get("monthly_notes", {})
        note = monthly_notes.get(self.current_month_str, "")
        self.edit_nota.setPlainText(note)
        
        self.btn_guardar.setText("💾 Actualizar Valor")
        self.btn_cancelar.setVisible(True)
        self.edit_valor.setFocus()
        self.edit_valor.selectAll()

    def _cancel_edit(self):
        """Cancela la edición."""
        self._new_concept()

    def _save_value(self):
        """Guarda el valor acumulado del concepto para el mes actual."""
        print("[SAVE_VALUE] ===== INICIO =====")
        
        concept_name = self.edit_concepto.text().strip()
        valor_str = self. edit_valor.text().strip().replace(",", "")
        
        print(f"[SAVE_VALUE] Concepto: {concept_name}")
        print(f"[SAVE_VALUE] Valor string: '{valor_str}'")
        
        if not concept_name: 
            print("[SAVE_VALUE] ❌ Concepto vacío")
            QMessageBox.warning(self, "Validación", "El concepto es obligatorio.")
            self.edit_concepto.setFocus()
            return

        try:
            valor = float(valor_str or 0)
            print(f"[SAVE_VALUE] Valor parseado:  {valor}")
            
            if valor < 0:
                reply = QMessageBox.question(
                    self,
                    "Valor Negativo",
                    "El valor acumulado es negativo.  ¿Estás seguro?",
                    QMessageBox. StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    print("[SAVE_VALUE] Usuario canceló valor negativo")
                    return
        except ValueError as e:
            print(f"[SAVE_VALUE] ❌ Error parseando valor:  {e}")
            QMessageBox.warning(self, "Validación", "El valor debe ser un número válido.")
            self.edit_valor.setFocus()
            return

        category = self.combo_categoria.currentText().strip()
        note = self. edit_nota.toPlainText().strip()
        
        print(f"[SAVE_VALUE] Categoría: {category}")
        print(f"[SAVE_VALUE] Nota: {note}")
        print(f"[SAVE_VALUE] Company ID: {self.company_id}")
        print(f"[SAVE_VALUE] Año: {self.current_year_int}")
        print(f"[SAVE_VALUE] Mes: {self.current_month_str}")

        try:
            print("[SAVE_VALUE] Verificando método update_annual_expense_value...")
            
            if hasattr(self.controller, "update_annual_expense_value"):
                print("[SAVE_VALUE] ✅ Método existe, llamando...")
                
                ok, msg = self.controller.update_annual_expense_value(
                    self.company_id,
                    self.current_year_int,
                    self.current_month_str,
                    concept_name,
                    category,
                    valor,
                    note
                )
                
                print(f"[SAVE_VALUE] Resultado: ok={ok}, msg={msg}")

                if ok:
                    QMessageBox.information(self, "Éxito", msg)
                    self._new_concept()
                    self._load_concepts()
                else:
                    QMessageBox.warning(self, "Error", msg)
            else:
                print("[SAVE_VALUE] ❌ Método NO existe en controller")
                print(f"[SAVE_VALUE] Controller type: {type(self.controller)}")
                print(f"[SAVE_VALUE] Métodos con 'annual': {[m for m in dir(self.controller) if 'annual' in m. lower()]}")
                
                QMessageBox.critical(
                    self,
                    "Error",
                    "Método update_annual_expense_value no implementado en el controller."
                )

        except Exception as e:
            print(f"[SAVE_VALUE] ❌ EXCEPCIÓN: {e}")
            import traceback
            traceback. print_exc()
            QMessageBox.critical(self, "Error", f"Error al guardar:\n{e}")
        
        print("[SAVE_VALUE] ===== FIN =====")

    def _delete_concept(self, concept_data):
        """Elimina un concepto anual completo."""
        concept_id = concept_data.get("id")
        concept_name = concept_data.get("concept")

        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Estás seguro de eliminar el concepto '{concept_name}'?\n\n"
            f"Se eliminarán TODOS los valores mensuales del año {self.current_year_int}.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if hasattr(self.controller, "delete_annual_expense_concept"):
                    ok, msg = self.controller.delete_annual_expense_concept(concept_id)

                    if ok:
                        QMessageBox.information(self, "Éxito", msg)
                        self._load_concepts()
                    else:
                        QMessageBox.warning(self, "Error", msg)
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Método delete_annual_expense_concept no implementado."
                    )

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar:\n{e}")

    def _show_history(self, concept_data):
        """Muestra el histórico mensual de un concepto."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel
        
        concept_name = concept_data.get("concept")
        monthly_values = concept_data.get("monthly_values", {})
        monthly_notes = concept_data.get("monthly_notes", {})

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Histórico:  {concept_name}")
        dlg.resize(600, 500)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel(f"📊 Histórico Mensual - {concept_name}")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #0F172A;")
        layout.addWidget(title)

        subtitle = QLabel(f"Año {self.current_year_int}")
        subtitle.setStyleSheet("font-size: 12px; color: #64748B;")
        layout.addWidget(subtitle)

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Mes", "Valor Acumulado", "Nota"])
        table.setRowCount(12)

        for month in range(1, 13):
            month_str = f"{month:02d}"
            month_name = list(self.MONTHS_MAP.keys())[month - 1]

            value = float(monthly_values.get(month_str, 0.0) or 0.0)
            note = monthly_notes.get(month_str, "")

            # Si no hay valor, buscar el anterior
            if value == 0.0 and month > 1:
                for m in range(month - 1, 0, -1):
                    m_str = f"{m:02d}"
                    if m_str in monthly_values:
                        value = float(monthly_values[m_str] or 0.0)
                        break

            table.setItem(month - 1, 0, QTableWidgetItem(month_name))
            
            value_item = QTableWidgetItem(f"RD$ {value:,.2f}")
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if month_str == self.current_month_str:
                value_item.setForeground(QColor("#3B82F6"))
                value_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            table.setItem(month - 1, 1, value_item)
            
            table.setItem(month - 1, 2, QTableWidgetItem(note))

        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        layout.addWidget(table)

        dlg.exec()

    def _open_concept_catalog(self):
        """Abre diálogo para gestionar el catálogo de conceptos."""
        try:
            from concept_catalog_dialog import ConceptCatalogDialog
            
            dlg = ConceptCatalogDialog(
                parent=self,
                controller=self.controller,
                company_id=self.company_id,
                year=self.current_year_int
            )
            
            if dlg.exec():
                # Recargar conceptos después de agregar desde catálogo
                self._load_concepts()
        
        except ImportError as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el diálogo del catálogo:\n{e}\n\nAsegúrate de que concept_catalog_dialog.py existe."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error al abrir el catálogo:\n{e}"
            )
            import traceback
            traceback.print_exc()