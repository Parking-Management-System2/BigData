"""
Augmentacja danych (Proces naprawczy)
Zastosowanie techniki SMOTE do zbalansowania klas w zbiorze Telco Customer Churn.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE


def load_and_preprocess_data(data_path: str):
    """
    Wczytuje dane i przygotowuje je do augmentacji SMOTE.
    
    Args:
        data_path: Ścieżka do pliku CSV
        
    Returns:
        df: DataFrame z danymi
        X: Cechy (zakodowane numerycznie)
        y: Zmienna docelowa
        encoders: Słownik z encoderami dla zmiennych kategorycznych
        feature_columns: Lista nazw kolumn cech
    """
    df = pd.read_csv(data_path)
    
    # Usunięcie kolumny customerID (nie jest cechą predykcyjną)
    if 'customerID' in df.columns:
        df = df.drop('customerID', axis=1)
    
    # Obsługa brakujących wartości w TotalCharges
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df['TotalCharges'] = df['TotalCharges'].fillna(0)
    
    # Separacja zmiennej docelowej
    y = df['Churn'].copy()
    X = df.drop('Churn', axis=1)
    
    # Zakodowanie zmiennych kategorycznych
    encoders = {}
    feature_columns = X.columns.tolist()
    
    for col in X.columns:
        if X[col].dtype == 'object':
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            encoders[col] = le
    
    # Zakodowanie zmiennej docelowej
    y_encoder = LabelEncoder()
    y_encoded = y_encoder.fit_transform(y)
    encoders['Churn'] = y_encoder
    
    return df, X, y_encoded, encoders, feature_columns


def apply_smote_augmentation(X, y, random_state=42):
    """
    Stosuje SMOTE do zbalansowania klas.
    
    Args:
        X: Cechy (DataFrame lub array)
        y: Zmienna docelowa (zakodowana)
        random_state: Seed dla powtarzalności
        
    Returns:
        X_resampled: Zaugmentowane cechy
        y_resampled: Zaugmentowana zmienna docelowa
        stats: Statystyki augmentacji
    """
    # Statystyki przed augmentacją
    unique, counts = np.unique(y, return_counts=True)
    before_stats = dict(zip(unique, counts))
    
    print("=" * 60)
    print("AUGMENTACJA DANYCH - SMOTE")
    print("=" * 60)
    print(f"\n📊 Przed augmentacją:")
    print(f"   • Klasa 0 (No):  {before_stats.get(0, 0):,}")
    print(f"   • Klasa 1 (Yes): {before_stats.get(1, 0):,}")
    print(f"   • Ratio: {before_stats.get(0, 0) / before_stats.get(1, 1):.2f}:1")
    
    # Zastosowanie SMOTE
    smote = SMOTE(random_state=random_state, sampling_strategy='auto')
    X_resampled, y_resampled = smote.fit_resample(X, y)
    
    # Statystyki po augmentacji
    unique, counts = np.unique(y_resampled, return_counts=True)
    after_stats = dict(zip(unique, counts))
    
    print(f"\n✅ Po augmentacji SMOTE:")
    print(f"   • Klasa 0 (No):  {after_stats.get(0, 0):,}")
    print(f"   • Klasa 1 (Yes): {after_stats.get(1, 0):,}")
    print(f"   • Ratio: {after_stats.get(0, 0) / after_stats.get(1, 1):.2f}:1")
    
    new_samples = after_stats.get(1, 0) - before_stats.get(1, 0)
    print(f"\n🔧 Wygenerowano {new_samples:,} syntetycznych próbek klasy mniejszościowej")
    print("=" * 60)
    
    stats = {
        'before': before_stats,
        'after': after_stats,
        'new_samples': new_samples
    }
    
    return X_resampled, y_resampled, stats


def decode_and_save_augmented_data(X_resampled, y_resampled, encoders, 
                                    feature_columns, output_path):
    """
    Dekoduje zaugmentowane dane i zapisuje do pliku CSV.
    
    Args:
        X_resampled: Zaugmentowane cechy
        y_resampled: Zaugmentowana zmienna docelowa
        encoders: Słownik z encoderami
        feature_columns: Lista nazw kolumn
        output_path: Ścieżka do zapisu
    """
    # Tworzenie DataFrame z zaugmentowanymi danymi
    df_augmented = pd.DataFrame(X_resampled, columns=feature_columns)
    
    # Dekodowanie zmiennych kategorycznych
    for col, encoder in encoders.items():
        if col != 'Churn' and col in df_augmented.columns:
            # Zaokrąglenie wartości do najbliższej liczby całkowitej
            df_augmented[col] = df_augmented[col].round().astype(int)
            # Ograniczenie do prawidłowego zakresu klas
            max_class = len(encoder.classes_) - 1
            df_augmented[col] = df_augmented[col].clip(0, max_class)
            df_augmented[col] = encoder.inverse_transform(df_augmented[col])
    
    # Dekodowanie zmiennej docelowej
    df_augmented['Churn'] = encoders['Churn'].inverse_transform(y_resampled)
    
    # Zapis do pliku
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_augmented.to_csv(output_path, index=False)
    print(f"\n✅ Zaugmentowane dane zapisane: {output_path}")
    
    return df_augmented


def visualize_augmentation_comparison(before_stats, after_stats, output_path):
    """
    Generuje wykres porównawczy przed/po augmentacji.
    
    Args:
        before_stats: Statystyki przed augmentacją
        after_stats: Statystyki po augmentacji
        output_path: Ścieżka do zapisu wykresu
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Porównanie Rozkładu Klas: Przed i Po Augmentacji SMOTE', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    colors = ['#2E86AB', '#E94F37']
    labels = ['No (Pozostają)', 'Yes (Odchodzą)']
    
    # ========== Wykres 1: PRZED augmentacją ==========
    ax1 = axes[0]
    before_values = [before_stats.get(0, 0), before_stats.get(1, 0)]
    bars1 = ax1.bar(labels, before_values, color=colors, edgecolor='black', linewidth=1.5)
    
    for bar, val in zip(bars1, before_values):
        height = bar.get_height()
        pct = val / sum(before_values) * 100
        ax1.annotate(f'{val:,}\n({pct:.1f}%)',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5), textcoords="offset points",
                     ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.set_ylabel('Liczba rekordów', fontsize=12)
    ax1.set_title('PRZED Augmentacją', fontsize=12, fontweight='bold', color='#D32F2F')
    ax1.set_ylim(0, max(after_stats.values()) * 1.2)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_axisbelow(True)
    
    # ========== Wykres 2: PO augmentacji ==========
    ax2 = axes[1]
    after_values = [after_stats.get(0, 0), after_stats.get(1, 0)]
    bars2 = ax2.bar(labels, after_values, color=colors, edgecolor='black', linewidth=1.5)
    
    for bar, val in zip(bars2, after_values):
        height = bar.get_height()
        pct = val / sum(after_values) * 100
        ax2.annotate(f'{val:,}\n({pct:.1f}%)',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 5), textcoords="offset points",
                     ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax2.set_ylabel('Liczba rekordów', fontsize=12)
    ax2.set_title('PO Augmentacji SMOTE', fontsize=12, fontweight='bold', color='#388E3C')
    ax2.set_ylim(0, max(after_stats.values()) * 1.2)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    ax2.set_axisbelow(True)
    
    # ========== Dodatkowe informacje ==========
    before_total = sum(before_values)
    after_total = sum(after_values)
    new_samples = after_values[1] - before_values[1]
    
    info_text = (f"Przed: {before_total:,} rekordów (ratio {before_values[0]/before_values[1]:.2f}:1)  →  "
                 f"Po: {after_total:,} rekordów (ratio {after_values[0]/after_values[1]:.2f}:1)\n"
                 f"Wygenerowano {new_samples:,} syntetycznych próbek metodą SMOTE")
    
    fig.text(0.5, -0.06, info_text, ha='center', va='top', fontsize=11,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#E8F5E9', alpha=0.9, edgecolor='#4CAF50'))
    
    plt.tight_layout()
    
    # Zapisanie wykresu
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"✅ Wykres porównawczy zapisany: {output_path}")
    
    plt.show()


def run_augmentation_pipeline(input_path: str, output_csv_path: str, 
                               output_plot_path: str, random_state=42):
    """
    Uruchamia pełny pipeline augmentacji danych.
    
    Args:
        input_path: Ścieżka do oryginalnego pliku CSV
        output_csv_path: Ścieżka do zapisu zaugmentowanych danych
        output_plot_path: Ścieżka do zapisu wykresu porównawczego
        random_state: Seed dla powtarzalności
        
    Returns:
        df_augmented: DataFrame z zaugmentowanymi danymi
    """
    # 1. Wczytanie i preprocessing
    print("\n📂 Wczytywanie danych...")
    df_original, X, y, encoders, feature_columns = load_and_preprocess_data(input_path)
    
    # 2. Zastosowanie SMOTE
    X_resampled, y_resampled, stats = apply_smote_augmentation(X, y, random_state)
    
    # 3. Zapis zaugmentowanych danych
    df_augmented = decode_and_save_augmented_data(
        X_resampled, y_resampled, encoders, feature_columns, output_csv_path
    )
    
    # 4. Wizualizacja
    visualize_augmentation_comparison(stats['before'], stats['after'], output_plot_path)
    
    return df_augmented


if __name__ == "__main__":
    # Określenie ścieżek
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    input_path = os.path.join(project_dir, 'data', 'WA_Fn-UseC_-Telco-Customer-Churn.csv')
    output_csv_path = os.path.join(project_dir, 'data', 'augmented_telco_churn.csv')
    output_plot_path = os.path.join(project_dir, 'data', 'augmentation_comparison.png')
    
    # Uruchomienie pipeline'u
    run_augmentation_pipeline(input_path, output_csv_path, output_plot_path)
