---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper boolean syntax, and fix handler naming inconsistencies.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols and enable only TLSv1.2
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Connects to hosts as root user with privilege escalation
   - Updates Apache SSL configuration to mitigate POODLE vulnerability by restricting protocols to TLSv1.2 only
   - Notifies handlers to restart Apache and SSH services
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean syntax |
| Handler name mismatch | Fix handler name consistency | poodle_fix.yml | Handler "Restart apache2" referenced but defined as "Restart apache" |
| Missing `mode` parameter | Add `mode` parameter | poodle_fix.yml | File operations should specify mode for security |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in this role.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in this playbook that require argument specifications

## Checks for the Migration

**Files to verify**: 
- poodle_fix.yml (modernized)
- meta/main.yml (to be created)
- meta/argument_specs.yml (to be created)

**Services to check**: 
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache configuration syntax: `apache2ctl configtest`
- Check SSL/TLS configuration: `nmap --script ssl-enum-ciphers -p 443 localhost`
- Verify SSH configuration: `sshd -t`
- Test SSL connection: `openssl s_client -connect localhost:443 -tls1_2`
- Verify no SSLv3 support: `openssl s_client -connect localhost:443 -ssl3` (should fail)

## Modernized Playbook

Here's how the modernized playbook should look:

```yaml
---
- hosts: myhost 
  remote_user: root
  become: true
  tasks: 
    - name: Fix SSL in Apache 
      ansible.builtin.replace:
        dest: /etc/apache2/mods-available/ssl.conf 
        regexp: '^SSLProtocol.*$' 
        replace: 'SSLProtocol -all +TLSv1.2'
        mode: '0644'
      notify: 
        - Restart apache
        - Restart sshd
  handlers:
    - name: Restart apache
      ansible.builtin.service:
        name: apache2
        state: restarted

    - name: Restart sshd
      ansible.builtin.service:
        name: sshd
        state: restarted
```

Note: This is a playbook rather than a full role structure. To convert to a proper role, it would need to be restructured with tasks/, handlers/, meta/ directories following Ansible role conventions.