# SSH Profile

This Ansible role implements security compliance checks for SSH configuration.

## Role Description

This role verifies that SSH root login is disabled in `/etc/ssh/sshd_config`, which is a security best practice. It checks that either:
- The `PermitRootLogin` setting is not set to 'yes' in `/etc/ssh/sshd_config`
- OR the openssh-server package is not installed

## Security Metadata

- **Security Group**: SRG-OS-000112
- **Vulnerability ID**: V-38607
- **Rule ID**: SV-50408r1_rule
- **Severity**: CAT I (Critical)
- **STIG ID**: RHEL-08-000227
- **CCI**: CCI-000774
- **Impact level**: 1.0 (High)

## Role Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ssh_profile_fail_on_check` | `true` | Whether to fail when security checks don't pass |
| `ssh_profile_run_checks` | `true` | Whether to run SSH security checks |

## Example Playbook

```yaml
- hosts: servers
  roles:
    - role: ssh_profile
```

## License

Apache-2.0