# MIGRATION FROM CHEF EXAMPLES TO ANSIBLE

This repository contains Chef-related examples and tools rather than traditional Chef cookbooks. The primary content consists of Ansible playbooks with Chef InSpec testing integration, and Chef server deployment scripts. The migration scope is limited as most content is already in Ansible format or consists of deployment utilities that may not require migration.

## Module Migration Plan

This repository contains mixed technologies that need individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating Apache HTTPS configuration with self-signed SSL certificates, virtual host setup, and SSL protocol hardening
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, virtual host configuration, SSL/TLS security hardening

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 (POODLE vulnerability mitigation)
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL configuration updates, protocol restriction, service restart handling

**chef-inspec-tests**:
- Description: Chef InSpec compliance tests for HTTPS functionality and SSH security configuration validation
- Path: chef-and-ansible/tests/
- Technology: Chef InSpec
- Key Features: Port 443 listening verification, HTTPS response validation, SSL protocol compliance, SSH root login security checks

**chef-server-deployment**:
- Description: Bash scripts for automated Chef Infra Server and Chef Automate deployment on cloud or on-premises VMs
- Path: setup-automate/
- Technology: Bash/Shell scripts
- Key Features: Chef server installation, user and organization creation, system configuration tuning

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with Vagrant driver and InSpec verification
- `index.html`: Static web content for demonstration purposes
- `README.md`: Documentation explaining Chef InSpec integration with Ansible for compliance automation

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (configured in Test Kitchen)
- **Cloud Platform**: Not specified - designed for generic cloud or on-premises deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible compliance testing using ansible-lint, molecule, or native Ansible testing modules
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and verification
- **Chef Automate/Server**: Evaluate need for Chef infrastructure - may be eliminated if only used for InSpec testing

### Security Considerations

- **SSL/TLS Configuration**: Existing Ansible playbooks already implement proper SSL hardening practices
  - Self-signed certificate generation using OpenSSL modules
  - SSL protocol restrictions (TLS 1.2 enforcement, SSLv3 disabled)
  - Proper file permissions on certificate files (0640)
- **SSH Security**: InSpec tests validate SSH root login restrictions - migrate to Ansible security role
- **Credential Management**: 
  - Hardcoded passwords in Chef server deployment scripts (userpassword='password')
  - Certificate and key file paths are properly secured
  - No Chef Vault or encrypted data bags detected

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-native testing requires:
  - Rewriting Ruby-based InSpec controls as Ansible tasks or using ansible-lint rules
  - Replacing Test Kitchen workflow with Molecule for playbook testing
  - Maintaining compliance validation capabilities without InSpec dependency
- **Chef Infrastructure Dependency**: Determine if Chef server/Automate infrastructure is still needed:
  - If only used for InSpec testing, can be eliminated
  - If used for other Chef cookbooks not in this repository, coordinate migration timing

### Migration Order

1. **Ansible Playbooks** (already complete - no migration needed)
2. **Testing Framework** (moderate complexity - InSpec to Ansible testing)
3. **Chef Infrastructure Scripts** (low priority - evaluate necessity)

### Assumptions

- The Ansible playbooks (website_https.yml, poodle_fix.yml) are already production-ready and do not require migration
- Chef InSpec tests are used solely for compliance validation and not integrated with a larger Chef infrastructure
- The Chef server deployment scripts may be obsolete if the organization is migrating away from Chef entirely
- Test Kitchen configuration suggests this is a development/testing environment rather than production infrastructure
- The repository serves as an example/demonstration rather than production infrastructure code
- Ubuntu 20.04 target platform may need updating to more recent LTS versions (22.04 or 24.04)
- Hardcoded credentials in deployment scripts indicate this is for demonstration purposes only