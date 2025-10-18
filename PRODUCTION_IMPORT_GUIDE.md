# Production Import Commands Guide

## 🛡️ Production-Safe Import Commands

This guide covers the production-safe import commands that **NEVER DELETE** existing data and include comprehensive safety features.

## ⚠️ IMPORTANT: Command Organization

### **Development Commands** (DO NOT USE IN PRODUCTION)
Located in: `api/management/commands/development/`
- `import_users.py` - **DELETES DATA** - Development only
- `import_org_structure.py` - Development only  
- `import_ladders.py` - Development only
- `import_history.py` - Development only

### **Production Commands** (SAFE FOR PRODUCTION)
Located in: `api/management/commands/`
- `import_users_prod.py` - **PRODUCTION SAFE** - Never deletes data
- `import_org_structure_prod.py` - **PRODUCTION SAFE** - Never deletes data
- `import_ladders_prod.py` - **PRODUCTION SAFE** - Never deletes data
- `import_history_prod.py` - **PRODUCTION SAFE** - Never deletes data

**🚨 NEVER run development commands in production! Always use the `_prod.py` commands.**

## 📋 Available Production Commands

### 1. `import_users_prod.py` - Production-Safe User Import
**Purpose**: Import users and their organizational relationships safely.

**Key Features**:
- ✅ **NO DELETION**: Never deletes existing users or data
- ✅ **Backup**: Creates database backup before import
- ✅ **Rollback**: Can restore from backup if needed
- ✅ **Validation**: Validates data integrity after import
- ✅ **Logging**: Detailed logging of all operations

**Usage**:
```bash
# Basic import with backup and validation
python manage.py import_users_prod --csv="/path/to/users.csv"

# With detailed logging
python manage.py import_users_prod --csv="/path/to/users.csv" --log-file="/path/to/import.log"

# Force update existing relationships
python manage.py import_users_prod --csv="/path/to/users.csv" --force-update

# Dry run (test without changes)
python manage.py import_users_prod --csv="/path/to/users.csv" --dry-run
```

**Arguments**:
- `--csv`: Path to users CSV file (required)
- `--log-file`: Path to detailed log file
- `--backup`: Create backup before import (default: True)
- `--force-update`: Force update existing user relationships
- `--validate`: Validate data after import (default: True)
- `--dry-run`: Test run without making changes

### 2. `import_org_structure_prod.py` - Production-Safe Organizational Structure Import
**Purpose**: Import organizational entities (organizations, chapters, tribes, teams) safely.

**Key Features**:
- ✅ **NO DELETION**: Never deletes existing organizational entities
- ✅ **Smart Detection**: Auto-detects file type (organizations, chapters, tribes, teams)
- ✅ **User Creation**: Optional user creation when referenced by email
- ✅ **Backup & Validation**: Full safety features

**Usage**:
```bash
# Import organizations
python manage.py import_org_structure_prod --csv="/path/to/organizations.csv"

# Import chapters with user creation
python manage.py import_org_structure_prod --csv="/path/to/chapters.csv" --create-users

# Import teams with force update
python manage.py import_org_structure_prod --csv="/path/to/teams.csv" --force-update

# Import tribes with detailed logging
python manage.py import_org_structure_prod --csv="/path/to/tribes.csv" --log-file="/path/to/org.log"
```

**Arguments**:
- `--csv`: Path to CSV file (required)
- `--create-users`: Create users if they don't exist when referenced
- `--force-update`: Force update existing organizational relationships
- `--log-file`: Path to detailed log file
- `--backup`: Create backup before import (default: True)
- `--validate`: Validate data after import (default: True)
- `--dry-run`: Test run without making changes

### 3. `import_ladders_prod.py` - Production-Safe Ladders Import
**Purpose**: Import ladder entities (ladders, aspects, levels) safely.

**Key Features**:
- ✅ **NO DELETION**: Never deletes existing ladder entities
- ✅ **Smart Detection**: Auto-detects row type (ladder, aspect, level)
- ✅ **Selective Import**: Import only specific sections
- ✅ **Backup & Validation**: Full safety features

**Usage**:
```bash
# Import all ladder entities
python manage.py import_ladders_prod --csv="/path/to/ladders.csv"

# Import only ladders
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --ladders-only

# Import only aspects
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --aspects-only

# Import only levels
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --levels-only

# With force update and logging
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --force-update --log-file="/path/to/ladders.log"
```

**Arguments**:
- `--csv`: Path to CSV file (required)
- `--ladders-only`: Import only ladders section
- `--aspects-only`: Import only aspects section
- `--levels-only`: Import only levels section
- `--force-update`: Force update existing ladder entities
- `--log-file`: Path to detailed log file
- `--backup`: Create backup before import (default: True)
- `--validate`: Validate data after import (default: True)
- `--dry-run`: Test run without making changes

### 4. `import_history_prod.py` - Production-Safe History Import
**Purpose**: Import historical events and snapshots safely.

**Key Features**:
- ✅ **NO DELETION**: Never deletes existing timeline events
- ✅ **Duplicate Handling**: Smart handling of duplicate events
- ✅ **Rich Summaries**: Enhanced event descriptions with pay band details
- ✅ **Backup & Validation**: Full safety features

**Usage**:
```bash
# Basic history import
python manage.py import_history_prod --csv="/path/to/history.csv"

# Skip duplicates (default behavior)
python manage.py import_history_prod --csv="/path/to/history.csv" --skip-duplicates

# Update existing events
python manage.py import_history_prod --csv="/path/to/history.csv" --update-existing

# With detailed logging
python manage.py import_history_prod --csv="/path/to/history.csv" --log-file="/path/to/history.log"
```

**Arguments**:
- `--csv`: Path to history CSV file (required)
- `--skip-duplicates`: Skip duplicate events instead of updating (default: True)
- `--update-existing`: Update existing events with new data
- `--log-file`: Path to detailed log file
- `--backup`: Create backup before import (default: True)
- `--validate`: Validate data after import (default: True)
- `--dry-run`: Test run without making changes

## 🔧 Production Safety Features

### 1. **Backup System**
- **Automatic Backup**: Creates database backup before each import
- **Backup Location**: `/tmp/merlin_backups/` (configurable via `PRODUCTION_BACKUP_DIR` setting)
- **Backup Contents**: All relevant database tables exported to JSON
- **Backup ID**: Unique timestamp-based backup identifier

### 2. **Rollback Capability**
- **Automatic Rollback**: Can restore from backup if import fails
- **Manual Rollback**: Use backup files to restore previous state
- **Rollback Logging**: Detailed logging of rollback operations

### 3. **Data Validation**
- **Pre-Import Validation**: Validates CSV data quality
- **Post-Import Validation**: Verifies imported data integrity
- **Relationship Validation**: Ensures all foreign keys are valid
- **Data Consistency Checks**: Validates business logic constraints

### 4. **Detailed Logging**
- **Operation Logging**: Logs every operation performed
- **Error Tracking**: Detailed error logging with context
- **Performance Metrics**: Tracks import performance
- **Audit Trail**: Complete audit trail of all changes

## 📊 Validation Checks

### User Data Validation
- ✅ Users without required fields
- ✅ Duplicate email addresses
- ✅ Orphaned relationships
- ✅ Invalid team references

### Organizational Structure Validation
- ✅ Teams without tribes
- ✅ Invalid leader references
- ✅ Missing departments
- ✅ Orphaned organizational entities

### Ladder Data Validation
- ✅ Ladders without aspects
- ✅ Aspects without ladders
- ✅ Missing ladder relationships
- ✅ Invalid level numbers

### Timeline Events Validation
- ✅ Events without users
- ✅ Snapshots without users
- ✅ Invalid event types
- ✅ Missing relationships

## 🚀 Production Deployment Workflow

### 1. **Pre-Deployment**
```bash
# Test on staging first
python manage.py import_users_prod --csv="/path/to/users.csv" --dry-run
python manage.py import_org_structure_prod --csv="/path/to/org.csv" --dry-run
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --dry-run
python manage.py import_history_prod --csv="/path/to/history.csv" --dry-run
```

### 2. **Production Import Order**
```bash
# 1. Import ladders first (foundation)
python manage.py import_ladders_prod --csv="/path/to/ladders.csv" --log-file="/var/log/merlin/ladders.log"

# 2. Import organizational structure
python manage.py import_org_structure_prod --csv="/path/to/organizations.csv" --log-file="/var/log/merlin/org.log"
python manage.py import_org_structure_prod --csv="/path/to/chapters.csv" --log-file="/var/log/merlin/chapters.log"
python manage.py import_org_structure_prod --csv="/path/to/tribes.csv" --log-file="/var/log/merlin/tribes.log"
python manage.py import_org_structure_prod --csv="/path/to/teams.csv" --log-file="/var/log/merlin/teams.log"

# 3. Import users
python manage.py import_users_prod --csv="/path/to/users.csv" --log-file="/var/log/merlin/users.log"

# 4. Import historical data
python manage.py import_history_prod --csv="/path/to/history.csv" --log-file="/var/log/merlin/history.log"
```

### 3. **Development/Staging Testing**
```bash
# For development and staging testing (DO NOT USE IN PRODUCTION)
python manage.py import_users --csv="/path/to/users.csv" --clear-users
python manage.py import_org_structure --csv="/path/to/org.csv"
python manage.py import_ladders --csv="/path/to/ladders.csv"
python manage.py import_history --csv="/path/to/history.csv"
```

### 4. **Post-Import Validation**
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

## 🛠️ Troubleshooting

### Common Issues

1. **Backup Creation Failed**
   - Check disk space in backup directory
   - Verify write permissions
   - Check database connection

2. **Validation Failed**
   - Review validation logs
   - Check data integrity
   - Verify CSV data quality

3. **Import Errors**
   - Check CSV format and encoding
   - Verify required fields are present
   - Review detailed error logs

### Recovery Procedures

1. **Rollback from Backup**
   ```bash
   # Restore from backup
   python manage.py shell -c "
   from api.management.commands._prod_utils import DatabaseBackup
   backup = DatabaseBackup(None, None)
   backup.restore_backup('/path/to/backup')
   "
   ```

2. **Manual Data Cleanup**
   ```bash
   # Remove imported data if needed
   python manage.py shell -c "
   from api.models import TimelineEvent, CompensationSnapshot, SenioritySnapshot
   TimelineEvent.objects.filter(created_by__isnull=True).delete()
   CompensationSnapshot.objects.filter(source_event__isnull=True).delete()
   SenioritySnapshot.objects.filter(source_event__isnull=True).delete()
   "
   ```

## 📝 Best Practices

### 1. **Always Use Dry Run First**
```bash
python manage.py import_users_prod --csv="/path/to/users.csv" --dry-run
```

### 2. **Enable Detailed Logging**
```bash
python manage.py import_users_prod --csv="/path/to/users.csv" --log-file="/var/log/merlin/import.log"
```

### 3. **Monitor Import Progress**
```bash
# Watch log files
tail -f /var/log/merlin/import.log
```

### 4. **Validate After Each Import**
```bash
# Check data integrity
python manage.py shell -c "
from api.management.commands._prod_utils import DataValidator
validator = DataValidator(None, None)
result = validator.validate_import('all', {})
print(result)
"
```

### 5. **Keep Backups**
- Store backups in secure location
- Keep multiple backup versions
- Test backup restoration regularly

## 🔒 Security Considerations

1. **File Permissions**: Ensure log files have appropriate permissions
2. **Backup Security**: Secure backup files with proper access controls
3. **Log Rotation**: Implement log rotation to prevent disk space issues
4. **Access Control**: Limit access to production import commands

## 📞 Support

For issues or questions:
1. Check the detailed logs first
2. Review validation results
3. Check backup availability
4. Contact the development team with specific error details

---

**Remember**: These production commands are designed to be **100% safe** and **never delete** existing data. Always test on staging first and keep backups!
