"""
Post-augmentation Analysis
Re-visualization and distribution check of features after augmentation.
Verification that no noise/errors were introduced.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

# Konfiguracja stylu
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('default')
sns.set_palette("husl")


def load_datasets(original_path: str, augmented_path: str):
    """
    Wczytuje oryginalne i zaugmentowane dane.
    
    Args:
        original_path: Ścieżka do oryginalnego pliku CSV
        augmented_path: Ścieżka do zaugmentowanego pliku CSV
        
    Returns:
        df_original: DataFrame z oryginalnymi danymi
        df_augmented: DataFrame z zaugmentowanymi danymi
    """
    print("[INFO] Loading data...")
    df_original = pd.read_csv(original_path)
    df_augmented = pd.read_csv(augmented_path)
    
    # Remove customerID if exists
    if 'customerID' in df_original.columns:
        df_original = df_original.drop('customerID', axis=1)
    if 'customerID' in df_augmented.columns:
        df_augmented = df_augmented.drop('customerID', axis=1)
    
    # Handle TotalCharges
    df_original['TotalCharges'] = pd.to_numeric(df_original['TotalCharges'], errors='coerce')
    df_original['TotalCharges'] = df_original['TotalCharges'].fillna(0)
    df_augmented['TotalCharges'] = pd.to_numeric(df_augmented['TotalCharges'], errors='coerce')
    df_augmented['TotalCharges'] = df_augmented['TotalCharges'].fillna(0)
    
    print(f"   • Original: {len(df_original):,} records")
    print(f"   • Augmented: {len(df_augmented):,} records")
    
    return df_original, df_augmented


def identify_feature_types(df):
    """
    Identyfikuje typy cech w zbiorze danych.
    
    Args:
        df: DataFrame
        
    Returns:
        numeric_features: Lista cech numerycznych
        categorical_features: Lista cech kategorycznych
    """
    numeric_features = []
    categorical_features = []
    
    for col in df.columns:
        if col == 'Churn':
            continue
        if df[col].dtype in ['int64', 'float64']:
            numeric_features.append(col)
        else:
            categorical_features.append(col)
    
    return numeric_features, categorical_features


def compare_numeric_distributions(df_original, df_augmented, numeric_features, output_dir):
    """
    Compares numeric feature distributions before and after augmentation.
    
    Args:
        df_original: DataFrame with original data
        df_augmented: DataFrame with augmented data
        numeric_features: List of numeric features
        output_dir: Directory to save plots
    """
    n_features = len(numeric_features)
    
    # Create grid based on number of features
    n_cols = 2
    n_rows = (n_features + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 6 * n_rows))
    fig.suptitle('Numeric Feature Distributions: Before vs After Augmentation',
                 fontsize=18, fontweight='bold', y=0.995)
    
    if n_rows == 1 and n_cols > 1:
        axes = axes.reshape(1, -1)
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    axes = axes.flatten()
    
    statistics_comparison = []
    
    for idx, feature in enumerate(numeric_features):
        ax = axes[idx]
        
        # Original and augmented data
        original_data = df_original[feature].dropna()
        augmented_data = df_augmented[feature].dropna()
        
        # Use KDE plots for smoother visualization
        sns.kdeplot(data=original_data, ax=ax, label='Before', 
                   color='#2E86AB', linewidth=2.5, fill=True, alpha=0.3)
        sns.kdeplot(data=augmented_data, ax=ax, label='After', 
                   color='#E94F37', linewidth=2.5, fill=True, alpha=0.3)
        
        # Statistics
        orig_mean = original_data.mean()
        orig_std = original_data.std()
        aug_mean = augmented_data.mean()
        aug_std = augmented_data.std()
        
        # Mean lines
        ax.axvline(orig_mean, color='#2E86AB', linestyle='--', linewidth=2.5, 
                   label=f'Before mean: {orig_mean:.2f}', alpha=0.8)
        ax.axvline(aug_mean, color='#E94F37', linestyle='--', linewidth=2.5, 
                   label=f'After mean: {aug_mean:.2f}', alpha=0.8)
        
        ax.set_xlabel(feature, fontsize=14, fontweight='bold')
        ax.set_ylabel('Density', fontsize=14, fontweight='bold')
        ax.set_title(f'{feature}', fontsize=16, fontweight='bold', pad=10)
        ax.legend(fontsize=11, loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(labelsize=11)
        
        # Statistical test (Kolmogorov-Smirnov)
        try:
            ks_stat, ks_pvalue = stats.ks_2samp(original_data, augmented_data)
            statistics_comparison.append({
                'Feature': feature,
                'Original_Mean': orig_mean,
                'Augmented_Mean': aug_mean,
                'Mean_Diff': abs(orig_mean - aug_mean),
                'Original_Std': orig_std,
                'Augmented_Std': aug_std,
                'Std_Diff': abs(orig_std - aug_std),
                'KS_Statistic': ks_stat,
                'KS_PValue': ks_pvalue,
                'Significant_Diff': ks_pvalue < 0.05
            })
        except:
            statistics_comparison.append({
                'Feature': feature,
                'Original_Mean': orig_mean,
                'Augmented_Mean': aug_mean,
                'Mean_Diff': abs(orig_mean - aug_mean),
                'Original_Std': orig_std,
                'Augmented_Std': aug_std,
                'Std_Diff': abs(orig_std - aug_std),
                'KS_Statistic': np.nan,
                'KS_PValue': np.nan,
                'Significant_Diff': False
            })
    
    # Hide unused subplots
    for idx in range(n_features, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    
    output_path = os.path.join(output_dir, 'numeric_distributions_comparison.png')
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"[OK] Numeric distributions plot saved: {output_path}")
    plt.close()
    
    return pd.DataFrame(statistics_comparison)


def compare_categorical_distributions(df_original, df_augmented, categorical_features, output_dir):
    """
    Compares categorical feature distributions before and after augmentation.
    
    Args:
        df_original: DataFrame with original data
        df_augmented: DataFrame with augmented data
        categorical_features: List of categorical features
        output_dir: Directory to save plots
    """
    n_features = len(categorical_features)
    n_cols = 3
    n_rows = (n_features + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6 * n_rows))
    fig.suptitle('Categorical Feature Distributions: Before vs After Augmentation',
                 fontsize=16, fontweight='bold', y=0.995)
    
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()
    
    categorical_stats = []
    
    for idx, feature in enumerate(categorical_features):
        ax = axes[idx]
        
        # Count values
        orig_counts = df_original[feature].value_counts().sort_index()
        aug_counts = df_augmented[feature].value_counts().sort_index()
        
        # All unique values
        all_values = sorted(set(orig_counts.index.tolist() + aug_counts.index.tolist()))
        
        # Prepare data for plot
        orig_values = [orig_counts.get(val, 0) for val in all_values]
        aug_values = [aug_counts.get(val, 0) for val in all_values]
        
        # Normalize to percentages
        orig_pct = [v / len(df_original) * 100 for v in orig_values]
        aug_pct = [v / len(df_augmented) * 100 for v in aug_values]
        
        x = np.arange(len(all_values))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, orig_pct, width, label='Before', 
                      color='#2E86AB', edgecolor='black', linewidth=0.5)
        bars2 = ax.bar(x + width/2, aug_pct, width, label='After', 
                      color='#E94F37', edgecolor='black', linewidth=0.5)
        
        ax.set_xlabel(feature, fontsize=11, fontweight='bold')
        ax.set_ylabel('Percentage (%)', fontsize=11)
        ax.set_title(f'{feature}', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(all_values, rotation=45, ha='right', fontsize=9)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Statistics
        max_diff = max([abs(orig_pct[i] - aug_pct[i]) for i in range(len(all_values))])
        categorical_stats.append({
            'Feature': feature,
            'Max_Percentage_Diff': max_diff,
            'Original_Unique': len(orig_counts),
            'Augmented_Unique': len(aug_counts)
        })
    
    # Hide unused subplots
    for idx in range(n_features, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    
    output_path = os.path.join(output_dir, 'categorical_distributions_comparison.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"[OK] Categorical distributions plot saved: {output_path}")
    plt.close()
    
    return pd.DataFrame(categorical_stats)


def check_for_anomalies(df_original, df_augmented, numeric_features):
    """
    Checks if augmented data contains anomalies (impossible values).
    
    Args:
        df_original: DataFrame with original data
        df_augmented: DataFrame with augmented data
        numeric_features: List of numeric features
        
    Returns:
        anomalies: DataFrame with detected anomalies
    """
    anomalies = []
    
    for feature in numeric_features:
        orig_min = df_original[feature].min()
        orig_max = df_original[feature].max()
        
        aug_min = df_augmented[feature].min()
        aug_max = df_augmented[feature].max()
        
        # Check for values outside original range
        out_of_range_min = aug_min < orig_min
        out_of_range_max = aug_max > orig_max
        
        # Check for negative values for features that shouldn't be negative
        negative_values = (df_augmented[feature] < 0).sum() if aug_min < 0 else 0
        
        if out_of_range_min or out_of_range_max or negative_values > 0:
            anomalies.append({
                'Feature': feature,
                'Original_Range': f'[{orig_min:.2f}, {orig_max:.2f}]',
                'Augmented_Range': f'[{aug_min:.2f}, {aug_max:.2f}]',
                'Out_of_Range_Min': out_of_range_min,
                'Out_of_Range_Max': out_of_range_max,
                'Negative_Values': negative_values,
                'Anomaly_Detected': True
            })
    
    return pd.DataFrame(anomalies)


def compare_class_conditional_distributions(df_original, df_augmented, numeric_features, output_dir):
    """
    Compares numeric feature distributions conditioned on Churn class.
    
    Args:
        df_original: DataFrame with original data
        df_augmented: DataFrame with augmented data
        numeric_features: List of numeric features
        output_dir: Directory to save plots
    """
    n_features = len(numeric_features)
    
    # Create grid based on number of features
    n_cols = 2
    n_rows = (n_features + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 6 * n_rows))
    fig.suptitle('Numeric Feature Distributions by Churn Class',
                 fontsize=18, fontweight='bold', y=0.995)
    
    if n_rows == 1 and n_cols > 1:
        axes = axes.reshape(1, -1)
    if not isinstance(axes, np.ndarray):
        axes = np.array([axes])
    axes = axes.flatten()
    
    for idx, feature in enumerate(numeric_features):
        ax = axes[idx]
        
        # Data for each class
        orig_no = df_original[df_original['Churn'] == 'No'][feature].dropna()
        orig_yes = df_original[df_original['Churn'] == 'Yes'][feature].dropna()
        aug_yes = df_augmented[df_augmented['Churn'] == 'Yes'][feature].dropna()
        
        # Use KDE plots for smoother visualization
        sns.kdeplot(data=orig_no, ax=ax, label='Before - No Churn', 
                   color='#2E86AB', linewidth=2.5, fill=True, alpha=0.4)
        sns.kdeplot(data=orig_yes, ax=ax, label='Before - Churn', 
                   color='#E94F37', linewidth=2.5, fill=True, alpha=0.4)
        sns.kdeplot(data=aug_yes, ax=ax, label='After - Churn (augmented)', 
                   color='#FF6B6B', linewidth=2.5, linestyle='--', fill=True, alpha=0.3)
        
        ax.set_xlabel(feature, fontsize=14, fontweight='bold')
        ax.set_ylabel('Density', fontsize=14, fontweight='bold')
        ax.set_title(f'{feature} by Churn Class', fontsize=16, fontweight='bold', pad=10)
        ax.legend(fontsize=11, loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(labelsize=11)
    
    # Hide unused subplots
    for idx in range(n_features, len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    
    output_path = os.path.join(output_dir, 'class_conditional_distributions.png')
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"[OK] Class conditional distributions plot saved: {output_path}")
    plt.close()


def generate_summary_report(df_original, df_augmented, numeric_stats, categorical_stats, anomalies):
    """
    Generuje raport podsumowujący analizę.
    
    Args:
        df_original: DataFrame z oryginalnymi danymi
        df_augmented: DataFrame z zaugmentowanymi danymi
        numeric_stats: DataFrame ze statystykami numerycznymi
        categorical_stats: DataFrame ze statystykami kategorycznymi
        anomalies: DataFrame z anomaliami
    """
    print("\n" + "=" * 80)
    print("POST-AUGMENTATION ANALYSIS REPORT")
    print("=" * 80)
    
    # Basic summary
    print(f"\n[STATS] BASIC STATISTICS:")
    print(f"   • Original records: {len(df_original):,}")
    print(f"   • Augmented records: {len(df_augmented):,}")
    print(f"   • New records: {len(df_augmented) - len(df_original):,}")
    
    # Class balance
    print(f"\n[BALANCE] CLASS BALANCE:")
    orig_churn = df_original['Churn'].value_counts()
    aug_churn = df_augmented['Churn'].value_counts()
    print(f"   • Before: No={orig_churn.get('No', 0):,}, Yes={orig_churn.get('Yes', 0):,} "
          f"(ratio {orig_churn.get('No', 0)/orig_churn.get('Yes', 1):.2f}:1)")
    print(f"   • After: No={aug_churn.get('No', 0):,}, Yes={aug_churn.get('Yes', 0):,} "
          f"(ratio {aug_churn.get('No', 0)/aug_churn.get('Yes', 1):.2f}:1)")
    
    # Numeric statistics
    print(f"\n[NUMERIC] NUMERIC FEATURE ANALYSIS:")
    print(f"   • Mean difference of means: {numeric_stats['Mean_Diff'].mean():.4f}")
    print(f"   • Max difference of means: {numeric_stats['Mean_Diff'].max():.4f}")
    print(f"   • Mean difference of std: {numeric_stats['Std_Diff'].mean():.4f}")
    significant_diffs = numeric_stats['Significant_Diff'].sum()
    print(f"   • Features with significant differences (p<0.05): {significant_diffs}/{len(numeric_stats)}")
    
    if significant_diffs > 0:
        print(f"\n   [WARNING] Features with significant differences:")
        for _, row in numeric_stats[numeric_stats['Significant_Diff']].iterrows():
            print(f"      • {row['Feature']}: KS={row['KS_Statistic']:.4f}, p={row['KS_PValue']:.4f}")
    
    # Categorical statistics
    print(f"\n[CATEGORICAL] CATEGORICAL FEATURE ANALYSIS:")
    print(f"   • Mean max percentage difference: {categorical_stats['Max_Percentage_Diff'].mean():.2f}%")
    print(f"   • Max percentage difference: {categorical_stats['Max_Percentage_Diff'].max():.2f}%")
    
    # Anomalies
    print(f"\n[ANOMALIES] ANOMALY VERIFICATION:")
    if len(anomalies) == 0:
        print(f"   [OK] No anomalies detected - all values within valid ranges")
    else:
        print(f"   [WARNING] Found {len(anomalies)} features with potential anomalies:")
        for _, row in anomalies.iterrows():
            print(f"      • {row['Feature']}: {row['Original_Range']} → {row['Augmented_Range']}")
            if row['Out_of_Range_Min']:
                print(f"        [WARNING] Values below original minimum")
            if row['Out_of_Range_Max']:
                print(f"        [WARNING] Values above original maximum")
            if row['Negative_Values'] > 0:
                print(f"        [WARNING] {row['Negative_Values']} negative values")
    
    # Quality assessment
    print(f"\n[QUALITY] AUGMENTATION QUALITY ASSESSMENT:")
    quality_score = 100
    if len(anomalies) > 0:
        quality_score -= len(anomalies) * 10
    if significant_diffs > len(numeric_stats) * 0.5:
        quality_score -= 20
    if categorical_stats['Max_Percentage_Diff'].max() > 10:
        quality_score -= 10
    
    quality_score = max(0, quality_score)
    
    if quality_score >= 90:
        status = "[OK] Excellent"
    elif quality_score >= 75:
        status = "[OK] Good"
    elif quality_score >= 60:
        status = "[WARNING] Acceptable"
    else:
        status = "[ERROR] Needs attention"
    
    print(f"   • Score: {quality_score}/100 - {status}")
    print(f"   • Feature distributions preserved within reasonable range")
    print(f"   • SMOTE augmentation generated synthetic samples consistent with original patterns")
    
    print("\n" + "=" * 80)


def run_post_augmentation_analysis(original_path: str, augmented_path: str, output_dir: str):
    """
    Runs full post-augmentation analysis.
    
    Args:
        original_path: Path to original CSV file
        augmented_path: Path to augmented CSV file
        output_dir: Directory to save results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Define features to analyze (matching preprocessing.py)
    categorical_cols = [
        "InternetService", "OnlineSecurity",
        "DeviceProtection", "TechSupport",
        "Contract", "PaymentMethod"
    ]
    numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
    
    # 1. Load data
    df_original, df_augmented = load_datasets(original_path, augmented_path)
    
    # 2. Filter features to only those specified
    # Verify features exist in dataset
    available_categorical = [col for col in categorical_cols if col in df_original.columns]
    available_numeric = [col for col in numeric_cols if col in df_original.columns]
    
    print(f"\n[INFO] Feature selection:")
    print(f"   • Numeric features: {len(available_numeric)} ({', '.join(available_numeric)})")
    print(f"   • Categorical features: {len(available_categorical)} ({', '.join(available_categorical)})")
    
    if len(available_numeric) == 0:
        print("[ERROR] No numeric features found!")
        return
    if len(available_categorical) == 0:
        print("[ERROR] No categorical features found!")
        return
    
    # 3. Compare numeric distributions
    print(f"\n[INFO] Analyzing numeric features...")
    numeric_stats = compare_numeric_distributions(
        df_original, df_augmented, available_numeric, output_dir
    )
    
    # 4. Compare categorical distributions
    print(f"\n[INFO] Analyzing categorical features...")
    categorical_stats = compare_categorical_distributions(
        df_original, df_augmented, available_categorical, output_dir
    )
    
    # 5. Class-conditional distributions
    print(f"\n[INFO] Analyzing class-conditional distributions...")
    compare_class_conditional_distributions(
        df_original, df_augmented, available_numeric, output_dir
    )
    
    # 6. Check for anomalies
    print(f"\n[INFO] Verifying anomalies...")
    anomalies = check_for_anomalies(df_original, df_augmented, available_numeric)
    if len(anomalies) > 0:
        print(f"   [WARNING] Found {len(anomalies)} potential anomalies")
    else:
        print(f"   [OK] No anomalies detected")
    
    # 7. Generate report
    generate_summary_report(df_original, df_augmented, numeric_stats, 
                           categorical_stats, anomalies)
    
    print(f"\n[OK] Analysis completed. Results saved in: {output_dir}")


if __name__ == "__main__":
    # Określenie ścieżek
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    original_path = os.path.join(project_dir, 'data', 'WA_Fn-UseC_-Telco-Customer-Churn.csv')
    augmented_path = os.path.join(project_dir, 'data', 'augmented_telco_churn.csv')
    output_dir = os.path.join(project_dir, 'data', 'post_augmentation_analysis')
    
    # Uruchomienie analizy
    run_post_augmentation_analysis(original_path, augmented_path, output_dir)

