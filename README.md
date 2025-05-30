# wind-compass

**テスト実行・開発前のセットアップ**

```bash
pip install -e .
```

これにより、sys.path操作なしで `pytest` などのテストが動作します。

---

# wind_compass CLI

## 使い方

### シミュレーション実行

```sh
python -m wind_compass --wind-data <CSVファイル> --config-file <JSONファイル> --angles 0,90 --gear-ratios 3,5
```

- `--angles`や`--gear-ratios`はカンマ区切りまたは複数指定可
- `--help`で詳細なヘルプが表示されます

### 例

```sh
python -m wind_compass --wind-data data.csv --config-file config.json --angles 0,90 --gear-ratios 3,5
```

> 旧: `python main.py ...` も動作しますが、今後は `python -m wind_compass ...` を推奨します。