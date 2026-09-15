# MIGRATION FROM CHEF INSPEC + ANSIBLE TO ANSIBLE

This repository contains educational examples demonstrating Chef InSpec integration with Ansible playbooks rather than traditional Chef cookbooks requiring migration. The content is already primarily Ansible-based with InSpec used for compliance testing. Migration complexity is minimal as the core infrastructure automation is already implemented in Ansible.

## Module Migration Plan

This repository contains demonstration examples that showcase Chef InSpec testing alongside existing Ansible playbooks:

### MODULE INVENTORY

**website-https-demo**:
- Description: Apache web server with HTTPS/SSL configuration, self-signed certificate generation, and virtual host setup for a "Hello World" website
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache 2.4.41 installation, SSL certificate generation via OpenSSL, virtual host configuration, directory structure creation

**poodle-ssl-fix**:
- Description: SSL security hardening playbook that disables vulnerable SSL protocols and enforces TLS 1.2 to address POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (with InSpec testing)
- Key Features: Apache SSL protocol configuration, TLS 1.2 enforcement, service restart handling

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification on Ubuntu 20.04
- `tests/website_https_verify.rb`: InSpec compliance tests verifying HTTPS port 443 listening, SSL protocol configuration, and web content
- `tests/ssh_profile.rb`: InSpec security control testing SSH root login disabled (STIG compliance)
- `setup-automate/deploy-automate.sh`: Chef Automate and Infra Server deployment script for demonstration environment
- `setup-automate/deploy-chef-server.sh`: Standalone Chef Infra Server deployment script
- `index.html`: Static HTML test content for web server verification

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (as specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant (configured in Test Kitchen driver)
- **Cloud Platform**: Not specified - designed for on-premises or cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with native Ansible testing modules (ansible.builtin.uri, ansible.builtin.wait_for, ansible.builtin.assert)
- **Test Kitchen**: Replace with ansible-test or molecule for playbook testing and validation
- **Chef Automate/Server**: Remove deployment scripts as they are not needed for pure Ansible infrastructure

### Security Considerations

- **SSL/TLS Configuration**: Current playbooks already implement proper SSL hardening practices
  - Self-signed certificate generation is appropriate for demo purposes
  - TLS 1.2 enforcement addresses POODLE vulnerability
  - No hardcoded credentials detected in playbook variables
- **SSH Security**: InSpec tests verify SSH root login disabled (STIG compliance requirement)
- **Certificate Management**: OpenSSL certificate generation handled via Ansible crypto modules

### Technical Challenges

- **Testing Framework Migration**: Replace InSpec compliance tests with Ansible native testing
  - Convert InSpec `describe port(443)` to `ansible.builtin.wait_for` tasks
  - Replace InSpec HTTP checks with `ansible.builtin.uri` module verification
  - Transform SSL protocol tests to Ansible fact gathering and assertions
- **Test Kitchen Replacement**: Migrate from Test Kitchen to Molecule for Ansible playbook testing
- **Compliance Verification**: Maintain STIG compliance checking without InSpec dependency

### Migration Order

1. **website-https-demo** (low risk, already Ansible-native)
2. **poodle-ssl-fix** (minimal changes needed)
3. **Testing Framework** (replace InSpec with Ansible testing modules)

### Assumptions

- The primary goal is to eliminate Chef InSpec dependency while maintaining compliance testing capabilities
- Current Ansible playbooks are production-ready and follow best practices
- Ubuntu 20.04 target platform will remain consistent post-migration
- Self-signed certificates are acceptable for demonstration purposes
- Test Kitchen can be replaced with Molecule or ansible-test for CI/CD integration
- Chef Automate/Server deployment scripts will be removed as they serve no purpose in pure Ansible environment
- STIG compliance requirements must be maintained through native Ansible testing methods