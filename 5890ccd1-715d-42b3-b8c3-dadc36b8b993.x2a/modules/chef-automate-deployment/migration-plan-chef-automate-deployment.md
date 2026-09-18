---
source-path: setup-automate/deploy-automate.sh
---

Based on my analysis, I can see that the provided path contains Bash scripts, not PowerShell scripts. The analysis summary also shows "Total files analyzed: 0" which confirms there are no PowerShell files to analyze. However, I can provide a migration plan for the Bash-based Chef Automate deployment to Ansible, treating this as a shell script migration rather than PowerShell.

# Migration Plan: Chef Automate Deployment Scripts

**TLDR**: Bash scripts that deploy Chef Automate and Chef Infra Server on Linux VMs, configuring system parameters, downloading and installing Chef Automate CLI, deploying services, and creating initial users and organizations. This is a Chef infrastructure deployment, not a PowerShell-based Windows service.

## Service Type and Configuration

**Service Type**: Chef Infrastructure Management Platform (Chef Automate + Chef Infra Server)

**Key Operations**:
- Set system hostname
- Configure kernel parameters (vm.max_map_count, vm.dirty_expire_centisecs)
- Download and install Chef Automate CLI
- Deploy Chef Automate and Chef Infra Server products
- Create Chef Server user accounts
- Create Chef Server organizations
- Generate authentication certificates (.pem files)

## File Structure

**Scripts:**
```
setup-automate/deploy-automate.sh
setup-automate/deploy-chef-server.sh
```

**Modules:**
```
None - No PowerShell modules found
```

**DSC Configurations:**
```
None - No DSC configurations found
```

**Data Files:**
```
None - No .psd1 configuration data files found
```

## Module Explanation

**IMPORTANT NOTE**: The provided scripts are Bash scripts, not PowerShell. The analysis shows no PowerShell files were found. Below is the migration plan for the Bash-based Chef deployment:

The scripts perform operations in this order:

1. **deploy-automate.sh** (`setup-automate/deploy-automate.sh`):
   - Step 1: Sets system hostname using hostnamectl
   - Step 2: Configures kernel parameters via sysctl
   - Step 3: Downloads Chef Automate CLI from packages.chef.io
   - Step 4: Deploys both Chef Automate and Chef Infra Server
   - Step 5: Creates Chef Server user with credentials
   - Step 6: Creates Chef Server organization with association
   - Ansible equivalent: ansible.builtin.shell, ansible.builtin.get_url, ansible.builtin.command modules

2. **deploy-chef-server.sh** (`setup-automate/deploy-chef-server.sh`):
   - Step 1: Sets system hostname using hostnamectl
   - Step 2: Configures kernel parameters via sysctl
   - Step 3: Downloads Chef Automate CLI from packages.chef.io
   - Step 4: Deploys only Chef Infra Server (without Automate)
   - Step 5: Creates Chef Server user with credentials
   - Step 6: Creates Chef Server organization with association
   - Ansible equivalent: ansible.builtin.shell, ansible.builtin.get_url, ansible.builtin.command modules

## Bash to Ansible Mapping

| Bash Operation | Ansible Module | Notes |
|---|---|---|
| hostnamectl set-hostname | ansible.builtin.hostname | Set system hostname |
| sysctl -w | ansible.posix.sysctl | Configure kernel parameters |
| curl \| gunzip | ansible.builtin.get_url + ansible.builtin.unarchive | Download and extract CLI |
| chmod +x | ansible.builtin.file | Set executable permissions |
| ./chef-automate deploy | ansible.builtin.command | Deploy Chef services |
| chef-server-ctl user-create | ansible.builtin.command | Create Chef user |
| chef-server-ctl org-create | ansible.builtin.command | Create Chef organization |

## Dependencies

**System Requirements**: Linux system with sudo access
**Network Access**: Internet connectivity to packages.chef.io
**Kernel Parameters**: vm.max_map_count=262144, vm.dirty_expire_centisecs=20000
**Chef Services**: chef-automate, chef-server-ctl

## Checks for the Migration

**Files to verify**: 
- /usr/local/bin/chef-automate (or installation path)
- ${username}.pem (user certificate)
- ${orgname}-validator.pem (organization validator certificate)

**System settings to check**:
- Hostname matches configured value
- Kernel parameters: vm.max_map_count and vm.dirty_expire_centisecs
- Chef Automate service status
- Chef Infra Server service status

**Services to check**:
- chef-automate service
- chef-server service components

## Pre-flight checks:
```bash
# Verify hostname
hostname

# Check kernel parameters
sysctl vm.max_map_count
sysctl vm.dirty_expire_centisecs

# Verify Chef Automate status
sudo chef-automate status

# Verify Chef Server status
sudo chef-server-ctl status

# Check user and org files exist
ls -la *.pem
```

**MIGRATION NOTE**: This analysis found Bash scripts rather than PowerShell scripts. The migration would involve converting shell commands to appropriate Ansible modules for Linux system configuration and Chef infrastructure deployment. No Windows-specific PowerShell cmdlets or DSC resources were found in the provided codebase.