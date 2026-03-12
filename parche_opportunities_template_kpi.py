from pathlib import Path

path = Path("/home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/templates/opportunities/list.html")
text = path.read_text()

kpi_styles = """
    .kpi-row {
      display: grid;
      grid-template-columns: repeat(8, minmax(140px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }
    .kpi-card {
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      padding: 14px;
    }
    .kpi-label {
      color: #6b7280;
      font-size: 12px;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: .02em;
    }
    .kpi-value {
      font-size: 22px;
      font-weight: 700;
      color: #111827;
    }

    @media (max-width: 1280px) {
      .kpi-row {
        grid-template-columns: repeat(4, minmax(140px, 1fr));
      }
    }

    @media (max-width: 720px) {
      .kpi-row {
        grid-template-columns: repeat(2, minmax(140px, 1fr));
      }
    }
"""

kpi_block = """
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-label">Total</div>
        <div class="kpi-value">{{ metrics.total_opportunities }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Estimated value</div>
        <div class="kpi-value">
          {% if metrics.estimated_value_count %}
            {{ metrics.total_estimated_value }}
          {% else %}
            —
          {% endif %}
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg confidence</div>
        <div class="kpi-value">
          {% if metrics.average_confidence != None %}
            {{ metrics.average_confidence }}
          {% else %}
            —
          {% endif %}
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">New</div>
        <div class="kpi-value">{{ metrics.new_count }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Qualified</div>
        <div class="kpi-value">{{ metrics.qualified_count }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Proposal</div>
        <div class="kpi-value">{{ metrics.proposal_count }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Won</div>
        <div class="kpi-value">{{ metrics.won_count }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Lost</div>
        <div class="kpi-value">{{ metrics.lost_count }}</div>
      </div>
    </div>
"""

if ".kpi-row" in text:
    raise SystemExit("El template ya parece tener estilos KPI. No he cambiado nada.")

style_close = text.find("</style>")
if style_close == -1:
    raise SystemExit("No encontré </style>. No he cambiado nada.")

text = text[:style_close] + kpi_styles + "\n" + text[style_close:]

stats_marker = '<div class="stats">'
stats_start = text.find(stats_marker)
if stats_start == -1:
    raise SystemExit('No encontré <div class="stats">. No he cambiado nada.')

stats_end = text.find("</div>", stats_start)
if stats_end == -1:
    raise SystemExit('No encontré el cierre del bloque stats. No he cambiado nada.')

stats_end += len("</div>")
text = text[:stats_end] + "\n" + kpi_block + text[stats_end:]

path.write_text(text)
print("OK: KPIs añadidos a templates/opportunities/list.html")
