# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository is a demonstration project showing Chef InSpec integration with Ansible for compliance automation. The migration scope is minimal as the primary automation is already implemented in Ansible. The main task is to replace Chef InSpec testing with native Ansible testing capabilities and remove Chef infrastructure dependencies.

## Module Migration Plan

This repository contains demonstration content that combines Ansible playbooks with Chef InSpec testing:

### MODULE INVENTORY

**website-https-deployment**:
- Description: Apache web server deployment with SSL/HTTPS configuration, self-signed certificate generation, and virtual host setup
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL module activation

**poodle-vulnerability-fix**:
- Description: SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible
- Key Features: Apache SSL configuration replacement, protocol restriction, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Vagrant-based testing with Ansible provisioner and InSpec verifier
- `tests/website_https_verify.rb`: InSpec compliance tests for HTTPS functionality, SSL protocol validation, and web service verification
- `tests/ssh_profile.rb`: InSpec security compliance test for SSH root login restrictions (STIG control)
- `setup-automate/deploy-automate.sh`: Chef Automate and Chef Infra Server deployment script for on-premises/cloud VMs
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static test content for web server validation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified (scripts support both on-premises and cloud deployment)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing modules (uri, assert, service_facts) or molecule testing framework
- **Test Kitchen**: Replace with molecule for Ansible-native testing and validation
- **Chef Automate/Server**: Remove dependency on Chef infrastructure components entirely

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks implement proper SSL hardening (TLS 1.2 enforcement, SSLv3 disabling)
- **Certificate Management**: Self-signed certificates are generated via OpenSSL modules - consider integration with Let's Encrypt or enterprise CA
- **SSH Hardening**: InSpec test validates SSH root login restrictions - migrate to Ansible assert tasks
- **Compliance Testing**: STIG controls (RHEL-08-000227) currently validated via InSpec need native Ansible verification
- **Credential Management**: Hardcoded passwords in deployment scripts require vault integration

### Technical Challenges

- **InSpec Test Migration**: Convert Ruby-based InSpec tests to Ansible assert tasks or molecule verifiers
- **Compliance Framework**: Maintain STIG compliance validation without Chef InSpec dependency
- **Test Kitchen Replacement**: Migrate testing workflow from kitchen to molecule for Ansible-native development
- **Infrastructure Deployment**: Replace Chef server deployment scripts with Ansible-based infrastructure provisioning

### Migration Order

1. **Website HTTPS Module** (low risk, already Ansible-native)
2. **POODLE Fix Module** (low complexity, simple configuration change)
3. **Test Migration** (moderate complexity, requires InSpec to Ansible test conversion)
4. **Infrastructure Scripts** (lowest priority, deployment tooling replacement)

### Assumptions

- The primary goal is to eliminate Chef dependencies while maintaining compliance automation capabilities
- Ubuntu 20.04 target environment will be maintained (Apache 2.4.41 package version suggests this)
- SSL certificate generation approach (self-signed) is acceptable for demonstration purposes
- STIG compliance requirements must be preserved in the migrated solution
- Test Kitchen workflow can be replaced with molecule without significant process disruption
- Chef Automate/Server infrastructure is being decommissioned as part of this migration
- The demonstration nature of this repository means production-grade secret management is not currently implemented