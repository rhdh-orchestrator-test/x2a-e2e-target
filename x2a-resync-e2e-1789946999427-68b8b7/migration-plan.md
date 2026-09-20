# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec used for compliance testing. Migration complexity is minimal as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains demonstration examples rather than production Chef cookbooks:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
No traditional Chef cookbooks found. Repository contains Ansible playbooks with InSpec compliance tests.

**ANSIBLE PLAYBOOKS (ALREADY MIGRATED):**
- **website-https**:
    - Description: Apache web server with SSL/TLS configuration, self-signed certificate generation, and virtual host setup
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

- **poodle-fix**:
    - Description: SSL security hardening to disable SSLv3 and enforce TLS 1.2 only (POODLE vulnerability mitigation)
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handlers

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality and SSL configuration
- `tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG control)
- `index.html`: Static HTML test content for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script

### Target Details

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in kitchen.yml driver)
- **Cloud Platform**: Not specified (local development/testing environment)

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with native Ansible testing solutions (ansible-test, molecule, or pytest-ansible)
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation
- **Chef Automate/Server**: Remove dependency on Chef infrastructure components

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates - consider integration with Let's Encrypt or enterprise CA
- SSH hardening: InSpec test validates SSH root login restrictions - ensure equivalent Ansible security hardening
- POODLE vulnerability mitigation: Already implemented in poodle_fix.yml playbook
- Credential management: Deployment scripts contain hardcoded credentials that should be moved to Ansible Vault

### Technical Challenges
- **InSpec Test Migration**: Convert InSpec compliance tests to native Ansible testing framework
  - Port website_https_verify.rb tests to Ansible uri module and assert tasks
  - Convert SSH security tests to Ansible lineinfile verification tasks
  - Maintain STIG compliance validation capabilities
- **Test Kitchen Replacement**: Migrate from Test Kitchen to Molecule for playbook testing
- **Chef Infrastructure Removal**: Eliminate dependency on Chef Automate/Server deployment scripts

### Migration Order
1. **InSpec Test Conversion** (low risk, high value) - Convert compliance tests to native Ansible
2. **Test Framework Migration** (moderate complexity) - Replace Test Kitchen with Molecule
3. **Infrastructure Cleanup** (low complexity) - Remove Chef deployment scripts and documentation

### Assumptions
- Repository is used for demonstration/training purposes rather than production deployment
- Current Ansible playbooks are functional and tested
- InSpec compliance requirements must be maintained in the migrated solution
- Test Kitchen functionality needs to be preserved through Molecule or equivalent testing framework
- Chef Automate/Server deployment scripts are not critical to core functionality
- SSL certificate generation approach (self-signed) is acceptable for the target environment
- Ubuntu 20.04 remains the target platform (though Apache version may need updating for newer OS versions)