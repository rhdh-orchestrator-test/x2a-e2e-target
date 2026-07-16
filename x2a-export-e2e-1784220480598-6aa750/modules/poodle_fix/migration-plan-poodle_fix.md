---
source-path: chef-and-ansible/poodle_fix.yml
---

Now I'll create a detailed migration plan based on the file content:

# Migration Plan: poodle_fix

**TLDR**: This role applies a security fix for the POODLE vulnerability by updating SSL configuration in Apache to disable vulnerable protocols and enable only TLSv1.2. The role needs modernization to use fully qualified collection names (FQCN), proper handler names, and structured playbook organization.

## Service Type and Configuration

**Service Type**: Security Hardening

**Key Operations**:
- Modifies Apache SSL configuration to disable vulnerable SSL protocols
- Enables only TLSv1.2 for secure connections
- Restarts Apache and SSH services after configuration changes

## File Structure

**IMPORTANT: List files using RELATIVE PATHS (relative to the role root), one per line. DO NOT use tree structure format.**

poodle_fix.yml

## Module Explanation

The role performs operations in this order:

1. **poodle_fix.yml**:
   - Targets hosts in the "myhost" group with root privileges
   - Modifies Apache SSL configuration to mitigate the POODLE vulnerability by restricting protocols to TLSv1.2
   - Uses the `replace` module to update the SSL configuration file
   - Notifies handlers to restart Apache and SSH services after changes
   - Ansible module mapping: `replace` → `ansible.builtin.replace`

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `become: yes` | `become: true` | poodle_fix.yml | Boolean modernization |
| Handler name mismatch | Match handler names with notifications | poodle_fix.yml | Handler "Restart apache2" notified but handler defined as "Restart apache" |
| Playbook structure | Convert to role structure | poodle_fix.yml | Convert from standalone playbook to proper role structure |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.builtin: latest

**Role dependencies**: None
**External packages**: None (assumes Apache and SSH are already installed)
**Services managed**: apache2, sshd

## Template Modernization

No templates present in the current implementation.

## Argument Specification

For meta/argument_specs.yml:
- No variables defined in the current implementation, but could add:
  - `ssl_protocol_string`: string, default: '-all +TLSv1.2', description: "SSL protocols to enable/disable"
  - `apache_ssl_conf_path`: string, default: '/etc/apache2/mods-available/ssl.conf', description: "Path to Apache SSL configuration file"

## Checks for the Migration

**Files to verify**:
- tasks/main.yml
- handlers/main.yml
- meta/main.yml
- meta/argument_specs.yml
- defaults/main.yml

**Services to check**:
- apache2
- sshd

**Templates to validate**: None

## Pre-flight checks:
- Verify Apache is installed: `systemctl status apache2`
- Verify SSH is installed: `systemctl status sshd`
- Validate Apache configuration after changes: `apache2ctl configtest`
- Check SSL configuration: `grep SSLProtocol /etc/apache2/mods-available/ssl.conf`
- Verify TLS version with: `nmap --script ssl-enum-ciphers -p 443 localhost`

## Migration Implementation Details

### Converting from Playbook to Role Structure

1. **Create role directory structure**:
```
poodle_fix/
├── defaults/
│   └── main.yml
├── handlers/
│   └── main.yml
├── meta/
│   └── main.yml
├── tasks/
│   └── main.yml
└── README.md
```

2. **tasks/main.yml**:
```yaml
---
- name: Fix SSL in Apache
  ansible.builtin.replace:
    dest: "{{ apache_ssl_conf_path }}"
    regexp: '^SSLProtocol.*$'
    replace: "SSLProtocol {{ ssl_protocol_string }}"
  notify:
    - Restart apache2
    - Restart sshd
```

3. **handlers/main.yml**:
```yaml
---
- name: Restart apache2
  ansible.builtin.service:
    name: apache2
    state: restarted

- name: Restart sshd
  ansible.builtin.service:
    name: sshd
    state: restarted
```

4. **defaults/main.yml**:
```yaml
---
apache_ssl_conf_path: /etc/apache2/mods-available/ssl.conf
ssl_protocol_string: "-all +TLSv1.2"
```

5. **meta/main.yml**:
```yaml
---
galaxy_info:
  author: Your Name
  description: Role to fix POODLE vulnerability in Apache
  company: Your Company
  license: MIT
  min_ansible_version: 2.9
  platforms:
    - name: Debian
      versions:
        - all
    - name: Ubuntu
      versions:
        - all
  galaxy_tags:
    - security
    - apache
    - ssl
    - poodle

dependencies: []
```

6. **meta/argument_specs.yml**:
```yaml
---
argument_specs:
  main:
    short_description: Role to fix POODLE vulnerability in Apache
    description: Configures Apache SSL settings to mitigate the POODLE vulnerability
    options:
      apache_ssl_conf_path:
        type: str
        default: /etc/apache2/mods-available/ssl.conf
        description: Path to Apache SSL configuration file
      ssl_protocol_string:
        type: str
        default: "-all +TLSv1.2"
        description: SSL protocols to enable/disable
```