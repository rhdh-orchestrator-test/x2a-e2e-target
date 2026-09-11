# MIGRATION FROM CHEF TO ANSIBLE

This repository is already primarily Ansible-based with Chef InSpec integration for compliance testing. The migration scope is minimal as the core infrastructure automation is implemented in Ansible playbooks, with Chef InSpec serving as a testing framework. The primary migration effort involves replacing Chef InSpec with native Ansible testing approaches and migrating Chef Server deployment scripts to Ansible automation.

## Module Migration Plan

This repository contains demonstration code showing Chef InSpec integration with Ansible rather than traditional Chef cookbooks:

### MODULE INVENTORY

**apache-https-website**:
- Description: Apache web server with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a Hello World website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: SSL certificate generation via OpenSSL modules, Apache virtual host configuration, security hardening with TLS 1.2

**ssl-security-hardening**:
- Description: SSL/TLS security configuration to disable vulnerable protocols (POODLE vulnerability fix)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol restriction, TLS 1.2 enforcement, security compliance

**chef-server-deployment**:
- Description: Chef Infra Server deployment automation for on-premises or cloud environments
- Path: setup-automate/deploy-chef-server.sh
- Technology: Bash shell script
- Key Features: Chef Server installation, user and organization creation, system configuration

**chef-automate-deployment**:
- Description: Chef Automate and Chef Infra Server combined deployment with full platform setup
- Path: setup-automate/deploy-automate.sh
- Technology: Bash shell script
- Key Features: Automate platform deployment, integrated server setup, user provisioning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL security
- `tests/ssh_profile.rb`: InSpec SSH security profile tests
- `index.html`: Static web content for demonstration purposes

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml), with Chef Server deployment targeting Linux distributions
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen for local testing)
- **Cloud Platform**: Cloud-agnostic deployment scripts support AWS, Azure, GCP, and on-premises environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible native testing using `ansible.builtin.uri`, `ansible.builtin.wait_for`, and `ansible.builtin.assert` modules
- **Test Kitchen**: Migrate to Molecule for Ansible playbook testing and validation
- **Chef Automate CLI**: Replace with Ansible automation for Chef platform deployment (if still needed)

### Security Considerations

- **SSL/TLS Configuration**: Current implementation uses secure TLS 1.2 enforcement and disables vulnerable protocols
  - Migration approach: Maintain existing security configurations in Ansible playbooks
- **Certificate Management**: Self-signed certificates generated via Ansible OpenSSL modules
  - Migration approach: Consider Let's Encrypt integration or enterprise CA integration
- **Hardcoded Credentials**: Chef Server deployment scripts contain plaintext passwords and configuration
  - Migration approach: Implement Ansible Vault for credential management
- **SSH Security**: InSpec tests verify SSH configuration compliance
  - Migration approach: Replace with Ansible security validation tasks

### Technical Challenges

- **InSpec Test Migration**: Converting Ruby-based InSpec tests to Ansible native validation
  - Mitigation: Use Ansible's `uri`, `wait_for`, and `assert` modules for equivalent functionality
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule testing framework
  - Mitigation: Molecule provides similar functionality with better Ansible integration
- **Chef Server Dependencies**: If Chef Server is still required for other systems
  - Mitigation: Maintain Chef Server deployment automation in Ansible format

### Migration Order

1. **InSpec Test Conversion** (low risk, high value) - Convert compliance tests to Ansible validation tasks
2. **Test Framework Migration** (moderate complexity) - Replace Test Kitchen with Molecule
3. **Chef Server Automation** (high complexity) - Convert deployment scripts to Ansible playbooks if needed

### Assumptions

- The primary goal is to eliminate Chef InSpec dependency while maintaining compliance validation capabilities
- Chef Server deployment automation may still be needed for hybrid environments
- Current SSL/TLS security configurations should be preserved
- Test coverage must be maintained during the migration from InSpec to native Ansible testing
- The demonstration nature of this repository suggests it may be used for training or proof-of-concept purposes
- Ubuntu 20.04 target platform may need updating to more recent LTS versions
- Vagrant-based testing environment is acceptable for continued use with Molecule