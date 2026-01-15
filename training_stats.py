import pandas as pd
import numpy as np

# Läs in träningsdata
df = pd.read_csv('results.csv')

print('🏆 MEGA YOLO TRÄNINGSSTATISTIK 🏆')
print('=' * 50)

# Grundläggande info
print(f'📊 TRÄNINGSÖVERSIKT:')
print(f'   Totalt antal epochs: {len(df)}')
print(f'   Total träningstid: {df["time"].iloc[-1]/3600:.1f} timmar')
print(f'   Genomsnittlig tid per epoch: {df["time"].mean()/60:.1f} minuter')

print(f'\n🎯 SLUTRESULTAT (Epoch {len(df)}):')
final = df.iloc[-1]
print(f'   mAP50: {final["metrics/mAP50(B)"]:.4f} ({final["metrics/mAP50(B)"]*100:.2f}%)')
print(f'   mAP50-95: {final["metrics/mAP50-95(B)"]:.4f} ({final["metrics/mAP50-95(B)"]*100:.2f}%)')
print(f'   Precision: {final["metrics/precision(B)"]:.4f} ({final["metrics/precision(B)"]*100:.2f}%)')
print(f'   Recall: {final["metrics/recall(B)"]:.4f} ({final["metrics/recall(B)"]*100:.2f}%)')

print(f'\n📈 BÄSTA PRESTANDA UNDER TRÄNINGEN:')
best_map = df["metrics/mAP50(B)"].max()
best_epoch = df["metrics/mAP50(B)"].idxmax() + 1
print(f'   Bästa mAP50: {best_map:.4f} ({best_map*100:.2f}%) i epoch {best_epoch}')

best_precision = df["metrics/precision(B)"].max()
best_recall = df["metrics/recall(B)"].max()
print(f'   Bästa Precision: {best_precision:.4f} ({best_precision*100:.2f}%)')
print(f'   Bästa Recall: {best_recall:.4f} ({best_recall*100:.2f}%)')

print(f'\n🚀 FÖRBÄTTRING FRÅN START:')
first = df.iloc[0]
print(f'   mAP50: {first["metrics/mAP50(B)"]:.6f} → {final["metrics/mAP50(B)"]:.4f} = {final["metrics/mAP50(B)"]/first["metrics/mAP50(B)"]:.0f}x förbättring!')
print(f'   Precision: {first["metrics/precision(B)"]:.6f} → {final["metrics/precision(B)"]:.4f} = {final["metrics/precision(B)"]/first["metrics/precision(B)"]:.0f}x förbättring!')
print(f'   Recall: {first["metrics/recall(B)"]:.6f} → {final["metrics/recall(B)"]:.4f} = {final["metrics/recall(B)"]/first["metrics/recall(B)"]:.0f}x förbättring!')

print(f'\n📉 LOSS UTVECKLING:')
first_train_loss = first['train/box_loss'] + first['train/cls_loss'] + first['train/dfl_loss']
final_train_loss = final['train/box_loss'] + final['train/cls_loss'] + final['train/dfl_loss']
first_val_loss = first['val/box_loss'] + first['val/cls_loss'] + first['val/dfl_loss']
final_val_loss = final['val/box_loss'] + final['val/cls_loss'] + final['val/dfl_loss']

print(f'   Training Loss: {first_train_loss:.3f} → {final_train_loss:.3f} ({(final_train_loss-first_train_loss)/first_train_loss*100:+.1f}%)')
print(f'   Validation Loss: {first_val_loss:.3f} → {final_val_loss:.3f} ({(final_val_loss-first_val_loss)/first_val_loss*100:+.1f}%)')

print(f'\n⚡ MILSTOLPAR UNDER TRÄNINGEN:')
milestones = [10, 25, 50, 75, 100]
for milestone in milestones:
    if milestone <= len(df):
        row = df.iloc[milestone-1]
        print(f'   Epoch {milestone:3d}: mAP50={row["metrics/mAP50(B)"]:.4f}, P={row["metrics/precision(B)"]:.3f}, R={row["metrics/recall(B)"]:.3f}')

print(f'\n🔄 TRÄNINGSSTABILITET:')
map_values = df["metrics/mAP50(B)"].values[-20:]  # Sista 20 epochs
map_std = np.std(map_values) 
map_mean = np.mean(map_values)
print(f'   Standardavvikelse sista 20 epochs: {map_std:.4f}')
print(f'   Medelvärde sista 20 epochs: {map_mean:.4f}')
print(f'   Stabilitet: {"HÖG" if map_std < 0.01 else "MEDIUM" if map_std < 0.02 else "LÅG"}')

print(f'\n📊 DETALJERAD EPOCH-ANALYS:')
print(f'   Första signifikanta prestanda (mAP50 > 1%): Epoch {df[df["metrics/mAP50(B)"] > 0.01].index[0] + 1 if len(df[df["metrics/mAP50(B)"] > 0.01]) > 0 else "Aldrig"}')
print(f'   Första bra prestanda (mAP50 > 10%): Epoch {df[df["metrics/mAP50(B)"] > 0.1].index[0] + 1 if len(df[df["metrics/mAP50(B)"] > 0.1]) > 0 else "Aldrig"}')
print(f'   Första utmärkta prestanda (mAP50 > 20%): Epoch {df[df["metrics/mAP50(B)"] > 0.2].index[0] + 1 if len(df[df["metrics/mAP50(B)"] > 0.2]) > 0 else "Aldrig"}')

print(f'\n🎖️ TOP 5 BÄSTA EPOCHS (mAP50):')
top5 = df.nlargest(5, "metrics/mAP50(B)")
for idx, (index, row) in enumerate(top5.iterrows(), 1):
    print(f'   {idx}. Epoch {index+1}: mAP50={row["metrics/mAP50(B)"]:.4f} ({row["metrics/mAP50(B)"]*100:.2f}%)')

# Kontrollera om modellen overfittar
train_loss_trend = np.polyfit(range(len(df)), df['train/box_loss'] + df['train/cls_loss'] + df['train/dfl_loss'], 1)[0]
val_loss_trend = np.polyfit(range(len(df)), df['val/box_loss'] + df['val/cls_loss'] + df['val/dfl_loss'], 1)[0]

print(f'\n🔍 OVERFITTING-ANALYS:')
print(f'   Training loss trend: {train_loss_trend:+.6f} (negativ = förbättring)')
print(f'   Validation loss trend: {val_loss_trend:+.6f} (negativ = förbättring)')
if train_loss_trend < 0 and val_loss_trend > 0:
    print('   ⚠️  VARNING: Möjlig overfitting detekterad!')
elif train_loss_trend < 0 and val_loss_trend < 0:
    print('   ✅ Bra: Både training och validation förbättras')
else:
    print('   📊 Modellen är stabil')