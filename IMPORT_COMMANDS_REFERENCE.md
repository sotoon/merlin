# Import Commands Reference

## 🚨 IMPORTANT: Command Safety

### **Production Commands** (SAFE - Use in Production)
- Located in: `api/management/commands/`
- **NEVER DELETE** existing data
- Include backup, rollback, validation, and detailed logging
- Safe to run multiple times

### **Development Commands** (DANGEROUS - Development Only)
- Located in: `api/management/commands/development/`
- **CAN DELETE** existing data
- For local development and staging testing only
- **NEVER USE IN PRODUCTION**

---

## 🏭 PRODUCTION COMMANDS

### 1. User Import (Production-Safe)
```bash
# Basic user import with backup and validation
python manage.py import_users_prod --csv="/path/to/users.csv"

# With detailed logging
python manage.py import_users_prod --csv="/path/to/users.csv" --log-file="/var/log/merlin/users.log"

# Force update existing relationships
python manage.py import_users_prod --csv="/path/to/users.csv" --force-update

# Dry run (test without changes)
python manage.py import_users_prod --csv="/path/to/users.csv" --dry-run

# Full production command with all safety features
python manage.py import_users_prod \
  --csv="/path/to/users.csv" \
  --log-file="/var/log/merlin/users.log" \
  --backup \
  --force-update \
  --validate
```

### 2. Organizational Structure Import (Production-Safe)
```bash
# Import organizations
python manage.py import_org_structure_prod --csv="/path/to/organizations.csv"

# Import chapters with user creation
python manage.py import_org_structure_prod --csv="/path/to/chapters.csv" --create-users

# Import tribes with force update
python manage.py import_org_structure_prod --csv="/path/to/tribes.csv" --force-update

# Import teams with detailed logging
python manage.py import_org_structure_prod --csv="/path/to/teams.csv" --log-file="/var/log/merlin/teams.log"

# Full production command
python manage.py import_org_structure_prod \
  --csv="/path/to/teams.csv" \
  --log-file="/var/log/merlin/teams.log" \
  --backup \
  --create-users \
  --force-update \
  --validate
```

### 3. Ladders Import (Production-Safe)
```bash
# Import all ladder entities
python manage.py import_ladders_prod --csv="/path/to/ladders.csv"

# Import only ladders
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --ladders-only

# Import only aspects
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --aspects-only

# Import only levels
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --levels-only

# Full production command
python manage.py import_ladders_prod \
  --csv="/path/to/ladders.csv" \
  --log-file="/var/log/merlin/ladders.log" \
  --backup \
  --force-update \
  --validate
```

### 4. History Import (Production-Safe)
```bash
# Basic history import
python manage.py import_history_prod --csv="/path/to/history.csv"

# Skip duplicates (default behavior)
python manage.py import_history_prod --csv="/path/to/history.csv" --skip-duplicates

# Update existing events
python manage.py import_history_prod --csv="/path/to/history.csv" --update-existing

# With detailed logging
python manage.py import_history_prod --csv="/path/to/history.csv" --log-file="/var/log/merlin/history.log"

# Full production command
python manage.py import_history_prod \
  --csv="/path/to/history.csv" \
  --log-file="/var/log/merlin/history.log" \
  --backup \
  --skip-duplicates \
  --validate
```

---

## 🧪 DEVELOPMENT COMMANDS

### ⚠️ WARNING: These commands can DELETE data!

### 1. User Import (Development - DANGEROUS)
```bash
# Clear all users and import new ones (DANGEROUS!)
python manage.py import_users --csv="/path/to/users.csv" --clear-users

# Import users without clearing (safer)
python manage.py import_users --csv="/path/to/users.csv"

# Dry run (test without changes)
python manage.py import_users --csv="/path/to/users.csv" --dry-run
```

### 2. Organizational Structure Import (Development)
```bash
# Import organizations
python manage.py import_org_structure --csv="/path/to/organizations.csv"

# Import chapters with user creation
python manage.py import_org_structure --csv="/path/to/chapters.csv" --create-users

# Import tribes
python manage.py import_org_structure --csv="/path/to/tribes.csv"

# Import teams
python manage.py import_org_structure --csv="/path/to/teams.csv"
```

### 3. Ladders Import (Development)
```bash
# Import all ladder entities
python manage.py import_ladders --csv="/path/to/ladders.csv"

# Import only ladders
python manage.py import_ladders --csv="/path/to/ladders.csv" --ladders-only

# Import only aspects
python manage.py import_ladders --csv="/path/to/ladders.csv" --aspects-only

# Import only levels
python manage.py import_ladders --csv="/path/to/ladders.csv" --levels-only
```

### 4. History Import (Development - DANGEROUS)
```bash
# Import history (may delete duplicate events)
python manage.py import_history --csv="/path/to/history.csv"

# Dry run (test without changes)
python manage.py import_history --csv="/path/to/history.csv" --dry-run
```

---

## 🚀 PRODUCTION DEPLOYMENT WORKFLOW

### Step 1: Pre-Deployment Testing
```bash
# Test all commands with dry-run first
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --dry-run
python manage.py import_org_structure_prod --csv="/path/to/org.csv" --dry-run
python manage.py import_users_prod --csv="/path/to/users.csv" --dry-run
python manage.py import_history_prod --csv="/path/to/history.csv" --dry-run
```

### Step 2: Production Import Order
```bash
# 1. Import ladders first (foundation)
python manage.py import_ladders_prod \
  --csv="/path/to/ladders.csv" \
  --log-file="/var/log/merlin/ladders.log" \
  --backup \
  --validate

# 2. Import organizational structure
python manage.py import_org_structure_prod \
  --csv="/path/to/organizations.csv" \
  --log-file="/var/log/merlin/org.log" \
  --backup \
  --validate

python manage.py import_org_structure_prod \
  --csv="/path/to/chapters.csv" \
  --log-file="/var/log/merlin/chapters.log" \
  --backup \
  --create-users \
  --validate

python manage.py import_org_structure_prod \
  --csv="/path/to/tribes.csv" \
  --log-file="/var/log/merlin/tribes.log" \
  --backup \
  --create-users \
  --validate

python manage.py import_org_structure_prod \
  --csv="/path/to/teams.csv" \
  --log-file="/var/log/merlin/teams.log" \
  --backup \
  --create-users \
  --validate

# 3. Import users
python manage.py import_users_prod \
  --csv="/path/to/users.csv" \
  --log-file="/var/log/merlin/users.log" \
  --backup \
  --force-update \
  --validate

# 4. Import historical data
python manage.py import_history_prod \
  --csv="/path/to/history.csv" \
  --log-file="/var/log/merlin/history.log" \
  --backup \
  --skip-duplicates \
  --validate
```

### Step 3: Post-Import Validation
```bash
# Check import results
python manage.py shell -c "
from api.models import User, Team, Tribe, Chapter, TimelineEvent
print(f'Users: {User.objects.count()}')
print(f'Teams: {Team.objects.count()}')
print(f'Tribes: {Tribe.objects.count()}')
print(f'Chapters: {Chapter.objects.count()}')
print(f'Timeline Events: {TimelineEvent.objects.count()}')
"
```

---

## 🧪 DEVELOPMENT/STAGING WORKFLOW

### For Local Development
```bash
# Clear and import everything (DANGEROUS - Development only!)
python manage.py import_users --csv="/path/to/users.csv" --clear-users
python manage.py import_org_structure --csv="/path/to/org.csv"
python manage.py import_ladders --csv="/path/to/ladders.csv"
python manage.py import_history --csv="/path/to/history.csv"
```

### For Staging Testing
```bash
# Test with production commands (safer)
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --dry-run
python manage.py import_org_structure_prod --csv="/path/to/org.csv" --dry-run
python manage.py import_users_prod --csv="/path/to/users.csv" --dry-run
python manage.py import_history_prod --csv="/path/to/history.csv" --dry-run
```

---

## 📋 Command Arguments Reference

### Production Commands Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--csv` | Path to CSV file | Required |
| `--log-file` | Path to detailed log file | None |
| `--backup` | Create backup before import | True |
| `--validate` | Validate data after import | True |
| `--dry-run` | Test run without changes | False |
| `--force-update` | Force update existing relationships | False |
| `--create-users` | Create users if referenced by email | False |
| `--skip-duplicates` | Skip duplicate events | True |
| `--update-existing` | Update existing events | False |

### Development Commands Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--csv` | Path to CSV file | Required |
| `--clear-users` | Clear existing users (DANGEROUS!) | False |
| `--create-users` | Create users if referenced by email | False |
| `--dry-run` | Test run without changes | False |
| `--ladders-only` | Import only ladders section | False |
| `--aspects-only` | Import only aspects section | False |
| `--levels-only` | Import only levels section | False |

---

## 🚨 SAFETY CHECKLIST

### Before Running in Production:
- [ ] Use `_prod.py` commands only
- [ ] Test with `--dry-run` first
- [ ] Enable logging with `--log-file`
- [ ] Ensure backup is enabled
- [ ] Verify CSV data quality
- [ ] Check disk space for backups
- [ ] Plan rollback procedure

### Before Running in Development:
- [ ] Understand that development commands can DELETE data
- [ ] Use `--clear-users` only when you want to delete all users
- [ ] Test with `--dry-run` first
- [ ] Backup your development database if needed

---

## 📞 Emergency Procedures

### If Production Import Fails:
1. Check the log files for errors
2. Use the backup to rollback if needed
3. Contact the development team
4. Review the validation results

### If Development Import Goes Wrong:
1. Restore from your development backup
2. Use the development commands to clear and re-import
3. Check the Django admin for data integrity

---

**Remember**: 
- **Production**: Always use `_prod.py` commands
- **Development**: Be careful with commands that can delete data
- **Testing**: Always use `--dry-run` first
- **Backup**: Keep backups of important data
