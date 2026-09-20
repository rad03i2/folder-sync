# Folder Sync

A safe, local, preview-first **one-way folder synchronization** CLI for Python. Folder Sync mirrors files from a source directory into a destination while making destructive behavior explicit and verifiable.

> Author: **Radwan Abdulhadi Ahmed — رضوان عبدالهادي أحمد — [@rad03i2](https://github.com/rad03i2)**

## Why this project?

Simple copy commands become risky when used repeatedly: stale destination files, accidental nesting, silent overwrites, and changed files between preview and execution can produce surprising results. Folder Sync is deliberately conservative: preview is the default, deletion is opt-in, copied bytes can be SHA-256 verified, and a plan becomes invalid when a source or deletion target changes.

## Features

- One-way source → destination synchronization.
- Preview-only by default; `--apply` is required to write.
- Detects new and changed files using size + SHA-256.
- Optional `--delete` for destination-only files; never enabled implicitly.
- Refuses identical or nested source/destination roots.
- Does not follow symbolic links.
- Hidden files/directories are excluded by default and can be opted in.
- Atomic copy/update: data is copied to a sibling temporary file then moved into place.
- Re-validates source hashes immediately before copying.
- Protects delete actions if the destination changed after preview.
- Optional post-copy SHA-256 verification.
- JSON plan output and JSON execution manifest.
- Cross-platform Python implementation with no runtime third-party dependencies.

## Requirements

- Python 3.10+
- Read access to the source and appropriate write access to the destination when applying.

## Installation

```bash
git clone https://github.com/rad03i2/folder-sync.git
cd folder-sync
python -m pip install -e .
```

## Usage

Preview a synchronization:

```bash
folder-sync ./source ./backup
```

Apply exactly the freshly calculated plan:

```bash
folder-sync ./source ./backup --apply --manifest sync-manifest.json
```

Preview destination-only deletions:

```bash
folder-sync ./source ./backup --delete
```

Only after reviewing that preview, execute them:

```bash
folder-sync ./source ./backup --delete --apply --manifest sync-manifest.json
```

Machine-readable plan:

```bash
folder-sync ./source ./backup --json
```

Include dotfiles and hidden directories:

```bash
folder-sync ./source ./backup --include-hidden
```

Verification is enabled by default. `--no-verify` skips only the *post-copy* hash check; preview/apply change detection remains in place.

## Python API

```python
from pathlib import Path
from folder_sync import apply, plan

source = Path("source")
destination = Path("backup")
actions = plan(source, destination)
apply(source, destination, actions, manifest=Path("manifest.json"))
```

## Safety model

Folder Sync is a synchronization utility, not a versioned backup system. An `update` replaces the destination copy after a successful temporary-file copy. If historical versions matter, point it at a versioned/snapshotted destination or use dedicated backup software. `--delete` permanently removes destination-only files and should be used only after reviewing the preview. The tool intentionally rejects nested roots because they can recursively ingest synchronization output.

Symbolic links are skipped rather than dereferenced. Special filesystem objects are not synchronized. Files may still change during extremely narrow filesystem race windows; the pre-copy hash and post-copy verification substantially reduce this risk but do not provide filesystem snapshot semantics.

## Project structure

```text
src/folder_sync/core.py   planning, hashing, validation, atomic execution
src/folder_sync/cli.py    command-line interface
src/folder_sync/__init__.py public Python API
tests/test_core.py        safety and end-to-end behavior tests
.github/workflows/ci.yml  cross-platform lint/test matrix
```

## Testing

```bash
python -m pip install -e . pytest ruff
ruff check src tests
pytest -q
```

CI runs linting and tests on Ubuntu, Windows, and macOS with Python 3.10, 3.12, and 3.13.

## Privacy & security

All synchronization and hashing are local. The application has no network code, telemetry, accounts, or API keys. Treat manifests as potentially sensitive because they contain absolute source/destination paths and relative filenames.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security-sensitive reports should follow [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).

## Author

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **[@rad03i2](https://github.com/rad03i2)**

---

# Folder Sync — العربية

أداة Python محلية وآمنة لمزامنة المجلدات **باتجاه واحد** من المصدر إلى الوجهة. صُممت بحيث تكون المعاينة هي الوضع الافتراضي، ولا يجري أي تعديل فعلي إلا عند طلبه صراحةً.

## لماذا هذا المشروع؟

تكرار نسخ المجلدات يدويًا قد يؤدي إلى استبدال ملفات أو إبقاء ملفات قديمة أو مزامنة مجلد داخل نفسه. لذلك يعتمد Folder Sync أسلوبًا محافظًا: يعرض الخطة أولًا، ويجعل الحذف اختياريًا، ويتحقق من المحتوى باستخدام SHA-256، ويرفض التنفيذ إذا تغير الملف بعد المعاينة.

## المميزات

- مزامنة باتجاه واحد: المصدر ← إلى الوجهة.
- المعاينة فقط هي الوضع الافتراضي، والتنفيذ يحتاج `--apply`.
- اكتشاف الملفات الجديدة والمتغيرة بالحجم وSHA-256.
- حذف الملفات الموجودة في الوجهة فقط عبر `--delete` بشكل اختياري وصريح.
- منع اختيار مسارين متطابقين أو متداخلين.
- عدم تتبع الروابط الرمزية.
- تجاهل الملفات والمجلدات المخفية افتراضيًا مع إمكانية تضمينها.
- نسخ ذري عبر ملف مؤقت قبل استبدال ملف الوجهة.
- إعادة التحقق من بصمة المصدر قبل النسخ مباشرة.
- رفض حذف ملف تغيّر بعد المعاينة.
- التحقق من SHA-256 بعد النسخ افتراضيًا.
- إخراج خطة JSON وحفظ Manifest لعملية التنفيذ.
- يعمل على الأنظمة الرئيسية دون مكتبات تشغيل خارجية.

## التثبيت

```bash
git clone https://github.com/rad03i2/folder-sync.git
cd folder-sync
python -m pip install -e .
```

## الاستخدام

معاينة المزامنة:

```bash
folder-sync ./source ./backup
```

التنفيذ مع حفظ سجل JSON:

```bash
folder-sync ./source ./backup --apply --manifest sync-manifest.json
```

معاينة الحذف أولًا:

```bash
folder-sync ./source ./backup --delete
```

ثم بعد مراجعة النتائج فقط:

```bash
folder-sync ./source ./backup --delete --apply
```

## الأمان والخصوصية

كل العمل محلي ولا توجد اتصالات شبكة أو Telemetry أو مفاتيح API. الحذف ليس افتراضيًا. يجب الانتباه إلى أن الأداة **ليست نظام نسخ احتياطي بإصدارات**؛ تحديث ملف يستبدل نسخة الوجهة، والحذف باستخدام `--delete` دائم. كما أن ملف Manifest قد يحتوي مسارات وأسماء ملفات حساسة، لذلك احفظه في مكان مناسب.

## الاختبارات

```bash
python -m pip install -e . pytest ruff
ruff check src tests
pytest -q
```

توجد اختبارات لسلوك النسخ والتحديث، ثبات المزامنة بعد التنفيذ، حماية الحذف، تغير المصدر بعد المعاينة، المسارات المتداخلة، الملفات المخفية، وManifest. كما أن CI مُعدّ لـ Windows وLinux وmacOS.

## المساهمة والترخيص

راجع [CONTRIBUTING.md](CONTRIBUTING.md) للمساهمة و[SECURITY.md](SECURITY.md) للملاحظات الأمنية. المشروع مرخص بترخيص MIT الموجود في [LICENSE](LICENSE).

## المؤلف

**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **[@rad03i2](https://github.com/rad03i2)**
