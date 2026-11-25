import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score

with open('backend/data/ins_taxonomy.json', 'r', encoding='utf-8') as f:
    tax = json.load(f)

STANDARD_CLASSES = [
    'Color', 'Preservative', 'Acidity regulator', 'Emulsifier', 
    'Antioxidant', 'Flavor enhancer', 'Sweetener', 'Anti-caking agent', 
    'Thickener', 'Stabilizer'
]

texts = []
labels = []

for k, v in tax.items():
    name = v.get('name', '')
    desc = v.get('description', '')
    alts = ' '.join(v.get('alternative_names', []))
    text = f'{name} {alts} {desc}'.strip()
    
    target_cls = None
    for fc in v.get('functional_categories', []):
        if fc in STANDARD_CLASSES:
            target_cls = fc
            break
    if not target_cls:
        c = v.get('class', '')
        if c in STANDARD_CLASSES:
            target_cls = c
        else:
            target_cls = 'Other'
            
    texts.append(text)
    labels.append(target_cls)

pipe = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000, sublinear_tf=True)),
    ('clf', LogisticRegression(max_iter=1000, C=1.0, random_state=42))
])

scores = cross_val_score(pipe, texts, labels, cv=5)
print('5-fold CV Accuracy:', round(scores.mean(), 4), [round(s, 4) for s in scores])
pipe.fit(texts, labels)

test_samples = [
    'artificial red dye azo colorant',
    'sodium benzoate chemical antimicrobial preservative',
    'aspartame intense zero calorie sweetener',
    'monosodium glutamate umami savory taste enhancer',
    'xanthan gum viscosity thickening agent',
    'citric acid ph buffering sour agent'
]
preds = pipe.predict(test_samples)
probs = pipe.predict_proba(test_samples)
for s, p, pr in zip(test_samples, preds, probs):
    print(f'"{s}" -> {p} (prob: {max(pr):.3f})')
