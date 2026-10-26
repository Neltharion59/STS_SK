import csv

def escape_latex(text):
    """Escape special LaTeX characters"""
    # Don't escape backslash globally - it breaks LaTeX commands like \%
    # Data shouldn't contain raw backslashes anyway
    replacements = [
        ('%', r'\%'),
        ('&', r'\&'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
    ]
    for char, esc in replacements:
        text = text.replace(char, esc)
    return text

def main():
    with open("template_metrics_v2.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{Coverage comparison: Conceptual Dictionary vs. WordNet (Slovak)}")
    lines.append(r"\label{tab:coverage-comparison}")
    # Use p{width} for first column to handle long text, c for centered numeric columns
    lines.append(r"\begin{tabular}{p{5.5cm}cc}")
    lines.append(r"\toprule")
    lines.append(r"\textbf{Metric} & \textbf{Conceptual Dictionary} & \textbf{WordNet} \\")
    lines.append(r"\midrule")
    lines.append(r"\multicolumn{3}{c}{\textit{Resource Coverage}} \\")
    lines.append(r"\midrule")

    in_lexical = False
    for row in rows:
        metric = row["metric"]
        cd = row["conceptual_dictionary"]
        wn = row["wordnet"]

        if metric == "HEADER":
            continue
        elif metric == r"\hline":
            lines.append(r"\midrule")
            lines.append(r"\multicolumn{3}{c}{\textit{Lexical Relations}} \\")
            lines.append(r"\midrule")
            in_lexical = True
        else:
            metric = escape_latex(metric)
            cd = escape_latex(cd)
            wn = escape_latex(wn)
            lines.append(f"{metric} & {cd} & {wn} \\\\")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    with open("coverage_comparison_table.tex", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Saved coverage_comparison_table.tex")

if __name__ == "__main__":
    main()