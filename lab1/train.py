from pathlib import Path
import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

X, y = load_iris(return_X_y=True)
model = RandomForestClassifier(n_estimators=50, random_state=42).fit(X, y)
joblib.dump(model, Path(__file__).parent / 'model.joblib')
print('Trained on', len(y), 'samples')
