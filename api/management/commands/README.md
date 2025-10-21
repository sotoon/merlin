# 🚨 DEVELOPMENT COMMANDS - DO NOT USE IN PRODUCTION

## ⚠️ WARNING

These commands are **ONLY for development and staging environments**. They contain **DANGEROUS operations** that can **DELETE DATA**.

## 🛡️ For Production Use

Use the production-safe commands in the parent directory:
- `import_users_prod.py` - Production-safe user import
- `import_org_structure_prod.py` - Production-safe org structure import  
- `import_ladders_prod.py` - Production-safe ladders import
- `import_history_prod.py` - Production-safe history import

## 📋 Development Commands

### `import_users.py`
- **⚠️ DANGEROUS**: Deletes all users (except superusers)
- **⚠️ DANGEROUS**: Deletes all timeline events and snapshots
- **⚠️ DANGEROUS**: Clears organizational relationships
- **Use case**: Local development and staging testing

### `import_org_structure.py`
- **⚠️ DANGEROUS**: Can create duplicate users
- **Use case**: Local development and staging testing

### `import_ladders.py`
- **✅ SAFE**: Only creates/updates ladder entities
- **Use case**: Local development and staging testing

### `import_history.py`
- **⚠️ DANGEROUS**: Deletes duplicate timeline events
- **Use case**: Local development and staging testing

## 🚫 NEVER RUN THESE IN PRODUCTION

These commands are moved to this subfolder to prevent accidental execution in production environments.

## 📖 Usage

For development/staging:
```bash
# These commands are in the development subfolder
python manage.py import_users --csv="/path/to/users.csv" --clear-users
python manage.py import_org_structure --csv="/path/to/org.csv"
python manage.py import_ladders --csv="/path/to/ladders.csv"
python manage.py import_history --csv="/path/to/history.csv"
```

For production:
```bash
# Use the production commands in the parent directory
python manage.py import_users_prod --csv="/path/to/users.csv"
python manage.py import_org_structure_prod --csv="/path/to/org.csv"
python manage.py import_ladders_prod --csv="/path/to/ladders.csv"
python manage.py import_history_prod --csv="/path/to/history.csv"
```

## 🔒 Safety Measures

1. **Folder Separation**: Development commands are in a separate folder
2. **Clear Naming**: Production commands have `_prod` suffix
3. **Documentation**: Clear warnings about dangerous operations
4. **Backup**: Production commands include automatic backup
5. **Validation**: Production commands include comprehensive validation

---

**Remember**: Always use the production commands (`_prod.py`) in production environments!
