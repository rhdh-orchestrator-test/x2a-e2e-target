# MIGRATION FROM CHEF INSPEC INTEGRATION TO ANSIBLE

This repository contains example code demonstrating Chef InSpec integration with Ansible playbooks, rather than traditional Chef cookbooks requiring migration. The primary content consists of Ansible playbooks with InSpec test verification, deployment scripts for Chef infrastructure, and documentation examples. This represents a **minimal migration effort** focused on consolidating testing frameworks rather than converting infrastructure code.

## Module Migration Plan

This repository contains demonstration and setup code that requires assessment for integration into a pure Ansible workflow:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
All paths verified from the provided repository tree structure.

- **website-https-demo**:
    - Description: Ansible playbook demonstrating Apache HTTPS configuration with SSL certificate generation, virtual host setup, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible (already migrated)
    - Key Features: Self-signed SSL certificates via openssl modules, Apache virtual host configuration, SSL/TLS security settings

- **poodle-ssl-fix**:
    - Description: Ansible playbook for SSL protocol hardening to disable SSLv3 and enforce TLS 1.2 (POODLE vulnerability mitigation)
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible (already migrated)
    - Key Features: Apache SSL configuration updates, protocol restriction enforcement

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Static HTML test content for web server validation
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for hybrid environments
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec compliance tests for HTTPS configuration validation
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec security profile for SSH root login compliance (STIG controls)

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for on-premises or cloud-agnostic deployment

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with native Ansible testing modules (ansible.builtin.uri, ansible.builtin.assert) or integrate with Molecule for testing
- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation
- **Chef Automate/Server**: Evaluate need for Chef infrastructure in pure Ansible environment - may be eliminated entirely

### Security Considerations
- **SSL/TLS Configuration**: Existing playbooks already implement proper SSL certificate management and protocol hardening
- **SSH Hardening**: InSpec tests verify SSH root login restrictions - convert to Ansible tasks with verification
- **Compliance Testing**: STIG controls currently verified via InSpec - migrate to Ansible compliance modules or maintain InSpec for audit requirements
- **Credential Management**: No hardcoded credentials detected in playbooks - uses Ansible variable substitution appropriately

### Technical Challenges
- **Testing Framework Migration**: Converting InSpec tests to native Ansible testing requires rewriting test logic and assertions
- **Compliance Validation**: STIG control verification may require maintaining InSpec or implementing equivalent Ansible-native compliance checks
- **Chef Infrastructure Dependencies**: Deployment scripts assume Chef Automate/Server presence - determine if these components are still needed

### Migration Order
1. **Testing Framework Consolidation** (low risk, high value) - Convert InSpec tests to Ansible native testing or Molecule
2. **Chef Infrastructure Assessment** (moderate complexity) - Evaluate continued need for Chef Automate/Server components
3. **Documentation Updates** (low complexity) - Update examples to reflect pure Ansible workflow

### Assumptions
- The Chef infrastructure deployment scripts may be retained if Chef Automate is still used for compliance reporting in the target environment
- InSpec may be maintained alongside Ansible if regulatory compliance requires specific testing frameworks
- The existing Ansible playbooks are already production-ready and require minimal modification
- Test Kitchen configuration suggests this is a development/testing environment rather than production infrastructure
- The repository serves as documentation/examples rather than active infrastructure code
- Ubuntu 20.04 target platform may need updating to more recent LTS versions (22.04 or 24.04)
- Self-signed certificates in examples should be replaced with proper CA-signed certificates in production environments