import pandas as pd

# Jämför gamla och nya resultaten
print('🏆 JÄMFÖRELSE: ORIGINAL VS FÖRBÄTTRAD TRÄNING 🏆')
print('=' * 55)

# Gamla resultatet (från tidigare träning)
old_map = 0.27256
old_precision = 0.44399
old_recall = 0.29412

print('📊 ORIGINAL TRÄNING (YOLOv8n):')
print(f'   mAP50: {old_map:.4f} ({old_map*100:.2f}%)')
print(f'   Precision: {old_precision:.4f} ({old_precision*100:.2f}%)')
print(f'   Recall: {old_recall:.4f} ({old_recall*100:.2f}%)')

# Nya resultatet
try:
    df = pd.read_csv('results.csv')
    final = df.iloc[-1]

    new_map = final['metrics/mAP50(B)']
    new_precision = final['metrics/precision(B)']
    new_recall = final['metrics/recall(B)']
    training_time = final['time']

    print(f'\n🚀 FÖRBÄTTRAD TRÄNING (YOLOv8s + Augmentation):')
    print(f'   mAP50: {new_map:.4f} ({new_map*100:.2f}%)')
    print(f'   Precision: {new_precision:.4f} ({new_precision*100:.2f}%)')
    print(f'   Recall: {new_recall:.4f} ({new_recall*100:.2f}%)')

    print(f'\n📈 FÖRBÄTTRINGAR:')
    map_improvement = (new_map - old_map) / old_map * 100
    precision_improvement = (new_precision - old_precision) / old_precision * 100
    recall_improvement = (new_recall - old_recall) / old_recall * 100

    print(f'   mAP50: {map_improvement:+.1f}% förbättring')
    print(f'   Precision: {precision_improvement:+.1f}% förbättring') 
    print(f'   Recall: {recall_improvement:+.1f}% förbättring')

    print(f'\n🎯 SLUTANALYS:')
    if new_map > old_map:
        print(f'   ✅ FRAMGÅNG! Modellen blev bättre!')
        print(f'   🎖️  Ny mAP50: {new_map*100:.1f}% (vs gamla {old_map*100:.1f}%)')
    else:
        print(f'   ⚠️  Ingen stor förbättring i mAP50')

    print(f'\n⏱️  TRÄNINGSINFO:')
    print(f'   Totala epochs: {len(df)}')
    print(f'   Träningstid: {training_time/3600:.1f} timmar')
    print(f'   Modelltyp: YOLOv8s (3M parametrar)')
    
    print(f'\n🏆 SAMMANTAGET:')
    if any([map_improvement > 0, precision_improvement > 0, recall_improvement > 0]):
        print(f'   Den förbättrade träningen lyckades!')
        print(f'   Du har nu två modeller att välja mellan')
    else:
        print(f'   Första modellen var redan mycket bra!')
    
except Exception as e:
    print(f'Fel vid läsning: {e}')