# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains educational examples demonstrating Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec used for compliance testing. Migration complexity is minimal as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains demonstration content that combines Ansible playbooks with Chef InSpec compliance testing:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with SSL/TLS configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to disable SSLv3 and enforce TLS 1.2 only (POODLE vulnerability mitigation)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification on Ubuntu 20.04
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS functionality, SSL protocols, and web service availability
- `tests/ssh_profile.rb`: InSpec security control testing SSH root login restrictions (STIG compliance)
- `index.html`: Static HTML test content for web server verification
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with native Ansible testing modules (ansible.builtin.uri, ansible.builtin.service_facts) or external testing frameworks like Molecule with Testinfra
- **Test Kitchen**: Replace with Ansible Molecule for testing and validation workflows
- **Chef Automate/Server**: Remove dependency on Chef infrastructure components for compliance reporting

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks implement proper SSL hardening practices that should be maintained
  - Self-signed certificate generation using OpenSSL modules
  - TLS 1.2 enforcement and SSLv3 disabling
  - Proper file permissions on certificate files (0640)
- **SSH Hardening**: InSpec tests verify SSH root login restrictions - implement equivalent Ansible tasks for SSH configuration
- **Vault/Secrets Management**: No encrypted data bags or vault usage detected; credentials are hardcoded in deployment scripts
  - Hardcoded passwords in setup scripts need to be externalized to Ansible Vault
  - SSL certificate management could benefit from Let's Encrypt integration

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec compliance tests to native Ansible testing approaches
  - InSpec provides rich compliance testing DSL that may require multiple Ansible modules to replicate
  - STIG compliance verification currently handled by InSpec needs equivalent Ansible implementation
- **Compliance Reporting**: Loss of Chef Automate's compliance dashboard and reporting capabilities
  - Need alternative solution for compliance visualization and reporting
  - Consider integration with external compliance tools or custom reporting

### Migration Order

1. **Ansible Playbook Validation** (immediate - already complete)
2. **Testing Framework Replacement** (low complexity - replace InSpec with Molecule/Testinfra)
3. **Compliance Reporting Solution** (moderate complexity - implement alternative to Chef Automate)

### Assumptions

- The primary goal is educational content migration rather than production infrastructure migration
- Current Ansible playbooks are already following best practices and don't require significant refactoring
- InSpec compliance tests represent the desired security posture that must be maintained in pure Ansible
- Test Kitchen workflow should be replaced with Ansible Molecule for consistency
- Chef Automate deployment scripts are for demonstration purposes only and not production dependencies
- The target audience requires compliance automation examples without Chef dependencies
- Ubuntu 20.04 remains the target platform (though playbooks should work on other Debian-based systems)
- Self-signed certificates are acceptable for demonstration purposes (production would use proper CA or Let's Encrypt)