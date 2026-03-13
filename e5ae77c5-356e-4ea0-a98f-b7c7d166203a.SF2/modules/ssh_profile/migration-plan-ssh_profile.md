# Migration Plan: ssh_profile

**TLDR**: This is an InSpec security test that verifies SSH root login is disabled on Linux systems. It checks either that the SSH configuration has PermitRootLogin set to anything other than 'yes', or that the OpenSSH server is not installed.

## Service Type and Instances

**Service Type**: Security Compliance Test

**Configured Instances**:
- **SSH daemon configuration**: Security test for SSH daemon configuration
  - Location/Path: /etc/ssh/sshd_config
  - Key Config: PermitRootLogin should not be set to 'yes'

## File Structure

```
chef-and-ansible/tests/ssh_profile.rb
```

## Module Explanation

The InSpec test performs the following operations:

1. **SSH Root Login Test** (`chef-and-ansible/tests/ssh_profile.rb`):
   - Defines a security control "Ensure_SSH_root_login_is_disabled"
   - Checks that either:
     - The SSH configuration file (/etc/ssh/sshd_config) has PermitRootLogin set to something other than 'yes'
     - OR the openssh-server package is not installed
   - Includes security metadata:
     - Security Technical Implementation Guide (STIG) ID: RHEL-08-000227
     - Vulnerability ID: V-38607
     - Rule ID: SV-50408r1_rule
     - Category: CAT I (highest severity)
     - CCI: CCI-000774
   - Resources: sshd_config (1), package (1)

## Dependencies

**External cookbook dependencies**: None (this is an InSpec test, not a Chef cookbook)
**System package dependencies**: None (the test checks for openssh-server but doesn't install it)
**Service dependencies**: None

## Checks for the Migration

**Files to verify**:
- /etc/ssh/sshd_config

**Service endpoints to check**:
- None (this is a compliance test, not a service)

**Templates rendered**:
- None (this is a compliance test, not a configuration management task)

## Pre-flight checks:
```bash
# Check SSH configuration
grep PermitRootLogin /etc/ssh/sshd_config

# Check if openssh-server is installed
rpm -q openssh-server || dpkg -l | grep openssh-server

# Validate the test with InSpec
inspec exec chef-and-ansible/tests/ssh_profile.rb

# Validate the test with Ansible
ansible-playbook -C ssh_security_check.yml
```