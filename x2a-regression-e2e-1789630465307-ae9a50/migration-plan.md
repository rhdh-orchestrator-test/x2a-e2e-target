# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and deployment scripts rather than production Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, Chef Automate deployment scripts, and test verification files. This represents a documentation/example repository rather than a traditional infrastructure-as-code migration scenario.

## Module Migration Plan

This repository contains example configurations and deployment utilities rather than traditional Chef cookbooks:

### MODULE INVENTORY

**No traditional Chef cookbooks or infrastructure modules were found in this repository.** Instead, the repository contains:

**EXAMPLE CONFIGURATIONS:**
- **website_https**:
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed certificates and SSL hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4.41 installation, SSL certificate generation, virtual host configuration, security hardening

- **poodle_fix**:
    - Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration remediation, POODLE vulnerability mitigation

**DEPLOYMENT UTILITIES:**
- **chef-automate-deployment**:
    - Description: Bash script for automated Chef Automate and Chef Infra Server deployment
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash scripting
    - Key Features: Hostname configuration, system tuning, user/organization creation

- **chef-server-deployment**:
    - Description: Bash script for standalone Chef Infra Server deployment without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash scripting
    - Key Features: Chef server installation, initial configuration, certificate management

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS configuration and SSL protocol verification
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG control)
- `index.html`: Static HTML test page for web server verification
- `README.md`: Documentation explaining Chef InSpec integration with Ansible

### Target Details

Based on the example configurations:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with RHEL compatibility indicated in InSpec profiles
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml for testing)
- **Cloud Platform**: Not specified - examples are platform-agnostic

## Migration Approach

### Key Dependencies to Address

**No external Chef dependencies found** - this repository contains examples rather than production cookbooks. However, for organizations using this as reference material:

- **Chef InSpec**: Already integrated with Ansible playbooks for compliance testing
- **Test Kitchen**: Used for testing Ansible playbooks with Vagrant driver
- **Apache 2.4.41**: Specific version pinned in playbook, may need updating for target environments

### Security Considerations

The repository demonstrates several security practices that should be maintained in production migrations:

- **SSL/TLS Configuration**: Examples show proper SSL certificate generation and protocol hardening
  - Self-signed certificate generation using OpenSSL modules
  - TLS 1.2 enforcement and SSLv3 disabling for POODLE mitigation
  - Certificate file permissions (0640) and directory structure

- **Compliance Testing**: InSpec profiles demonstrate STIG compliance verification
  - SSH root login restrictions (STIG control RHEL-08-000227)
  - SSL protocol compliance testing
  - Port and service verification

- **Credential Management**: Deployment scripts contain hardcoded credentials
  - Username/password combinations in plain text
  - Organization names and email addresses exposed
  - **CRITICAL**: Production deployments must use Ansible Vault or external secret management

### Technical Challenges

**Minimal technical challenges** as this is primarily an example repository:

- **Script to Playbook Conversion**: Bash deployment scripts could be converted to Ansible playbooks for consistency
  - Chef Automate installation automation
  - System parameter tuning (vm.max_map_count, vm.dirty_expire_centisecs)
  - User and organization provisioning

- **Testing Framework Integration**: Maintaining InSpec integration while migrating to pure Ansible
  - Test Kitchen configuration may need adjustment for different environments
  - InSpec profile compatibility across different OS distributions

### Migration Order

**Not applicable** - no traditional migration required. However, for organizations using these examples:

1. **Security Hardening** (immediate): Remove hardcoded credentials from deployment scripts
2. **Script Modernization** (low priority): Convert Bash scripts to Ansible playbooks for consistency
3. **Test Enhancement** (ongoing): Expand InSpec profiles for additional compliance requirements

### Assumptions

- This repository serves as documentation/examples rather than production infrastructure code
- Organizations referencing these examples will adapt them for their specific environments
- The Ansible playbooks are already in target format and demonstrate best practices
- InSpec integration patterns shown here will be replicated in production migrations
- Deployment scripts are intended for development/lab environments only
- Target environments will require updated package versions and security configurations
- Production deployments will implement proper secret management practices
- The examples assume Ubuntu/Debian package management but include RHEL-compatible InSpec profiles