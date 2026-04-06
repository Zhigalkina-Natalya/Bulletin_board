import os

import coverage
import matplotlib.pyplot as plt
import pandas as pd

cov = coverage.Coverage(data_file=".coverage")
cov.load()

files = list(cov.get_data().measured_files())

data = []

for f in files:
    try:
        analysis = cov.analysis2(f)

        filename = analysis[0]
        statements = analysis[1]
        missing = analysis[3]

        total = len(statements)
        covered = total - len(missing)

        percent = (covered / total * 100) if total > 0 else 0

        short_name = os.path.relpath(filename)

        data.append({"file": short_name, "coverage": percent})

    except Exception as e:
        print(f"Пропущен файл {f}: {e}")

df = pd.DataFrame(data).sort_values("coverage")

plt.figure(figsize=(10, 6))
plt.barh(df["file"], df["coverage"])

plt.xlabel("Покрытие (%)")
plt.title("Покрытие кода по файлам")
plt.xlim(0, 100)

plt.tight_layout()
plt.savefig("coverage_chart.png")

print("Диаграмма сохранена: coverage_chart.png")
