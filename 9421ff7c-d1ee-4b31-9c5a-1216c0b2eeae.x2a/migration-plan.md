# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and tools rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks demonstrating Chef InSpec integration, Chef server deployment scripts, and compliance testing examples. The migration scope is minimal as most content is already Ansible-based or consists of deployment utilities.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Ansible playbooks demonstrating Chef InSpec integration for compliance automation with HTTPS website deployment and SSL configuration
- Path: chef-and-ansible/
- Technology: Ansible (already migrated) with Chef InSpec testing
- Key Features: Apache HTTPS setup, SSL certificate generation, Test Kitchen integration, InSpec compliance verification

**setup-automate**:
- Description: Bash deployment scripts for Chef Automate and Chef Infra Server installation and initial configuration
- Path: setup-automate/
- Technology: Bash scripts
- Key Features: Chef Automate deployment, Chef server setup, user and organization creation, system tuning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `website_https.yml`: Ansible playbook for Apache HTTPS site deployment with SSL certificates
- `poodle_fix.yml`: Ansible playbook for SSL protocol hardening (disabling SSLv3, enabling TLSv1.2)
- `website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `ssh_profile.rb`: InSpec compliance profile for SSH security hardening verification
- `deploy-automate.sh`: Chef Automate and Infra Server deployment automation script
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml), with Chef server scripts targeting Linux distributions
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen)
- **Cloud Platform**: Not specified, designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Already integrated with Ansible playbooks for compliance testing - no migration needed
- **Test Kitchen**: Currently configured for Ansible playbook testing - maintain existing integration
- **Chef Automate/Server**: Deployment scripts are infrastructure utilities, not application code requiring migration
- **Apache 2.4.41**: Specific version pinned in Ansible playbook - verify availability in target environment

### Security Considerations

- **SSL/TLS Configuration**: Existing Ansible playbooks properly implement SSL certificate generation and TLS hardening
  - Self-signed certificate generation using OpenSSL modules
  - SSL protocol hardening (disabling SSLv3, enforcing TLSv1.2)
  - InSpec tests verify SSL configuration compliance
- **SSH Hardening**: InSpec profile includes SSH root login disable verification (STIG compliance)
- **Credential Management**: Chef server deployment scripts contain hardcoded credentials that should be externalized to Ansible Vault
- **File Permissions**: Proper file permissions implemented for certificates (0640) and web content (0644/0755)

### Technical Challenges

- **Minimal Migration Required**: Most content is already Ansible-based or consists of deployment utilities
- **InSpec Integration**: Existing Chef InSpec integration with Ansible is a best practice - maintain this approach
- **Credential Externalization**: Hardcoded credentials in deployment scripts need to be moved to secure variable management
- **Test Kitchen Compatibility**: Ensure Test Kitchen configuration remains functional with any infrastructure changes

### Migration Order

1. **chef-and-ansible** (already complete - Ansible playbooks with InSpec testing)
2. **Credential Security** (externalize hardcoded credentials from deployment scripts)
3. **setup-automate** (convert to Ansible playbooks if infrastructure-as-code approach desired)

### Assumptions

- The repository serves as an example/demo collection rather than production infrastructure code
- Chef InSpec integration with Ansible is intentional and should be preserved for compliance automation
- Test Kitchen integration is required for continued testing workflows
- Chef server deployment scripts may be used as-is for infrastructure setup rather than requiring conversion to Ansible
- Ubuntu 20.04 target environment will remain consistent or be updated to a compatible version
- Self-signed certificates are acceptable for demo/testing purposes
- The existing Ansible playbook structure and InSpec testing approach represents the desired end state
- Hardcoded credentials in deployment scripts are acceptable for demo purposes but should be flagged for production use