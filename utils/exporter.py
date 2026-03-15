import pandas as pd
import io

def export_to_excel(enriched_df, summary):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Holdings
        holdings = enriched_df.copy()
        holdings.to_excel(writer, sheet_name='Holdings', index=False)

        # Sheet 2: Summary
        summary_df = pd.DataFrame([{
            'Total Invested'  : f"",
            'Portfolio Value' : f"",
            'Total P&L'       : f"",
            'Total Return'    : f"{summary.get('total_return_pct', 0):+.2f}%",
            'Best Stock'      : summary.get('best_stock', '-'),
            'Worst Stock'     : summary.get('worst_stock', '-'),
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)

    output.seek(0)
    return output.getvalue()
