import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns
from collections import Counter
import re
import warnings


#dogsy
dog_service =  ['Передержка собак', 'Передержка кошек', 'Выгул собак']
dog_reasons = ['Проверяем догситтеров', 'Заключается договор', 'Бесплатная предварительная встреча', 'Менеджеры Догси насвязи 24/7', 'В каждую передержку входит бесплатная онлайн-консультация ветеринараБесплатная онлайн-консультация ветеринара']

#murchalkin
cat_service = ['Передержка кошек: от 1390₽/СУТ', 'Няня на час: от 860₽', 'Экспресс-няня: от 740₽']
cat_reasons = ['Ветеринарная поддержка', 'Пробное знакомство', 'Страхование от несчастных случаев', 'Профессионализм специалистов', 'Всегда на связи', 'Ответственность', 'Забота и уход', 'Команда, которой доверяют', 'На связи 7 дней в неделю']

#mospet
mos_service = ['Советы владельцам', 'Экстренные ситуации', 'Уход и сервис', 'Прививки и лечение', 'Неравнодушным', 'Будущему хозяину']


def remove_double(text):
    capitals = re.finditer(r'[А-Я]', text)
    capitals_positions = [m.start() for m in capitals]

    if len(capitals_positions) >= 2:
        return text[:capitals_positions[1]]
    return text

dog_reasons = [remove_double(reason) for reason in dog_reasons]


def get_price(s): return s.split(': ', 1)[1] if ': от ' in s else 'нет доп инфо'
def get_name(s): return s.split(': ', 1)[0] if ': от ' in s else s

df = pd.DataFrame(
    [{'название_сайта': 'Dogsy', 'вид': 'услуга', 'услуга_или_преимущество': s, 'доп_инфо': 'нет доп инфо'} for s in dog_service] +
    [{'название_сайта': 'Dogsy', 'вид': 'преимущества', 'услуга_или_преимущество': r, 'доп_инфо': 'нет доп инфо'} for r in dog_reasons] +
    [{'название_сайта': 'Мурчалкин', 'вид': 'услуга', 'услуга_или_преимущество': get_name(s), 'доп_инфо': get_price(s)} for s in cat_service] +
    [{'название_сайта': 'Мурчалкин', 'вид': 'преимущества', 'услуга_или_преимущество': r, 'доп_инфо': 'нет доп инфо'} for r in cat_reasons] +
    [{'название_сайта': 'Моспитомец', 'вид': 'услуга', 'услуга_или_преимущество': s, 'доп_инфо': 'нет доп инфо'} for s in mos_service],
    columns=['название_сайта', 'вид', 'услуга_или_преимущество', 'доп_инфо']
)

print(df.to_string(index=True))



warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'Arial Unicode MS'
plt.rcParams['axes.unicode_minus'] = False


col_site = 'название_сайта'
col_type = 'вид'
col_name = 'услуга_или_преимущество'
col_info = 'доп_инфо'

fig = plt.figure(figsize=(15, 12))

#first plot
ax1 = fig.add_subplot(2, 3, 1)
site_counts = df[col_site].value_counts()
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
bars = ax1.bar(range(len(site_counts)), site_counts.values, color=colors[:len(site_counts)], edgecolor='black')
ax1.set_xticks(range(len(site_counts)))
ax1.set_xticklabels(site_counts.index, rotation=15, ha='right')
ax1.set_title('Количество позиций по сайтам', fontsize=12, fontweight='bold')
ax1.set_ylabel('Количество')
ax1.set_xlabel('Название сайта')
for bar, val in zip(bars, site_counts.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
             str(val), ha='center', va='bottom', fontweight='bold')

#second plot
ax2 = fig.add_subplot(2, 3, 2)
grouped = df.groupby([col_site, col_type]).size().unstack(fill_value=0)
grouped.plot(kind='bar', ax=ax2, color=['#4ECDC4', '#FF6B6B'], edgecolor='black')
ax2.set_title('Услуги vs Преимущества по сайтам', fontsize=12, fontweight='bold')
ax2.set_xlabel('Название сайта')
ax2.set_ylabel('Количество')
ax2.legend(title='Вид')
ax2.tick_params(axis='x', rotation=15)

#third plot
ax3 = fig.add_subplot(2, 3, 3)
type_counts = df[col_type].value_counts()
colors_pie = ['#4ECDC4', '#FF6B6B']
wedges, texts, autotexts = ax3.pie(type_counts.values, labels=type_counts.index,
                                    autopct='%1.1f%%', colors=colors_pie, startangle=90)
ax3.set_title('Общее распределение', fontsize=12, fontweight='bold')
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

#forth plot
ax4 = fig.add_subplot(2, 3, 4)
if col_info in df.columns:
    services_with_prices = df[(df[col_site] == 'Мурчалкин') & (df[col_type] == 'услуга')]
    if not services_with_prices.empty:
        import re
        prices = []
        service_names = []
        for idx, row in services_with_prices.iterrows():
            price_str = row[col_info]
            numbers = re.findall(r'\d+', price_str)
            if numbers:
                prices.append(int(numbers[0]))
                service_names.append(row[col_name][:20])
        if prices:
            bars = ax4.bar(range(len(prices)), prices, color='#FFD93D', edgecolor='black')
            ax4.set_xticks(range(len(prices)))
            ax4.set_xticklabels(service_names, rotation=15, ha='right', fontsize=9)
            ax4.set_title('Цены на услуги Мурчалкина', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Цена (руб)')
            ax4.set_xlabel('Услуга')
            for bar, price in zip(bars, prices):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                        f'{price} руб', ha='center', va='bottom', fontweight='bold', fontsize=9)

#fifth plot
ax5 = fig.add_subplot(2, 3, 5)
df['длина_названия'] = df[col_name].str.len()
avg_length = df.groupby(col_site)['длина_названия'].mean()
bars = ax5.bar(range(len(avg_length)), avg_length.values, color='#96CEB4', edgecolor='black')
ax5.set_xticks(range(len(avg_length)))
ax5.set_xticklabels(avg_length.index, rotation=15, ha='right')
ax5.set_title('Средняя длина названий по сайтам', fontsize=12, fontweight='bold')
ax5.set_ylabel('Средняя длина (символы)')
ax5.set_xlabel('Название сайта')
for bar, val in zip(bars, avg_length.values):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f'{val:.1f}', ha='center', va='bottom', fontweight='bold')

#sixth plot
ax6 = fig.add_subplot(2, 3, 6)
all_text = ' '.join(df[col_name].astype(str).values)
words = all_text.split()
exclude_words = {'и', 'в', 'на', 'с', 'по', 'из', 'у', 'о', 'для', 'от', 'до', 'за', 'к', 'со', 'при'}
words = [w for w in words if len(w) > 3 and w not in exclude_words]
word_counts = Counter(words).most_common(8)
if word_counts:
    words_top = [w[0] for w in word_counts]
    counts_top = [w[1] for w in word_counts]
    bars = ax6.barh(range(len(words_top)), counts_top, color='#FFB347', edgecolor='black')
    ax6.set_yticks(range(len(words_top)))
    ax6.set_yticklabels(words_top)
    ax6.set_title('Частые слова в названиях', fontsize=12, fontweight='bold')
    ax6.set_xlabel('Частота')
    ax6.invert_yaxis()

plt.suptitle('Анализ услуг сайтов о питомцах', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('services_analysis_full.png', dpi=150, bbox_inches='tight')
plt.show()

