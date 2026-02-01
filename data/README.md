# Data Files

These files provide fallback data when Faker is not installed.

The data is intentionally minimal - for richer, localized data, install Faker:

```bash
pip install faker
```

## Files

- `names.txt` - First and last names (if needed for custom expansion)
- `locations.txt` - Cities and regions
- `occupations.txt` - Job titles
- `interests.txt` - Hobbies and interests

## Note

Most data is embedded directly in `lib/identity.py` for zero-dependency operation.
These files exist for potential user customization.

```
=^.^=
```
