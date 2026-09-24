# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible for compliance automation. **No actual migration is required** as the infrastructure automation is already implemented in Ansible. This is a demonstration/example repository showing how to use Chef InSpec as a testing framework alongside existing Ansible playbooks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec test profiles that demonstrate compliance automation patterns:

### MODULE INVENTORY

**No Chef cookbooks or infrastructure modules found for migration.** The repository contains:

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS/SSL support, including self-signed certificate generation and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, security hardening

- **poodle_fix**:
    - Description: Ansible playbook that applies SSL security fixes to Apache, specifically disabling SSLv3 and enforcing TLS 1.2 to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: SSL protocol configuration, Apache security hardening, TLS 1.2 enforcement

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality and SSL configuration
- `tests/ssh_profile.rb`: InSpec security profile testing SSH root login restrictions (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test file for web server verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured as Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

**No migration dependencies** - this repository demonstrates integration patterns rather than requiring migration:

- **Chef InSpec**: Already integrated as verification framework alongside Ansible
- **Test Kitchen**: Configured to orchestrate Ansible playbook execution and InSpec testing
- **Apache 2.4.41**: Specific version pinned in Ansible playbook (ubuntu package: apache2=2.4.41-4ubuntu3.10)

### Security Considerations

The repository demonstrates security best practices that are already implemented in Ansible:

- **SSL/TLS Configuration**: Self-signed certificate generation using Ansible's openssl modules
- **POODLE Vulnerability Mitigation**: Dedicated playbook for disabling SSLv3 and enforcing TLS 1.2
- **SSH Hardening**: InSpec profile validates SSH root login restrictions per STIG requirements
- **File Permissions**: Proper file modes set for certificates (0640) and web content (0644/0755)
- **Service Management**: Proper handler configuration for Apache and SSH service restarts

### Technical Challenges

**No migration challenges** - this is an example repository demonstrating integration patterns:

- **Integration Pattern**: Shows how to use Chef InSpec for compliance testing with Ansible automation
- **Test Kitchen Integration**: Demonstrates Test Kitchen configuration for Ansible + InSpec workflows
- **Compliance Automation**: Provides working examples of security compliance verification

### Migration Order

**No migration required** - repository structure recommendation for teams adopting this pattern:

1. **Ansible Playbooks**: Already implemented and functional
2. **InSpec Test Profiles**: Already implemented for compliance verification
3. **Test Kitchen Configuration**: Already configured for integrated testing workflow

### Assumptions

- **Purpose Clarification**: This repository serves as example/demonstration code for Chef InSpec + Ansible integration patterns, not production infrastructure requiring migration
- **Testing Framework**: Chef InSpec is being used as a compliance testing tool, not as infrastructure automation that needs migration
- **Development Environment**: The setup scripts in `setup-automate/` are for creating Chef development/testing environments, not production infrastructure
- **Example Nature**: The Apache configurations and HTML content are simplified examples for demonstration purposes
- **Integration Focus**: The primary value is demonstrating how to integrate Chef InSpec compliance testing with Ansible automation workflows
- **No Production Dependencies**: No production systems depend on this code - it's educational/example material

## Recommendation

**No migration action required.** This repository already demonstrates the target state: Ansible for infrastructure automation with Chef InSpec for compliance verification. Teams can use this as a reference implementation for integrating compliance testing into their Ansible workflows.