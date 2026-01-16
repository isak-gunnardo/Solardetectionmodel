print('🔍 SOLCELLS-DETEKTERINGSANALYS 🔍')
print('=' * 45)

# Data från den slutliga träningen
final_recall = 0.29412
final_precision = 0.44399
final_map50 = 0.27256

print(f'📊 ANDEL SOLCELLER SOM HITTAS:')
print(f'   Recall: {final_recall:.1%} ({final_recall:.4f})')
print(f'   ➡️  Modellen hittar {final_recall:.1%} av alla solceller som finns!')

print(f'\n🎯 NOGGRANNHET I DETEKTERINGARNA:')  
print(f'   Precision: {final_precision:.1%} ({final_precision:.4f})')
print(f'   ➡️  När modellen säger "solcell", så stämmer det {final_precision:.1%} av gångerna')

print(f'\n📈 OVERALL PRESTANDA:')
print(f'   mAP50: {final_map50:.1%} ({final_map50:.4f})')
print(f'   ➡️  Övergripande detekteringskvalitet: {final_map50:.1%}')

print(f'\n🤔 VAD BETYDER DETTA I PRAKTIKEN?')
print(f'   Om en bild har 100 solceller:')
print(f'   • Modellen hittar ~{final_recall*100:.0f} av dem')
print(f'   • Den missar ~{(1-final_recall)*100:.0f} solceller') 
print(f'   • Av de {final_recall*100:.0f} detekterade är ~{final_precision*final_recall*100:.0f} korrekta')
print(f'   • ~{(1-final_precision)*final_recall*100:.0f} är felaktiga detekteringar')

print(f'\n📋 KVALITETSBEDÖMNING:')
if final_recall >= 0.8:
    recall_grade = '🥇 EXCELLENT (≥80%)'
elif final_recall >= 0.6:
    recall_grade = '🥈 GOOD (60-80%)'
elif final_recall >= 0.4:
    recall_grade = '🥉 DECENT (40-60%)'
elif final_recall >= 0.2:
    recall_grade = '⚠️  FAIR (20-40%)'
else:
    recall_grade = '❌ POOR (<20%)'

print(f'   Recall-kvalitet: {recall_grade}')

print(f'\n💡 FÖRBÄTTRINGSMÖJLIGHETER:')
print(f'   För att hitta fler solceller (höja recall):')
print(f'   • Fler träningsexempel med solceller')
print(f'   • Mer varierat dataset (olika vinklar, väder)')
print(f'   • Längre träning eller större modell')
print(f'   • Data augmentation (rotation, ljusförändringar)')

print(f'\n🎯 BALANS PRECISION VS RECALL:')
f1_score = 2 * (final_precision * final_recall) / (final_precision + final_recall)
print(f'   F1-score: {f1_score:.3f} ({f1_score:.1%})')
print(f'   ➡️  Balanserat mått mellan precision och recall')

print(f'\n🏠 EXEMPEL PÅ ETT BOSTADSOMRÅDE:')
print(f'   Om området har 50 hus med solceller:')
print(f'   • Modellen hittar ~{int(final_recall*50)} av husen')
print(f'   • {50-int(final_recall*50)} hus med solceller missas')
print(f'   • Detta är {final_recall:.1%} upptäcktsgrad')