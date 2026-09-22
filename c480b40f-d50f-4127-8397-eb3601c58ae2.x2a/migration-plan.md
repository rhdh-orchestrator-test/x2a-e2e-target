# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains Chef InSpec compliance tests and Ansible playbooks demonstrating hybrid automation approaches. The migration involves consolidating InSpec testing capabilities into native Ansible testing frameworks while preserving compliance validation functionality. The scope is limited with low complexity, estimated timeline of 1-2 weeks for a small team.

## Module Migration Plan

This repository contains demonstration content that combines Chef InSpec with Ansible rather than traditional Chef cookbooks:

### MODULE INVENTORY

**website-https-compliance**:
- Description: Apache HTTPS web server deployment with SSL/TLS configuration, self-signed certificate generation, and compliance validation
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, HTTPS compliance testing

**poodle-vulnerability-fix**:
- Description: SSL/TLS security hardening to disable vulnerable protocols and enforce TLS 1.2+ only
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, POODLE vulnerability mitigation, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `tests/website_https_verify.rb`: InSpec compliance tests validating HTTPS functionality, port 443 availability, and SSL protocol security
- `tests/ssh_profile.rb`: InSpec security profile testing SSH root login restrictions (STIG compliance control)
- `setup-automate/deploy-chef-server.sh`: Chef Infra Server deployment script for on-premises or cloud VMs
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script with user and organization setup
- `index.html`: Static test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (supports on-premises and cloud deployment via setup scripts)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible's built-in testing modules (uri, assert, service_facts) and external tools like Testinfra or Molecule
- **Test Kitchen**: Migrate to Ansible Molecule for testing framework with similar multi-platform support
- **Chef Automate/Server**: Replace with Ansible AWX/Tower for centralized automation management and compliance reporting

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates via OpenSSL Ansible modules - production migration should integrate with proper CA or certificate management solutions
- SSH hardening compliance: InSpec SSH profile validates STIG controls - migrate to Ansible security roles like ansible-hardening or custom compliance playbooks
- Credential management: Setup scripts contain hardcoded passwords - implement Ansible Vault for secrets management in production migration
- Apache security configuration: POODLE fix demonstrates security patching - establish Ansible-based security baseline management

### Technical Challenges
- InSpec test translation: Convert Ruby-based InSpec controls to Ansible native testing or integrate with pytest/testinfra for similar functionality
- Compliance reporting: Chef Automate provides compliance dashboards - evaluate Ansible AWX reporting or integrate with external compliance tools
- Multi-platform testing: Test Kitchen supports multiple OS platforms - ensure Molecule configuration maintains equivalent test coverage
- STIG compliance validation: SSH profile implements specific STIG controls - verify Ansible security roles provide equivalent compliance coverage

### Migration Order
1. InSpec test conversion (low risk, establishes testing foundation)
2. Test Kitchen to Molecule migration (moderate complexity, testing infrastructure)
3. Chef Automate replacement evaluation (high complexity, requires architectural decisions)

### Assumptions
- Repository serves as demonstration/training content rather than production infrastructure code
- Existing Ansible playbooks are already functional and require minimal modification
- InSpec compliance tests need conversion to Ansible-native testing approaches
- Chef server deployment scripts are used for lab/demo environments only
- Production migration would require proper certificate management and secrets handling
- Target environments support Ansible's OpenSSL modules and required Python dependencies
- Compliance requirements can be met through Ansible security roles or custom validation playbooks