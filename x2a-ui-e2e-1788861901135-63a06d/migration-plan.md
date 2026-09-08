# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains demonstration examples of Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is primarily educational/example code showing compliance automation patterns. The migration scope is minimal as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains example Ansible playbooks with Chef InSpec testing integration that require analysis for potential consolidation into pure Ansible solutions:

### MODULE INVENTORY

**chef-and-ansible**:
- Description: Apache HTTPS web server deployment with SSL certificate generation, virtual host configuration, and security hardening (POODLE vulnerability fix)
- Path: chef-and-ansible/
- Technology: Ansible (with Chef InSpec testing)
- Key Features: Self-signed SSL certificates via OpenSSL modules, Apache virtual host configuration, SSL protocol hardening, Test Kitchen integration with InSpec verification

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with InSpec verification
- `website_https.yml`: Main Ansible playbook for Apache HTTPS setup with SSL certificate generation
- `poodle_fix.yml`: Security hardening playbook to disable SSLv3 and enforce TLS 1.2
- `index.html`: Static HTML content for web server testing
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG controls)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with native Ansible testing solutions (ansible-test, molecule, or custom verification tasks)
- **Test Kitchen**: Migrate to Molecule for Ansible-native testing framework
- **Chef Automate/Server**: Remove deployment scripts as they are not needed in pure Ansible environment

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates generated via Ansible OpenSSL modules - this pattern can be retained
- SSH security hardening: InSpec SSH compliance tests should be converted to Ansible verification tasks
- STIG compliance: SSH root login controls (V-38607, RHEL-08-000227) need native Ansible compliance verification
- No hardcoded credentials detected in the reviewed files
- SSL certificate files are generated dynamically, no static certificate management required

### Technical Challenges
- **InSpec Test Migration**: Converting Ruby-based InSpec tests to Ansible native verification requires rewriting test logic in YAML/Jinja2
- **Test Kitchen Replacement**: Migrating from Test Kitchen to Molecule requires restructuring test scenarios and driver configurations  
- **Compliance Reporting**: InSpec provides structured compliance reporting that needs equivalent Ansible solution
- **STIG Control Mapping**: Maintaining traceability to security controls (CCI-000774, SRG-OS-000112) in pure Ansible implementation

### Migration Order
1. **Apache HTTPS Playbook** (low risk, already pure Ansible)
2. **Security Hardening Playbook** (moderate complexity, convert InSpec verification to Ansible tasks)
3. **Test Framework Migration** (high complexity, requires Molecule setup and test conversion)

### Assumptions
- The repository serves as example/demonstration code rather than production infrastructure
- Test Kitchen and InSpec are used for compliance verification rather than core functionality
- The Apache configuration is intended for development/testing environments (self-signed certificates)
- Chef Automate deployment scripts are reference implementations not requiring migration
- SSH security requirements follow RHEL 8 STIG guidelines
- The target environment will maintain the same Ubuntu 20.04 platform for consistency
- Compliance reporting requirements can be met with Ansible native solutions or third-party tools
- The migration timeline assumes this is example code that can be refactored rather than production systems requiring careful coordination