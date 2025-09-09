Single-database configuration for Flask.

## Basic Migration Commands

### Initial Setup
```bash
# Initialize migrations (only run once)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations to database
flask db upgrade
```

### Common Migration Commands
```bash
# Create a new migration after model changes
flask db migrate -m "Description of changes"

# Apply pending migrations
flask db upgrade

# Downgrade to previous migration
flask db downgrade

# Show current migration revision
flask db current

# Show migration history
flask db history

# Show pending migrations
flask db show
```

### Migration Best Practices
- Always review generated migration files before applying
- Test migrations on a copy of production data
- Create descriptive migration messages
- Backup database before applying migrations in production
