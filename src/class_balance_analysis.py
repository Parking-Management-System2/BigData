"""
Analiza balansu klas (przed przetworzeniem)
Wizualizacja zbioru przed zbalansowaniem - wykres przedstawiający liczebność dwóch klas.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

def analyze_class_balance(data_path: str, output_path: str = None):
    """
    Analizuje balans klas w zbiorze danych i generuje wizualizację.
    
    Args:
        data_path: Ścieżka do pliku CSV z danymi
        output_path: Ścieżka do zapisu wykresu (opcjonalne)
    """
    # Wczytanie danych
    df = pd.read_csv(data_path)
    
    # Analiza rozkładu klas
    class_counts = df['Churn'].value_counts()
    class_percentages = df['Churn'].value_counts(normalize=True) * 100
    
    # Obliczenie stopnia niezbalansowania (imbalance ratio)
    majority_class = class_counts.max()
    minority_class = class_counts.min()
    imbalance_ratio = majority_class / minority_class
    
    print("=" * 60)
    print("ANALIZA BALANSU KLAS - PRZED PRZETWORZENIEM")
    print("=" * 60)
    print(f"\n📊 Rozkład klas:")
    print(f"   • Klasa 'No'  (Pozostają):  {class_counts['No']:,} ({class_percentages['No']:.2f}%)")
    print(f"   • Klasa 'Yes' (Odchodzą):   {class_counts['Yes']:,} ({class_percentages['Yes']:.2f}%)")
    print(f"\n⚖️  Stopień niezbalansowania (Imbalance Ratio): {imbalance_ratio:.2f}:1")
    print(f"   Klasa większościowa jest {imbalance_ratio:.2f}x liczniejsza od mniejszościowej")
    print("=" * 60)
    
    # Tworzenie wizualizacji
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Analiza Balansu Klas - Przed Zbalansowaniem\n(Telco Customer Churn Dataset)', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    # Kolory - ciemniejsze, bardziej profesjonalne
    colors = ['#2E86AB', '#E94F37']  # Niebieski dla No, Czerwony dla Yes
    
    # ========== Wykres 1: Wykres słupkowy ==========
    ax1 = axes[0]
    bars = ax1.bar(['No\n(Pozostają)', 'Yes\n(Odchodzą)'], 
                   [class_counts['No'], class_counts['Yes']], 
                   color=colors, 
                   edgecolor='black', 
                   linewidth=1.5,
                   width=0.6)
    
    # Dodanie etykiet na słupkach
    for bar, count, pct in zip(bars, [class_counts['No'], class_counts['Yes']], 
                                      [class_percentages['No'], class_percentages['Yes']]):
        height = bar.get_height()
        ax1.annotate(f'{count:,}\n({pct:.1f}%)',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5),
                     textcoords="offset points",
                     ha='center', va='bottom',
                     fontsize=12, fontweight='bold')
    
    ax1.set_ylabel('Liczba klientów', fontsize=12)
    ax1.set_title('Rozkład klas w zbiorze danych', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, class_counts['No'] * 1.15)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_axisbelow(True)
    
    # Dodanie linii pokazującej różnicę
    ax1.axhline(y=class_counts['Yes'], color='gray', linestyle='--', alpha=0.5)
    
    # ========== Wykres 2: Wykres kołowy ==========
    ax2 = axes[1]
    
    explode = (0, 0.05)  # Lekkie wyróżnienie klasy mniejszościowej
    wedges, texts, autotexts = ax2.pie([class_counts['No'], class_counts['Yes']], 
                                        explode=explode,
                                        colors=colors,
                                        autopct='%1.1f%%',
                                        startangle=90,
                                        pctdistance=0.6,
                                        wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})
    
    # Stylizacja tekstu
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(14)
        autotext.set_fontweight('bold')
    
    ax2.set_title('Proporcje klas', fontsize=12, fontweight='bold')
    
    # Legenda
    legend_labels = [f"No (Pozostają): {class_counts['No']:,}", 
                     f"Yes (Odchodzą): {class_counts['Yes']:,}"]
    ax2.legend(wedges, legend_labels, 
               title="Klasy", 
               loc="center left", 
               bbox_to_anchor=(0.9, 0, 0.5, 1),
               fontsize=10)
    
    # ========== Dodatkowe informacje ==========
    info_text = (f"Łącznie: {len(df):,} rekordów\n"
                 f"Współczynnik niezbalansowania: {imbalance_ratio:.2f}:1\n"
                 f"Różnica: {class_counts['No'] - class_counts['Yes']:,} rekordów")
    
    fig.text(0.5, -0.08, info_text, ha='center', va='top', fontsize=11,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgray', alpha=0.7))
    
    plt.tight_layout()
    
    # Zapisanie wykresu
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"\n✅ Wykres zapisany: {output_path}")
    
    plt.show()
    
    return {
        'total_records': len(df),
        'class_counts': class_counts.to_dict(),
        'class_percentages': class_percentages.to_dict(),
        'imbalance_ratio': imbalance_ratio
    }


if __name__ == "__main__":
    # Określenie ścieżek
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_path = os.path.join(project_dir, 'data', 'WA_Fn-UseC_-Telco-Customer-Churn.csv')
    output_path = os.path.join(project_dir, 'data', 'class_balance_before_preprocessing.png')
    
    # Uruchomienie analizy
    results = analyze_class_balance(data_path, output_path)
