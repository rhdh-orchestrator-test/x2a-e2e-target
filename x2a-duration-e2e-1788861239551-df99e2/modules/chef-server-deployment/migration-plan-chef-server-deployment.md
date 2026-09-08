---
source-path: setup-automate
---

Based on my analysis, I can see that:

1. The `setup-automate` directory contains shell scripts for deploying Chef Automate and Chef Infra Server, not an existing Ansible role
2. The `chef-and-ansible` directory contains some legacy Ansible playbooks that need modernization
3. There is no existing "chef-server-deployment" Ansible role to migrate

However, I can provide a migration plan that converts the shell script functionality into a modern Ansible role, and also address the modernization needs of the existing Ansible playbooks. Let me create a comprehensive migration plan:

# Migration Plan: Chef Server Deployment

**TLDR**: This migration converts shell-based Chef Automate and Chef Infra Server deployment scripts into a modern Ansible role following current best practices. The existing shell scripts perform system configuration, software installation, and user/organization setup for Chef infrastructure. Key modernization needs include converting shell commands to idempotent Ansible tasks, implementing proper error handling, and using FQCN module names.

## Service Type and Configuration

**Service Type**: Infrastructure Management / Configuration Management Server

**Key Operations**:
- System hostname configuration
- Kernel parameter tuning (vm.max_map_count, vm.dirty_expire_centisecs)
- Chef Automate CLI download and installation
- Chef Automate deployment (with or without Infra Server)
- Chef Server user creation and management
- Chef Server organization creation and management
- SSL certificate and key file generation

## File Structure

**Current Shell Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Proposed Modern Ansible Role Structure:**
```
roles/chef_server_deployment/tasks/main.yml
roles/chef_server_deployment/tasks/system_setup.yml
roles/chef_server_deployment/tasks/install_automate.yml
roles/chef_server_deployment/tasks/configure_users.yml
roles/chef_server_deployment/handlers/main.yml
roles/chef_server_deployment/defaults/main.yml
roles/chef_server_deployment/vars/main.yml
roles/chef_server_deployment/meta/main.yml
roles/chef_server_deployment/meta/argument_specs.yml
roles/chef_server_deployment/templates/chef-automate-config.toml.j2
roles/chef_server_deployment/files/chef-automate-cli-checksum.txt
```

**Additional Legacy Ansible Files Requiring Modernization:**
```
chef-and-ansible/poodle_fix.yml
chef-and-ansible/website_https.yml
```

## Module Explanation

The role performs operations in this order:

1. **system_setup.yml** (`roles/chef_server_deployment/tasks/system_setup.yml`):
   - Set system hostname using `ansible.builtin.hostname` module
   - Configure kernel parameters using `ansible.posix.sysctl` module
   - Legacy pattern: `sudo hostnamectl set-hostname` → Modern: `ansible.builtin.hostname`
   - Legacy pattern: `sudo sysctl -w` → Modern: `ansible.posix.sysctl` with persistent configuration

2. **install_automate.yml** (`roles/chef_server_deployment/tasks/install_automate.yml`):
   - Download Chef Automate CLI using `ansible.builtin.get_url` with checksum validation
   - Set executable permissions using `ansible.builtin.file`
   - Deploy Chef Automate using `ansible.builtin.command` with proper `changed_when` conditions
   - Legacy pattern: `curl | gunzip` → Modern: `ansible.builtin.get_url` + `ansible.builtin.unarchive`
   - Legacy pattern: `chmod +x` → Modern: `ansible.builtin.file` with `mode: '0755'`

3. **configure_users.yml** (`roles/chef_server_deployment/tasks/configure_users.yml`):
   - Create Chef Server users using `ansible.builtin.command` with idempotency checks
   - Create Chef Server organizations using `ansible.builtin.command` with idempotency checks
   - Manage PEM files with proper ownership and permissions
   - Legacy pattern: Direct `chef-server-ctl` commands → Modern: Wrapped with `changed_when` and `creates` parameters

## Modernization Mapping

| Legacy Pattern | Modern Equivalent | Files Affected | Notes |
|---|---|---|---|
| `sudo hostnamectl set-hostname` | `ansible.builtin.hostname:` | system_setup.yml | Idempotent hostname setting |
| `sudo sysctl -w` | `ansible.posix.sysctl:` | system_setup.yml | Persistent kernel parameters |
| `curl \| gunzip` | `ansible.builtin.get_url:` + `ansible.builtin.unarchive:` | install_automate.yml | Secure download with checksum |
| `chmod +x` | `ansible.builtin.file: mode: '0755'` | install_automate.yml | Proper file permissions |
| `./chef-automate deploy` | `ansible.builtin.command:` with `creates:` | install_automate.yml | Idempotent deployment |
| `chef-server-ctl user-create` | `ansible.builtin.command:` with `creates:` | configure_users.yml | Idempotent user creation |
| `chef-server-ctl org-create` | `ansible.builtin.command:` with `creates:` | configure_users.yml | Idempotent org creation |
| `replace:` | `ansible.builtin.replace:` | poodle_fix.yml | FQCN |
| `apt:` | `ansible.builtin.apt:` | website_https.yml | FQCN |
| `file:` | `ansible.builtin.file:` | website_https.yml | FQCN |
| `copy:` | `ansible.builtin.copy:` | website_https.yml | FQCN |
| `command:` | `ansible.builtin.command:` | website_https.yml | FQCN + changed_when |
| `update_cache=true` | `update_cache: true` | website_https.yml | Boolean modernization |
| `mode: 0640` | `mode: '0640'` | website_https.yml | Quoted octal permissions |

## Dependencies

**Collection dependencies** (for requirements.yml):
- ansible.posix: ">=1.0.0"
- community.crypto: ">=2.0.0"
- ansible.builtin: (core collection)

**Role dependencies**: None
**External packages**: 
- chef-automate-cli (downloaded during role execution)
- curl (system dependency)
- gunzip (system dependency)

**Services managed**: 
- chef-automate
- chef-server

## Template Modernization

- **chef-automate-config.toml.j2**: Configuration template for Chef Automate deployment settings
  - Use `ansible_facts['hostname']` instead of `ansible_hostname`
  - Implement proper variable validation with `| default()` filters

## Argument Specification

Variables for meta/argument_specs.yml:
- `chef_hostname`: string, required, "Hostname for Chef Automate server"
- `chef_username`: string, required, "Chef server admin username"
- `chef_user_fullname`: string, required, "Full name for Chef admin user"
- `chef_user_email`: string, required, "Email for Chef admin user"
- `chef_user_password`: string, required, no_log: true, "Password for Chef admin user"
- `chef_org_name`: string, required, "Chef organization short name"
- `chef_org_fullname`: string, required, "Chef organization full name"
- `chef_products`: list, default: ['automate', 'infra-server'], "Chef products to deploy"
- `chef_accept_license`: boolean, default: false, "Accept Chef license terms"

## Checks for the Migration

**Files to verify**: 
- roles/chef_server_deployment/tasks/main.yml
- roles/chef_server_deployment/tasks/system_setup.yml
- roles/chef_server_deployment/tasks/install_automate.yml
- roles/chef_server_deployment/tasks/configure_users.yml
- roles/chef_server_deployment/handlers/main.yml
- roles/chef_server_deployment/defaults/main.yml
- roles/chef_server_deployment/meta/argument_specs.yml
- Modernized versions of poodle_fix.yml and website_https.yml

**Services to check**: 
- chef-automate service status
- chef-server service status

**Templates to validate**: 
- chef-automate-config.toml.j2 syntax validation

## Pre-flight checks:
```bash
# Verify Chef Automate is running
sudo chef-automate status

# Verify Chef Server is accessible
sudo chef-server-ctl status

# Test user authentication
knife ssl check -s https://{{ chef_hostname }}

# Verify organization exists
knife client list -s https://{{ chef_hostname }}

# Check system requirements
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Validate hostname resolution
nslookup {{ chef_hostname }}
```

**Critical Migration Notes:**
1. The shell scripts lack idempotency - the Ansible role must implement proper `changed_when` conditions
2. Error handling is minimal in shell scripts - implement `block`/`rescue`/`always` patterns
3. Secrets management: Use Ansible Vault for passwords and sensitive data
4. The role should support both deployment scenarios (Automate only vs. Automate + Infra Server)
5. Implement proper backup procedures for existing Chef installations
6. Add validation tasks to verify successful deployment before proceeding with user/org creation