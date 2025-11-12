# PostgreSQL Password Reset Guide (Windows)

This guide explains how to reset your PostgreSQL `postgres` user password on Windows using Command Prompt.

## Prerequisites

- Administrator access to your Windows machine
- PostgreSQL installed (this guide uses PostgreSQL 17)

## Steps to Reset Password

### Step 1: Modify Authentication Settings

1. **Locate the `pg_hba.conf` file**:
   ```
   C:\Program Files\PostgreSQL\17\data\pg_hba.conf
   ```

2. **Open it with a text editor as Administrator**:
   - Right-click Notepad → Run as Administrator
   - Open the `pg_hba.conf` file

3. **Find lines that look like this**:
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   host    all             all             ::1/128                 scram-sha-256
   ```

4. **Temporarily change `scram-sha-256` to `trust`**:
   ```
   host    all             all             127.0.0.1/32            trust
   host    all             all             ::1/128                 trust
   ```

5. **Save the file**

### Step 2: Restart PostgreSQL Service

Open Command Prompt **as Administrator** and run:

```cmd
net stop postgresql-x64-17
net start postgresql-x64-17
```

> **Note**: Adjust the service name if your PostgreSQL version differs. You can check the exact service name in Services (services.msc).

### Step 3: Reset the Password

Navigate to the PostgreSQL bin directory and connect without a password:

```cmd
cd C:\Program Files\PostgreSQL\17\bin
psql -U postgres
```

Once connected, reset the password:

```sql
ALTER USER postgres WITH PASSWORD 'your_new_password';
\q
```

### Step 4: Restore Security Settings

1. **Reopen `pg_hba.conf` as Administrator**
2. **Change `trust` back to `scram-sha-256`**:
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   host    all             all             ::1/128                 scram-sha-256
   ```
3. **Save the file**

### Step 5: Restart PostgreSQL Again

```cmd
net stop postgresql-x64-17
net start postgresql-x64-17
```

## Verify the New Password

Test your new password by connecting:

```cmd
cd C:\Program Files\PostgreSQL\17\bin
psql -U postgres
```

Enter your new password when prompted.

## Important Security Notes

⚠️ **Warning**: Always change the authentication method back from `trust` to `scram-sha-256` after resetting the password. The `trust` method allows anyone to connect to your database without a password!

## Troubleshooting

- **Service won't stop/start**: Make sure you're running Command Prompt as Administrator
- **Can't find pg_hba.conf**: Check your PostgreSQL installation directory, it may differ from the default
- **Changes not taking effect**: Ensure you've restarted the PostgreSQL service after each configuration change

## Alternative Versions

If you're using a different PostgreSQL version, replace `17` with your version number in the paths and service names:

- PostgreSQL 16: `C:\Program Files\PostgreSQL\16\...` and `postgresql-x64-16`
- PostgreSQL 15: `C:\Program Files\PostgreSQL\15\...` and `postgresql-x64-15`

---

**Last Updated**: November 2025  
**PostgreSQL Version**: 17 (adaptable to other versions)
