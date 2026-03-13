# Migration Plan: ssh_profile

**TLDR**: This is an InSpec security profile for SSH configuration that checks if SSH root login is disabled. It's a single control that verifies the SSH configuration complies with security standards.

## Service Type and Instances

**Service Type**: Security Compliance Profile (InSpec)

**Configured Instances**:
- This is not a Chef cookbook that configures a service, but rather an InSpec security profile that tests SSH configuration.
- The profile contains a single control that verifies SSH root login is disabled in `/etc/ssh/sshd_config`.

## File Structure

```
chef-and-ansible/tests/ssh_profile.rb
```

## Module Explanation

This is not a traditional Chef cookbook with recipes, but rather an InSpec security profile with a single control:

1. **ssh_profile.rb** (`chef-and-ansible/tests/ssh_profile.rb`):
   - Defines a security control "Ensure_SSH_root_login_is_disabled"
   - Verifies that SSH root login is disabled in `/etc/ssh/sshd_config`
   - Checks that either:
     - The `PermitRootLogin` setting is not set to 'yes' in `/etc/ssh/sshd_config`
     - OR the openssh-server package is not installed
   - Includes security metadata:
     - Security Group: 'SRG-OS-000112'
     - Vulnerability ID: 'V-38607'
     - Rule ID: 'SV-50408r1_rule'
     - Severity: 'CAT I' (Critical)
     - STIG ID: 'RHEL-08-000227'
     - CCI: 'CCI-000774'
   - Impact level: 1.0 (High)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: None (checks for openssh-server)
**Service dependencies**: None

## Checks for the Migration

**Files to verify**:
- `/etc/ssh/sshd_config` - SSH daemon configuration file

**Service endpoints to check**: None

**Templates rendered**: None

## Pre-flight checks:
```bash
# Check SSH configuration
grep PermitRootLogin /etc/ssh/sshd_config

# Verify SSH package status
rpm -q openssh-server || echo "openssh-server not installed"

# Test SSH root login (should fail)
ssh root@localhost
# Expected result: Permission denied or authentication failure

# Check SSH daemon status if installed
systemctl status sshd || echo "SSH daemon not running"

# Verify SSH daemon is properly configured
sshd -T | grep permitrootlogin
```